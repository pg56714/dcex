"""Shared pytest configuration for test classification."""

import ast
import inspect
import textwrap
from pathlib import Path

import pytest

_LIVE_TEST_DIRS = {"sync_support", "async_support"}
_STATEFUL_METHOD_PREFIXES = (
    "amend",
    "cancel",
    "change_margin",
    "close",
    "create",
    "funds_transfer",
    "future_dual_mode_switch",
    "modify",
    "place",
    "post_withdraw",
    "repay",
    "set",
    "submit_leverage",
    "switch",
    "transfer",
    "update",
    "upgrade",
    "withdraw",
)


def _calls_stateful_client_method(item: pytest.Item) -> bool:
    test_function = getattr(item, "obj", None)
    if test_function is None:
        return False

    try:
        source = textwrap.dedent(inspect.getsource(test_function))
    except (OSError, TypeError):
        return False

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        method_name = node.func.attr
        if method_name.startswith(_STATEFUL_METHOD_PREFIXES):
            return True
    return False


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Mark exchange API tests as live so the default suite stays offline."""
    tests_root = Path(config.rootpath) / "tests"

    for item in items:
        item_path = Path(str(item.fspath))
        try:
            relative_path = item_path.relative_to(tests_root)
        except ValueError:
            continue

        is_live_test = bool(relative_path.parts and relative_path.parts[0] in _LIVE_TEST_DIRS)
        if is_live_test:
            item.add_marker(pytest.mark.live)

        if is_live_test and _calls_stateful_client_method(item):
            item.add_marker(pytest.mark.stateful)
