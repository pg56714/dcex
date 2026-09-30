"""Keep regression filenames and Rust test modules named by behavior."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]


def invalid_test_name(filename):
    return bool(re.match(r'test_(?:round_|review_|generated_review_)', filename))


def invalid_rust_modules(source):
    from tests.unit.rust_dispatch import mask
    return re.findall(r'\bmod\s+(review_\w+)', mask(source))


def test_regression_names_describe_behavior():
    assert not [p.name for p in (ROOT / 'tests/unit').glob('test_*.py') if invalid_test_name(p.name)]
    assert not [(str(p.relative_to(ROOT)), invalid_rust_modules(p.read_text(encoding='utf8'))) for p in (ROOT / 'crates').rglob('*.rs') if invalid_rust_modules(p.read_text(encoding='utf8'))]


@pytest.mark.parametrize('filename', ['test_round_new.py', 'test_review_orders.py', 'test_generated_review_aliases.py'])
def test_obsolete_filename_mutations_are_rejected(filename):
    assert invalid_test_name(filename)


def test_old_rust_module_mutation_is_rejected():
    assert invalid_rust_modules('mod review_cache_tests {}') == ['review_cache_tests']
    assert not invalid_rust_modules('// mod review_cache_tests {}\nmod schema_cache_tests {}')


def test_exchange_native_names_and_round_trip_scenarios_remain_valid():
    assert not invalid_test_name('test_wallet_transfer_round_trip.py')
    assert not invalid_rust_modules('mod preview_tests {}')
