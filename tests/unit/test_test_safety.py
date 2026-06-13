"""Tests for live-test safety controls."""
# ruff: noqa: D103

import importlib.util
from decimal import Decimal
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from dcex.utils.errors import FailedRequestError


def _load_test_conftest() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "conftest.py"
    spec = importlib.util.spec_from_file_location("dcex_test_conftest", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load tests/conftest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_test_module(relative_path: str, module_name: str) -> ModuleType:
    path = Path(__file__).resolve().parents[1] / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _stateful_item(module: ModuleType) -> object:
    class StatefulItem:
        stash = {module._relative_path_key: Path("sync_support/bybit/test_trade.py")}

        def get_closest_marker(self, name: str) -> object | None:
            return object() if name == "stateful" else None

    return StatefulItem()


def test_stateful_live_test_requires_explicit_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_test_conftest()
    monkeypatch.delenv("RUN_LIVE_TRADING_TESTS", raising=False)

    with pytest.raises(pytest.skip.Exception, match="RUN_LIVE_TRADING_TESTS=1"):
        module.pytest_runtest_setup(_stateful_item(module))


def test_stateful_live_test_runs_after_explicit_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_test_conftest()
    monkeypatch.setenv("RUN_LIVE_TRADING_TESTS", "1")

    module.pytest_runtest_setup(_stateful_item(module))


def test_change_contract_methods_are_classified_as_stateful(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_test_conftest()

    def test_contract_account(client: object) -> None:
        client.change_contract_leverage()

    source = """
def test_contract_account(client):
    client.change_contract_leverage()
"""
    monkeypatch.setattr(module.inspect, "getsource", lambda _: source)

    class TestItem:
        obj = test_contract_account

    assert module._calls_stateful_client_method(TestItem())


@pytest.mark.parametrize("method_name", ["get_listen_key", "keep_alive_listen_key"])
def test_listen_key_methods_are_classified_as_stateful(
    method_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_test_conftest()

    def test_account(client: object) -> None:
        pass

    source = f"""
def test_account(client):
    client.{method_name}()
"""
    monkeypatch.setattr(module.inspect, "getsource", lambda _: source)

    class TestItem:
        obj = test_account

    assert module._calls_stateful_client_method(TestItem())


@pytest.mark.parametrize(
    "path",
    [
        Path("sync_support/backpack/test_stateful_trade.py"),
        Path("async_support/aster/test_stateful_account.py"),
    ],
)
def test_stateful_test_files_are_classified_by_path(path: Path) -> None:
    module = _load_test_conftest()

    assert module._is_stateful_path(path)


def test_regular_live_test_files_are_not_classified_by_path() -> None:
    module = _load_test_conftest()

    assert not module._is_stateful_path(Path("sync_support/bybit/test_account.py"))


def test_collection_marks_stateful_file_without_matching_method_prefix(tmp_path: Path) -> None:
    module = _load_test_conftest()

    def read_only_test_body() -> None:
        pass

    class Config:
        rootpath = tmp_path

    class Item:
        fspath = tmp_path / "tests/sync_support/backpack/test_stateful_trade.py"
        stash: dict[object, object] = {}
        obj = read_only_test_body
        markers: list[object] = []

        def add_marker(self, marker: object) -> None:
            self.markers.append(marker)

    item = Item()
    module.pytest_collection_modifyitems(Config(), [item])

    assert any(getattr(marker, "name", None) == "stateful" for marker in item.markers)


def test_kraken_ambiguous_withdrawal_is_not_retried(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_test_module(
        "sync_support/kraken/test_stateful_trade.py",
        "dcex_sync_kraken_stateful_test",
    )
    withdraw = Mock(
        side_effect=FailedRequestError(
            request="POST https://futures.kraken.com/derivatives/api/v3/withdrawal",
            message="Service unavailable",
            status_code=503,
        )
    )
    client = SimpleNamespace(
        wallet_transfer_to_futures=Mock(return_value={"error": [], "result": {}}),
        withdraw_futures_to_spot_wallet=withdraw,
    )
    balances = iter((Decimal("1"), *(Decimal("0") for _ in range(6))))
    monkeypatch.setattr(module, "_spot_available", lambda *_: next(balances))
    monkeypatch.setattr(module.time, "sleep", lambda _: None)

    with pytest.raises(FailedRequestError, match="Service unavailable"):
        module.test_wallet_transfer_round_trip(client)

    assert withdraw.call_count == 1


@pytest.mark.asyncio
async def test_async_kraken_ambiguous_withdrawal_is_not_retried(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_test_module(
        "async_support/kraken/test_stateful_trade.py",
        "dcex_async_kraken_stateful_test",
    )
    withdraw = AsyncMock(
        side_effect=FailedRequestError(
            request="POST https://futures.kraken.com/derivatives/api/v3/withdrawal",
            message="Service unavailable",
            status_code=503,
        )
    )
    client = SimpleNamespace(
        wallet_transfer_to_futures=AsyncMock(return_value={"error": [], "result": {}}),
        withdraw_futures_to_spot_wallet=withdraw,
    )
    balances = iter((Decimal("1"), *(Decimal("0") for _ in range(6))))

    async def spot_available(*_args: object) -> Decimal:
        return next(balances)

    monkeypatch.setattr(module, "_spot_available", spot_available)
    monkeypatch.setattr(module.asyncio, "sleep", AsyncMock())

    with pytest.raises(FailedRequestError, match="Service unavailable"):
        await module.test_wallet_transfer_round_trip(client)

    assert withdraw.await_count == 1


def test_hyperliquid_unfilled_order_fails() -> None:
    module = _load_test_module(
        "sync_support/hyperliquid/test_stateful_trade.py",
        "dcex_sync_hyperliquid_stateful_test",
    )
    response = {
        "status": "ok",
        "response": {
            "type": "order",
            "data": {"statuses": [{"error": "Order must have minimum value of $10."}]},
        },
    }

    with pytest.raises(pytest.fail.Exception, match="minimum value"):
        module._filled_size(response)
