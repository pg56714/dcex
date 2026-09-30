"""Local Rust mock servers need enough time for loaded CI workers."""

import re
from pathlib import Path

import pytest

from scripts.fund_literal_audit import production_source
from tests.unit.rust_dispatch import functions

ROOT = Path(__file__).parents[2]
DURATION = re.compile(r"Duration::from_(secs|millis)\(\s*(\d[\d_]*)\s*\)")


def short_mock_timeouts(source, test_file=False):
    if not test_file:
        production = production_source(source)
        source = ''.join(c if p == ' ' else ' ' for c, p in zip(source, production))
    bodies = dict(functions(source))
    local = {name for name, body in bodies.items() if re.search(r'127\.0\.0\.1|localhost|TcpListener|with_base_url|with_endpoint|\bserver\s*\(', body)}
    while True:
        expanded = local | {name for name, body in bodies.items() if any(re.search(r'\b' + re.escape(callee) + r'\s*\(', body) for callee in local)}
        if expanded == local:
            break
        local = expanded
    errors = []
    for name in sorted(local):
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
        found = short_mock_timeouts(source, 'tests' in path.parts or path.name == 'tests.rs')
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
