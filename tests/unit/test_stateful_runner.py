"""The shared runner cannot initialize clients before explicit opt-in."""

import importlib
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tests import stateful_runner as runner


@pytest.mark.asyncio
async def test_runner_without_opt_in_never_imports_client(monkeypatch):
    monkeypatch.delenv("RUN_LIVE_TRADING_TESTS", raising=False)
    monkeypatch.setattr("tests.live_gate.LIVE_TRADING_ENABLED", False)
    importer = Mock(side_effect=AssertionError("must not import client"))
    monkeypatch.setattr(runner.importlib, "import_module", importer)
    with pytest.raises(pytest.skip.Exception, match="RUN_LIVE_TRADING_TESTS"):
        await runner.run_case("binance", "sync", "spot", "BTC-USDC-SPOT", {})
    importer.assert_not_called()


@pytest.mark.parametrize(
    "exchange,name",
    [
        ("okx", "OKX_PASSPHRASE"),
        ("bitget", "BITGET_PASSPHRASE"),
        ("kucoin", "KUCOIN_API_PASSPHRASE"),
    ],
)
def test_runner_uses_existing_passphrase_variable_names(monkeypatch, exchange, name):
    monkeypatch.setenv(exchange.upper() + "_API_KEY", "fixture")
    monkeypatch.setenv(exchange.upper() + "_API_SECRET", "fixture")
    monkeypatch.delenv(name, raising=False)
    with pytest.raises(pytest.skip.Exception, match=name):
        runner.client_options(exchange)


def test_market_scope_excludes_coin_margin_and_kucoin_uta():
    assert runner.MARKETS["binance"][0] == ("spot", "BTC-USDC-SPOT")
    assert runner.MARKETS["binance"][1][1].endswith("-USDT-SWAP")
    assert [market for market, _ in runner.MARKETS["kucoin"]] == ["spot", "swap"]


@pytest.mark.asyncio
async def test_arcus_client_options_construct_every_arcus_client(monkeypatch):
    from dcex.arcus.client import Client
    from dcex.arcus.spot import SpotClient
    from dcex.async_support.arcus.client import Client as AsyncClient
    from dcex.async_support.arcus.spot import SpotClient as AsyncSpotClient
    from scripts.live.accounts import clients_for

    # Only the Python constructors are under test; the native clients are stubbed.
    native = SimpleNamespace(ArcusHttpClient=dict, ArcusSpotHttpClient=dict)
    for module in ("dcex.arcus._http_manager", "dcex.async_support.arcus._http_manager"):
        monkeypatch.setattr(importlib.import_module(module), "load_native", lambda: native)
    monkeypatch.setenv("ARCUS_API_KEY", "fixture-key")
    monkeypatch.setenv("ARCUS_API_SIGNING_KEY", "fixture-seed")
    monkeypatch.setenv("ARCUS_ADDRESS", "0x" + "33" * 20)
    options = runner.client_options("arcus")
    spot_options = {"wallet_address": options["address"], "logger": options["logger"]}
    Client(**options).close()
    SpotClient(**spot_options, timeout=20).close()
    for client in (AsyncClient(**options), AsyncSpotClient(**spot_options, timeout=20)):
        await client.async_init()
        await client.close()
    async with clients_for("arcus") as clients:
        assert [market for _, market, _ in clients] == ["spot", "swap"]
