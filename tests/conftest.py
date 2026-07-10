"""Shared pytest configuration for test classification."""

import ast
import inspect
import os
import textwrap
from pathlib import Path

import pytest

_LIVE_TEST_DIRS = {"sync_support", "async_support"}
_relative_path_key = pytest.StashKey[Path | None]()
_PRIVATE_ENV_VARS = {
    "aster": ("ASTER_USER_ADDRESS", "ASTER_SIGNER_ADDRESS", "ASTER_PRIVATE_KEY"),
    "backpack": ("BACKPACK_API_KEY", "BACKPACK_API_SECRET"),
    "binance": ("BINANCE_API_KEY", "BINANCE_API_SECRET"),
    "bingx": ("BINGX_API_KEY", "BINGX_API_SECRET"),
    "bitget": ("BITGET_API_KEY", "BITGET_API_SECRET", "BITGET_PASSPHRASE"),
    "bitmart": ("BITMART_API_KEY", "BITMART_API_SECRET", "BITMART_MEMO"),
    "bitmex": ("BITMEX_API_KEY", "BITMEX_API_SECRET"),
    "bybit": ("BYBIT_API_KEY", "BYBIT_API_SECRET"),
    "extended": ("EXTENDED_API_KEY",),
    "gateio": ("GATEIO_API_KEY", "GATEIO_API_SECRET"),
    "kucoin": ("KUCOIN_API_KEY", "KUCOIN_API_SECRET", "KUCOIN_API_PASSPHRASE"),
    "kraken": (
        "KRAKEN_SPOT_API_KEY",
        "KRAKEN_SPOT_API_SECRET",
        "KRAKEN_FUTURES_API_KEY",
        "KRAKEN_FUTURES_API_SECRET",
    ),
    "hyperliquid": ("HYPERLIQUID_WALLET_ADDRESS", "HYPERLIQUID_PRIVATE_KEY"),
    "lighter": (
        "LIGHTER_ACCOUNT_INDEX",
        "LIGHTER_API_KEY_INDEX",
        "LIGHTER_API_PRIVATE_KEY",
    ),
    "mexc": ("MEXC_API_KEY", "MEXC_API_SECRET"),
    "okx": ("OKX_API_KEY", "OKX_API_SECRET", "OKX_PASSPHRASE"),
}
_GENERATED_METHOD_NAMES = {
    "get_account_bills_history_archive",
    "get_monthly_statement",
    "post_account_bills_history_archive",
    "post_monthly_statement",
}
_STATEFUL_METHOD_NAMES = {
    "get_listen_key",
    "keep_alive_listen_key",
}
_STATEFUL_METHOD_PREFIXES = (
    "amend",
    "cancel",
    "change",
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


def _relative_test_path(config: pytest.Config, item: pytest.Item) -> Path | None:
    tests_root = Path(config.rootpath) / "tests"
    item_path = Path(str(item.fspath))
    try:
        return item_path.relative_to(tests_root)
    except ValueError:
        return None


def _is_live_path(relative_path: Path | None) -> bool:
    return bool(relative_path and relative_path.parts and relative_path.parts[0] in _LIVE_TEST_DIRS)


def _is_stateful_path(relative_path: Path | None) -> bool:
    return bool(relative_path and relative_path.name.startswith("test_stateful"))


def _calls_client_method(item: pytest.Item, names: set[str] | None = None) -> bool:
    """
    Check whether a test's AST calls certain client methods.

    When *names* is provided the check is an exact-match lookup against that
    set.  When *names* is ``None`` the check falls back to prefix-matching
    against ``_STATEFUL_METHOD_PREFIXES``.
    """
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
        if names is not None and method_name in names:
            return True
        if names is None and method_name.startswith(_STATEFUL_METHOD_PREFIXES):
            return True
    return False


def _calls_stateful_client_method(item: pytest.Item) -> bool:
    return _calls_client_method(item, _STATEFUL_METHOD_NAMES) or _calls_client_method(item)


def _calls_generated_client_method(item: pytest.Item) -> bool:
    return _calls_client_method(item, _GENERATED_METHOD_NAMES)


def _private_env_vars(item: pytest.Item, relative_path: Path | None) -> tuple[str, ...]:
    if item.get_closest_marker("private") is None or not _is_live_path(relative_path):
        return ()
    if relative_path is None or len(relative_path.parts) < 2:
        return ()
    exchange = relative_path.parts[1]
    if exchange == "extended" and _calls_stateful_client_method(item):
        return (
            "EXTENDED_API_KEY",
            "EXTENDED_STARK_PRIVATE_KEY",
            "EXTENDED_STARK_PUBLIC_KEY",
            "EXTENDED_VAULT_NUMBER",
        )
    return _PRIVATE_ENV_VARS.get(exchange, ())


def _stateful_tests_enabled() -> bool:
    return os.getenv("RUN_LIVE_TRADING_TESTS") == "1"


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Enforce opt-in and credential requirements for live tests."""
    relative_path = item.stash.get(_relative_path_key, None) or _relative_test_path(
        item.config, item
    )
    if (
        _is_live_path(relative_path)
        and item.get_closest_marker("stateful") is not None
        and not _stateful_tests_enabled()
    ):
        pytest.skip("Set RUN_LIVE_TRADING_TESTS=1 before running a stateful live test.")

    missing = [name for name in _private_env_vars(item, relative_path) if not os.getenv(name)]
    if missing:
        pytest.skip(f"Set {', '.join(missing)} before running this private live test.")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Mark exchange API tests as live so the default suite stays offline."""
    for item in items:
        relative_path = _relative_test_path(config, item)
        item.stash[_relative_path_key] = relative_path
        is_live_test = _is_live_path(relative_path)
        if is_live_test:
            item.add_marker(pytest.mark.live)

        if is_live_test and _calls_generated_client_method(item):
            item.add_marker(pytest.mark.generated)

        if is_live_test and (
            _is_stateful_path(relative_path) or _calls_stateful_client_method(item)
        ):
            item.add_marker(pytest.mark.stateful)
