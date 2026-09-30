"""Keep regression names tied to behavior across every test surface."""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]


def invalid_test_name(name):
    # Preserve normal mathematical and exchange-native terminology.
    name = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', name).lower()
    if name in {'test_kucoin_review_status', 'test_pending_review', 'round_down_to_step', 'round_up_to_step'}:
        return False
    for native_term in ('round_trip', 'round_tp_percent', 'preview'):
        name = re.sub(r'(?<![^_])' + native_term + r'(?=_|$)', '', name)
    return 'review' in name or bool(re.search(r'(?:^|_)round(?:_|\d)', name))


def invalid_rust_modules(source):
    from tests.unit.rust_dispatch import mask
    return [name for name in re.findall(r'\b(?:mod|fn)\s+(\w+)', mask(source)) if invalid_test_name(name)]


def naming_violations(root):
    errors = []
    for path in (root / 'tests').rglob('*.py'):
        if path.name.startswith('test_') and invalid_test_name(path.stem):
            errors.append((path, path.stem))
        tree = ast.parse(path.read_text(encoding='utf8'))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_') and invalid_test_name(node.name):
                errors.append((path, node.name))
            if isinstance(node, ast.ClassDef) and node.name.startswith('Test') and invalid_test_name(node.name):
                errors.append((path, node.name))
    for path in (root / 'crates').rglob('*.rs'):
        if 'tests' in path.relative_to(root / 'crates').parts and invalid_test_name(path.stem):
            errors.append((path, path.stem))
        errors.extend((path, name) for name in invalid_rust_modules(path.read_text(encoding='utf8')))
    return errors


def assert_behavior_names(root):
    assert not (errors := naming_violations(root)), errors


def test_regression_names_describe_behavior():
    assert_behavior_names(ROOT)


@pytest.mark.parametrize('surface', ['unit', 'sync_support', 'async_support'])
@pytest.mark.parametrize('filename,source', [
    ('test_round_new.py', 'def test_orders(): pass'),
    ('test_review_orders.py', 'def test_orders(): pass'),
    ('test_generated_review_aliases.py', 'def test_orders(): pass'),
    ('test_orders.py', 'def test_round_ten_orders(): pass'),
    ('test_orders.py', 'async def test_orders_review_validation(): pass'),
    ('test_orders.py', 'def test_ordersreviewvalidation(): pass'),
    ('test_round_trip_review_orders.py', 'def test_orders(): pass'),
    ('test_preview_review_orders.py', 'def test_orders(): pass'),
])
def test_process_names_fail_repository_guard_by_mutation(tmp_path, surface, filename, source):
    folder = tmp_path / 'tests' / surface
    folder.mkdir(parents=True)
    assert_behavior_names(tmp_path)
    (folder / filename).write_text(source, encoding='utf8')
    with pytest.raises(AssertionError):
        assert_behavior_names(tmp_path)


@pytest.mark.parametrize('module', ['review_cache_tests', 'round_ten_tests'])
def test_rust_process_modules_fail_repository_guard_by_mutation(tmp_path, module):
    folder = tmp_path / 'crates'
    folder.mkdir()
    assert_behavior_names(tmp_path)
    (folder / 'lib.rs').write_text(f'mod {module} {{}}', encoding='utf8')
    with pytest.raises(AssertionError):
        assert_behavior_names(tmp_path)
    assert not invalid_rust_modules(f'// mod {module} {{}}\nmod schema_cache_tests {{}}')


@pytest.mark.parametrize('name', ['test_round_trip', 'test_round_trip_orders', 'test_wallet_transfer_round_trip', 'test_preview_order', 'test_round_tp_percent', 'test_kucoin_review_status', 'test_pending_review'])
def test_native_terms_and_transaction_cycles_are_valid(name):
    assert not invalid_test_name(name)
    assert not invalid_rust_modules('mod ' + name + ' {}')


@pytest.mark.parametrize('relative,source', [
    ('tests/unit/test_orders.py', 'def test_round10_orders(): pass'),
    ('tests/unit/test_orders.py', 'class TestReviewFixes: pass'),
    ('tests/unit/test_orders.py', 'def test_code_review_status_fix(): pass'),
    ('crates/dcex/src/cache.rs', '#[test] fn review_regression_orders() {}'),
    ('crates/dcex/tests/review_regressions.rs', '#[test] fn orders() {}'),
    ('tests/async_support/test_orders.py', 'async def test_round12_orders(): pass'),
    ('tests/sync_support/test_orders.py', 'class TestRound12Orders: pass'),
    ('tests/unit/test_orders.py', 'def test_previewing_review_orders(): pass'),
])
def test_additional_process_name_mutations_fail(tmp_path, relative, source):
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    assert_behavior_names(tmp_path)
    path.write_text(source, encoding='utf8')
    with pytest.raises(AssertionError):
        assert_behavior_names(tmp_path)
