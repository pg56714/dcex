"""Offline verification for newly added Bitget and KuCoin UTA endpoints."""

# ruff: noqa: D103

from __future__ import annotations

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _patch_hyperliquid_market,
    _wire_async,
    _wire_sync,
)

UTA_CASES = (
    (
        "binance",
        "create_oco_order",
        {"product_symbol": "BTCUSDT-SPOT", "side": "SELL", "quantity": "1"},
        "NATIVE_PRIVATE",
    ),
    (
        "binance",
        "create_oto_order",
        {"product_symbol": "BTCUSDT-SPOT", "side": "BUY", "quantity": "1"},
        "NATIVE_PRIVATE",
    ),
    (
        "binance",
        "create_otoco_order",
        {"product_symbol": "BTCUSDT-SPOT", "side": "BUY", "quantity": "1"},
        "NATIVE_PRIVATE",
    ),
    (
        "binance",
        "get_prevented_matches",
        {"product_symbol": "BTCUSDT-SPOT"},
        "NATIVE_PRIVATE",
    ),
    (
        "binance",
        "get_allocations",
        {"product_symbol": "BTCUSDT-SPOT"},
        "NATIVE_PRIVATE",
    ),
    ("binance", "get_order_rate_limit", {}, "NATIVE_PRIVATE"),
    ("bitmex", "set_cancel_all_after", {"timeout": 60000}, "NATIVE_PRIVATE"),
    (
        "mexc",
        "place_contract_plan_order",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "vol": "1",
            "side": "1",
            "openType": "2",
            "triggerPrice": "100000",
            "triggerType": "1",
            "executeCycle": "1",
            "orderType": "1",
            "trend": "1",
            "leverage": "2",
        },
        "NATIVE_PRIVATE",
    ),
    ("mexc", "cancel_contract_plan_orders", {"orders": "[]"}, "NATIVE_PRIVATE"),
    ("mexc", "cancel_all_contract_plan_orders", {}, "NATIVE_PRIVATE"),
    ("kraken", "get_spot_system_status", {}, "NATIVE_PUBLIC"),
    ("kraken", "get_spot_assets", {}, "NATIVE_PUBLIC"),
    (
        "kraken",
        "get_spot_spread",
        {"product_symbol": "BTCUSDT-SPOT", "since": "1"},
        "NATIVE_PUBLIC",
    ),
    (
        "kraken",
        "cancel_spot_all_orders_after",
        {"timeout": "60"},
        "NATIVE_PRIVATE",
    ),
    ("kraken", "get_spot_websocket_token", {}, "NATIVE_PRIVATE"),
    ("bitget", "get_uta_all_fee_rates", {"category": "USDT-FUTURES"}, "NATIVE_PRIVATE"),
    ("bitget", "get_uta_loan_data", {}, "NATIVE_PRIVATE"),
    ("bitget", "get_uta_collateral_type", {}, "NATIVE_PRIVATE"),
    ("bitget", "get_uta_custom_collateral_coins", {}, "NATIVE_PRIVATE"),
    (
        "bitget",
        "get_uta_pre_set_leverage",
        {"category": "USDT-FUTURES", "marginMode": "cross"},
        "NATIVE_PRIVATE",
    ),
    (
        "bitget",
        "get_uta_liquidations",
        {"product_symbol": "BTC-USDT-SWAP"},
        "NATIVE_PUBLIC",
    ),
    (
        "bitget",
        "place_uta_strategy_order",
        {"category": "USDT-FUTURES", "product_symbol": "BTC-USDT-SWAP"},
        "NATIVE_PRIVATE",
    ),
    (
        "bitget",
        "modify_uta_strategy_order",
        {"qty": "1", "orderId": "123"},
        "NATIVE_PRIVATE",
    ),
    (
        "kucoin",
        "get_uta_fee_rates",
        {"tradeType": "SPOT", "symbol": "BTC-USDT"},
        "NATIVE_PRIVATE",
    ),
    (
        "kucoin",
        "get_uta_position_tiers",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "tradeType": "FUTURES",
            "data": "RISK_LIMIT",
            "accountType": "UNIFIED",
        },
        "NATIVE_PUBLIC",
    ),
    (
        "bybit",
        "pre_check_order",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "side": "Buy",
            "orderType": "Limit",
            "qty": "1",
        },
        "NATIVE_PRIVATE",
    ),
    (
        "bybit",
        "set_disconnected_cancel_all",
        {"timeWindow": "10"},
        "NATIVE_PRIVATE",
    ),
    (
        "okx",
        "pre_check_order",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "tdMode": "cross",
            "side": "buy",
            "ordType": "limit",
            "sz": "1",
        },
        "NATIVE_PRIVATE",
    ),
    (
        "okx",
        "set_cancel_all_after",
        {"timeOut": "10"},
        "NATIVE_PRIVATE",
    ),
)


@pytest.mark.parametrize(("exchange", "method_name", "kwargs", "request_type"), UTA_CASES)
def test_sync_uta_wrappers_only_build_native_requests(
    exchange: str,
    method_name: str,
    kwargs: dict[str, str],
    request_type: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_hyperliquid_market(monkeypatch)
    client = _client_class("sync", exchange)(**_client_kwargs(exchange))
    calls = _wire_sync(client)

    assert getattr(client, method_name)(**kwargs) == {"ok": True}
    assert calls == [
        {
            "method": request_type,
            "path": method_name,
            "query": [(key, str(value)) for key, value in kwargs.items()],
        }
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(("exchange", "method_name", "kwargs", "request_type"), UTA_CASES)
async def test_async_uta_wrappers_only_build_native_requests(
    exchange: str,
    method_name: str,
    kwargs: dict[str, str],
    request_type: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_hyperliquid_market(monkeypatch)
    client = _client_class("async", exchange)(**_client_kwargs(exchange))
    calls = _wire_async(client)

    assert await getattr(client, method_name)(**kwargs) == {"ok": True}
    assert calls == [
        {
            "method": request_type,
            "path": method_name,
            "query": [(key, str(value)) for key, value in kwargs.items()],
        }
    ]
