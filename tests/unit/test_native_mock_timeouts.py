"""Local Rust mock servers need enough time for loaded CI workers."""

import re
import ast
from pathlib import Path

import pytest

from scripts.fund_literal_audit import production_source
from tests.unit.rust_dispatch import functions

ROOT = Path(__file__).parents[2]
DURATION = re.compile(r"Duration::from_(secs|millis)\(\s*(\d[\d_]*)\s*\)")


def short_mock_timeouts(source, test_file=False, helpers=""):
    if not test_file:
        production = production_source(source)
        source = ''.join(c if p == ' ' else ' ' for c, p in zip(source, production))
    own_bodies = dict(functions(source))
    bodies = {**dict(functions(helpers)), **own_bodies}
    local = {name for name, body in bodies.items() if re.search(r'127\.0\.0\.1|localhost|TcpListener|with_\w*base_url|with_endpoint|server\w*\s*\(', body)}
    while True:
        expanded = local | {name for name, body in bodies.items() if any(re.search(r'\b' + re.escape(callee) + r'\s*\(', body) for callee in local)}
        if expanded == local:
            break
        local = expanded
    errors = []
    for name in sorted(local & own_bodies.keys()):
        body = bodies[name]
        for match in DURATION.finditer(body):
            before = body[max(0, match.start() - 90):match.start()]
            # Sleeping or heartbeat cadence is not a network/request deadline.
            if re.search(r'(?:sleep|interval|heartbeat_interval|ping_interval)\s*\(\s*$', before):
                continue
            seconds = int(match[2].replace('_', '')) / (1000 if match[1] == 'millis' else 1)
            if seconds < 10:
                errors.append((name, match[0]))
    return errors


def test_local_native_mock_timeouts_are_at_least_ten_seconds():
    errors = {}
    for path in (ROOT / 'crates').rglob('*.rs'):
        source = path.read_text(encoding='utf8')
        helper = path.with_name('helpers.rs')
        helpers = helper.read_text(encoding='utf8') if helper.exists() and helper != path else ''
        found = short_mock_timeouts(source, 'tests' in path.parts or path.name == 'tests.rs', helpers)
        if found:
            errors[str(path.relative_to(ROOT))] = found
    assert not errors, errors


@pytest.mark.parametrize('duration', ['Duration::from_secs(2)', 'Duration::from_millis(9000)'])
@pytest.mark.parametrize('inline', [False, True])
def test_short_mock_deadlines_are_detected(duration, inline):
    source = f'fn server() {{ TcpListener::bind("127.0.0.1:0"); }} fn wire() {{ server(); Client::new({duration}); }}'
    if inline:
        source = '#[cfg(test)] mod tests { ' + source + ' }'
    assert short_mock_timeouts(source, not inline) == [('wire', duration)]


def test_sleep_and_production_timeouts_are_not_mock_deadlines():
    assert not short_mock_timeouts('fn production() { server(); Client::new(Duration::from_secs(1)); }')
    assert not short_mock_timeouts('fn wire() { TcpListener::bind("127.0.0.1:0"); sleep(Duration::from_secs(1)); Client::new(Duration::from_secs(10)); }', True)


@pytest.mark.parametrize('body,helpers', [
    ('recording_server_after_time_sync(); Client::new(Duration::from_secs(2));', ''),
    ('Client::new(Duration::from_secs(2)).with_coin_futures_base_url(url);', ''),
    ('recording_peer(); Client::new(Duration::from_secs(2));', 'fn recording_peer() { TcpListener::bind("127.0.0.1:0"); }'),
])
def test_indirect_native_mock_timeout_mutations(body, helpers):
    assert short_mock_timeouts('fn wire() { ' + body + ' }', True, helpers) == [('wire', 'Duration::from_secs(2)')]


def python_mock_timeouts(source):
    tree = ast.parse(source)
    functions = {n.name: n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    texts = {name: ast.get_source_segment(source, node) for name, node in functions.items()}
    local = {name for name, text in texts.items() if re.search(r'127\.0\.0\.1|localhost|(?:server|peer)\w*\s*\(', text)
             or any(a.arg.endswith('server') for a in functions[name].args.posonlyargs + functions[name].args.args + functions[name].args.kwonlyargs)
             or any(isinstance(node, ast.keyword) and node.arg and (node.arg in {'base_url', 'endpoint'} or node.arg.endswith('_base_url')) and not isinstance(node.value, ast.Constant) for node in ast.walk(functions[name]))}
    callees = {name: {n.func.id for n in ast.walk(function) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)} & functions.keys()
               for name, function in functions.items()}
    while True:
        expanded = local | {name for name, calls in callees.items() if calls & local}
        expanded |= {callee for name in local for callee in callees[name]}
        if expanded == local:
            break
        local = expanded
    errors = []
    for name in local:
        for node in ast.walk(functions[name]):
            if not isinstance(node, ast.Call):
                continue
            values = [k.value for k in node.keywords if k.arg == 'timeout']
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'wait_for' and len(node.args) >= 2:
                values.append(node.args[1])
            for value in values:
                if isinstance(value, ast.Constant) and isinstance(value.value, (int, float)) and 0 < value.value < 10:
                    errors.append((value.lineno, value.col_offset, value.end_col_offset, name, value.value))
    return sorted(set(errors))


def test_python_local_mock_timeouts_are_at_least_ten_seconds():
    errors = {}
    for path in (ROOT / 'tests').rglob('test_*.py'):
        found = python_mock_timeouts(path.read_text(encoding='utf8'))
        if found:
            errors[str(path.relative_to(ROOT))] = found
    assert not errors, errors


@pytest.mark.parametrize('call', ['Client(base_url=url, timeout=2)', 'received.get(timeout=2)', 'await asyncio.wait_for(client.recv(), 3)'])
def test_python_mock_timeout_mutations(call):
    source = 'async def wire():\n    url = "http://127.0.0.1:1234"\n    ' + call + '\n'
    assert python_mock_timeouts(source)
    assert not python_mock_timeouts(source.replace('timeout=2', 'timeout=10').replace('recv(), 3', 'recv(), 10'))


def test_python_timeout_controls_outside_local_io_remain_valid():
    assert not python_mock_timeouts('def clock():\n    timer.wait(timeout=1)\n')


@pytest.mark.parametrize('source', [
    'def test_wire(recording_server):\n    received.get(timeout=5)\n',
    'def test_wire(server):\n    helper()\ndef helper():\n    Client(timeout=2)\n',
    'def test_wire(http_server):\n    middle()\ndef middle():\n    helper()\ndef helper():\n    Client(timeout=2)\n',
    'def helper():\n    Client(coin_futures_base_url=url, timeout=2)\n',
    'def test_wire(*, ws_server):\n    received.get(timeout=5)\n',
])
def test_fixture_and_callee_mock_deadline_mutations(source):
    assert python_mock_timeouts(source)
    assert not python_mock_timeouts(source.replace('timeout=5', 'timeout=10').replace('timeout=2', 'timeout=10'))
