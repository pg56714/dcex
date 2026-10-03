"""Offline tests of documented maker-only types, expiry units and order fields."""

import time
from decimal import Decimal

import pytest

from tests.stateful_adapters import CexAdapter, normalize_order
from tests.stateful_dex import ExtendedAdapter, HyperliquidAdapter, LighterAdapter
from tests.unit.test_stateful_adapters import ExchangeMock, order_record
from tests.unit.test_stateful_dex import DexMock


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exchange,spot,expected",
    [
        ("binance", True, {"type_": "LIMIT_MAKER"}),
        ("binance", False, {"type_": "LIMIT", "timeInForce": "GTX"}),
        ("aster", True, {"timeInForce": "GTX"}),
        ("aster", False, {"timeInForce": "GTX"}),
        ("bybit", True, {"timeInForce": "PostOnly"}),
        ("bybit", False, {"timeInForce": "PostOnly"}),
        ("okx", True, {"ordType": "post_only"}),
        ("bitget", False, {"time_in_force": "post_only"}),
        ("bingx", True, {"time_in_force": "PostOnly"}),
        ("bingx", False, {"time_in_force": "PostOnly"}),
        ("mexc", True, {"type_": "LIMIT_MAKER"}),
        ("mexc", False, {"type_": 2}),
    ],
)
async def test_cex_uses_documented_maker_only_parameters(exchange, spot, expected):
    client = ExchangeMock(exchange, spot, "sync")
    adapter = CexAdapter(
        client, exchange, "spot" if spot else "swap", "BTC-USDT-SPOT" if spot else "BTC-USDT-SWAP"
    )
    plan, _ = await adapter.prepare()
    await adapter.place(plan)
    params = next(params for method, params in client.calls if method.startswith("place_"))
    assert expected.items() <= params.items()
    if exchange == "binance" and spot:
        assert "timeInForce" not in params


@pytest.mark.asyncio
async def test_dex_maker_only_and_lighter_expiry_milliseconds(monkeypatch):
    monkeypatch.setattr(time, "time", lambda: 1_800_000_000.0)
    for exchange, cls in [("hyperliquid", HyperliquidAdapter), ("lighter", LighterAdapter)]:
        client = DexMock(exchange, "sync")
        adapter = cls(
            client,
            exchange,
            "swap" if exchange == "hyperliquid" else "mainnet",
            "BTC-USD-SWAP" if exchange == "hyperliquid" else "ETH",
        )
        plan, _ = await adapter.prepare()
        await adapter.place(plan)
        params = next(
            params for method, params in client.calls if method in {"place_order", "create_order"}
        )
        if exchange == "hyperliquid":
            assert params["tif"] == "Alo"
        else:
            assert params["time_in_force"] == 2
            assert params["order_expiry"] == 1_800_000_000_000 + 28 * 24 * 60 * 60 * 1000


def test_mexc_contract_reads_documented_order_type_and_rejects_missing_field():
    row = order_record("mexc", False)
    row["orderType"] = 2
    row["type"] = 5  # unrelated field must not override the documented one
    assert normalize_order("mexc", False, row, "123").kind == "limit"
    del row["orderType"]
    with pytest.raises(KeyError):
        normalize_order("mexc", False, row, "123")


@pytest.mark.parametrize(
    "exchange,kind", [("binance", "LIMIT_MAKER"), ("mexc", "LIMIT_MAKER"), ("okx", "post_only")]
)
def test_maker_only_order_query_types_are_limits(exchange, kind):
    row = order_record(exchange, True)
    row["ordType" if exchange == "okx" else "type"] = kind
    assert normalize_order(exchange, True, row, "123").kind == "limit"


@pytest.mark.asyncio
@pytest.mark.parametrize("spot", [False, True])
async def test_aster_price_bands_are_not_ignored(spot):
    client = ExchangeMock("aster", spot, "sync")
    original = client.payload

    def payload(method, kwargs):
        if method.endswith("exchange_info"):
            return {
                "symbols": [
                    {
                        "symbol": "BTCUSDT",
                        "filters": [
                            {
                                "filterType": "PERCENT_PRICE",
                                "multiplierDown": ".95",
                                "multiplierUp": "1.05",
                            }
                        ],
                    }
                ]
            }
        if method == "get_futures_premium_index":
            return {"markPrice": "100", "indexPrice": "100"}
        return original(method, kwargs)

    client.payload = payload
    adapter = CexAdapter(
        client, "aster", "spot" if spot else "swap", "BTC-USDT-SPOT" if spot else "BTC-USDT-SWAP"
    )
    plan, _ = await adapter.prepare()
    # Spot uses the best bid (100) as its reference; futures use the 100 mark price.
    # Either way the price sits inside the band with a margin above the 95 floor.
    assert Decimal(95) + (Decimal(100) - Decimal(95)) / 4 <= plan.price < Decimal(100)


@pytest.mark.asyncio
@pytest.mark.parametrize("spot", [False, True])
@pytest.mark.parametrize("reference", ["80", "100", "110"])
async def test_extended_clamps_price_without_crossing(spot, reference):
    client = DexMock("extended", "sync")
    original = client.response

    def response(method, kwargs):
        value = original(method, kwargs)
        if method == "get_markets":
            value[0]["tradingConfig"].update(limitPriceFloor=".05", limitPriceCap=".05")
            value[0]["marketStats"]["indexPrice" if spot else "markPrice"] = reference
        return value

    client.response = response
    adapter = ExtendedAdapter(
        client, "extended", "spot" if spot else "swap", "BTC-USD-SPOT" if spot else "BTC-USD-SWAP"
    )
    plan, _ = await adapter.prepare()
    assert plan.price == min(Decimal(90), Decimal(reference) * Decimal("1.05"))
    assert plan.price < Decimal(100)


@pytest.mark.asyncio
@pytest.mark.parametrize("exchange,spot", [("backpack", True), ("kraken", False), ("bitget", True)])
async def test_best_bid_and_ask_ignore_level_order(exchange, spot):
    client = ExchangeMock(exchange, spot, "sync")
    original = client.payload

    def payload(method, kwargs):
        value = original(method, kwargs)
        if "orderbook" in method or method == "get_order_book_depth":
            book = value["orderBook"] if exchange == "kraken" else value
            bids, asks = ("b", "a") if exchange == "bitget" else ("bids", "asks")
            book[bids] = [["30", "1"], ["99", "1"], ["100", "1"]]
            book[asks] = [["103", "1"], ["101", "1"]]
        return value

    client.payload = payload
    adapter = CexAdapter(
        client, exchange, "spot" if spot else "swap", "BTC-USDT-SPOT" if spot else "BTC-USDT-SWAP"
    )
    assert await adapter.book() == (Decimal(100), Decimal(101))
