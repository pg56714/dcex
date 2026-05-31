"""Shared pytest configuration for test classification."""

from pathlib import Path

import pytest

_LIVE_TEST_DIRS = {"sync_support", "async_support"}


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
