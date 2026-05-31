"""Shared pytest configuration for test classification."""

from pathlib import Path

import pytest

_LIVE_TEST_DIRS = {"sync_support", "async_support"}
_STATEFUL_TESTS = {
    ("async_support", "bitmex", "test_positions.py", "test_set_leverage"),
    ("async_support", "bitmex", "test_positions.py", "test_set_margining_mode"),
    ("async_support", "bitmex", "test_positions.py", "test_switch_mode"),
    ("async_support", "okx", "test_account.py", "test_set_greeks"),
    ("async_support", "okx", "test_account.py", "test_set_leverage"),
    ("async_support", "okx", "test_account.py", "test_set_position_mode"),
    ("sync_support", "bitmex", "test_positions.py", "test_set_leverage"),
    ("sync_support", "bitmex", "test_positions.py", "test_set_margining_mode"),
    ("sync_support", "bitmex", "test_positions.py", "test_switch_mode"),
    ("sync_support", "okx", "test_account.py", "test_set_greeks"),
    ("sync_support", "okx", "test_account.py", "test_set_leverage"),
    ("sync_support", "okx", "test_account.py", "test_set_position_mode"),
}


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Mark exchange API tests as live so the default suite stays offline."""
    tests_root = Path(config.rootpath) / "tests"

    for item in items:
        item_path = Path(str(item.fspath))
        try:
            relative_path = item_path.relative_to(tests_root)
        except ValueError:
            continue

        if relative_path.parts and relative_path.parts[0] in _LIVE_TEST_DIRS:
            item.add_marker(pytest.mark.live)

        stateful_key = (*relative_path.parts, item.name)
        if stateful_key in _STATEFUL_TESTS:
            item.add_marker(pytest.mark.stateful)
