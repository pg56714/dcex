"""Shared pytest configuration for test classification."""

import ast
import inspect
import os
import textwrap
from pathlib import Path

import pytest
from dotenv import load_dotenv

from tests.live_gate import stateful_tests_enabled
from tests.stateful_reporting import DETAILS, RESULTS, initial_result, update_report, write_results

load_dotenv(override=False)


@pytest.fixture
def stateful_result(request: pytest.FixtureRequest) -> dict[str, str]:
    """Allow the order lifecycle to record its market, stage and sanitized result."""
    result = request.node.stash.get(DETAILS, initial_result(request.node.nodeid))
    request.node.stash[DETAILS] = result
    return result


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Collect one redacted result per stateful test, including setup failures."""
    outcome = yield
    if item.get_closest_marker("stateful") is None:
        return
    report = outcome.get_result()
    results = item.config.stash.get(RESULTS, {})
    item.config.stash[RESULTS] = results
    details = item.stash.get(DETAILS, initial_result(item.nodeid))
    if report.when == "teardown" and not report.failed:
        return
    if report.when == "setup" and not (report.failed or report.skipped):
        return
    if report.when == "teardown" and item.nodeid in results:
        details = results[item.nodeid]
    results[item.nodeid] = update_report(details, report)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Persist stateful summaries without changing ordinary offline runs."""
    results = session.config.stash.get(RESULTS, {})
    write_results(Path(session.config.rootpath) / "live-results", list(results.values()))


def pytest_terminal_summary(
    terminalreporter: object, exitstatus: int, config: pytest.Config
) -> None:
    """Display a compact stateful status table without raw exchange responses."""
    results = config.stash.get(RESULTS, {})
    if not results:
        return
    terminalreporter.write_sep("=", "Stateful results")
    terminalreporter.write_line(
        "exchange | mode | market | stage | status | client_order_id | "
        "prior_client_order_ids | cleanup"
    )
    for row in results.values():
        terminalreporter.write_line(
            " | ".join(
                row[key]
                for key in (
                    "exchange",
                    "mode",
                    "market",
                    "stage",
                    "status",
                    "client_order_id",
                    "prior_client_order_ids",
                    "cleanup",
                )
            )
        )


_LIVE_TEST_DIRS = {"sync_support", "async_support"}
_relative_path_key = pytest.StashKey[Path | None]()
_PRIVATE_ENV_VARS = {
    "aster": ("ASTER_USER_ADDRESS", "ASTER_SIGNER_ADDRESS", "ASTER_PRIVATE_KEY"),
    "backpack": ("BACKPACK_API_KEY", "BACKPACK_API_SECRET"),
    "binance": ("BINANCE_API_KEY", "BINANCE_API_SECRET"),
    "bingx": ("BINGX_API_KEY", "BINGX_API_SECRET"),
    "bitget": ("BITGET_API_KEY", "BITGET_API_SECRET", "BITGET_PASSPHRASE"),
    "bybit": ("BYBIT_API_KEY", "BYBIT_API_SECRET"),
    "extended": ("EXTENDED_API_KEY",),
    "kucoin": ("KUCOIN_API_KEY", "KUCOIN_API_SECRET", "KUCOIN_API_PASSPHRASE"),
    "kraken": (
        "KRAKEN_SPOT_API_KEY",
        "KRAKEN_SPOT_API_SECRET",
        "KRAKEN_FUTURES_API_KEY",
        "KRAKEN_FUTURES_API_SECRET",
    ),
    "hyperliquid": ("HYPERLIQUID_WALLET_ADDRESS", "HYPERLIQUID_PRIVATE_KEY"),
    "mexc": ("MEXC_API_KEY", "MEXC_API_SECRET"),
    "ondo": ("ONDO_API_KEY_ID", "ONDO_API_SECRET"),
    "okx": ("OKX_API_KEY", "OKX_API_SECRET", "OKX_PASSPHRASE"),
}
_GENERATED_METHOD_NAMES = {
    "get_account_bills_history_archive",
    "get_monthly_statement",
    "post_account_bills_history_archive",
    "post_monthly_statement",
}


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
    return bool(
        relative_path and relative_path.name in {"test_stateful_trade.py", "test_stateful_ws.py"}
    )


def _calls_client_method(item: pytest.Item, names: set[str]) -> bool:
    """Check whether a test's AST calls an explicitly named client method."""
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
        if method_name in names:
            return True
    return False


def _calls_generated_client_method(item: pytest.Item) -> bool:
    return _calls_client_method(item, _GENERATED_METHOD_NAMES)


def _private_env_vars(item: pytest.Item, relative_path: Path | None) -> tuple[str, ...]:
    if item.get_closest_marker("private") is None or not _is_live_path(relative_path):
        return ()
    if relative_path is None or len(relative_path.parts) < 2:
        return ()
    exchange = relative_path.parts[1]
    if exchange == "extended" and _is_stateful_path(relative_path):
        return (
            "EXTENDED_API_KEY",
            "EXTENDED_STARK_PRIVATE_KEY",
            "EXTENDED_STARK_PUBLIC_KEY",
            "EXTENDED_VAULT_NUMBER",
        )
    return _PRIVATE_ENV_VARS.get(exchange, ())


def _stateful_tests_enabled() -> bool:
    return stateful_tests_enabled()


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

        if is_live_test and _is_stateful_path(relative_path):
            item.add_marker(pytest.mark.stateful)
