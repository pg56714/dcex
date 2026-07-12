"""Offline verification for the newly exposed account fee-rate wrappers."""

from __future__ import annotations

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _patch_hyperliquid_market,
    _wire_async,
    _wire_sync,
)


FEE_RATE_CASES = (
    ("binance", "get_spot_fee_rates", {"product_symbol": "BTC-USDT-SPOT"}, "NATIVE_PRIVATE"),
    ("binance", "get_futures_fee_rates", {"product_symbol": "BTC-USDT-SWAP"}, "NATIVE_PRIVATE"),
    ("bitget", "get_spot_fee_rates", {"product_symbol": "BTC-USDT-SPOT"}, "NATIVE_PRIVATE"),
    ("bitget", "get_futures_fee_rates", {"product_symbol": "BTC-USDT-SWAP"}, "NATIVE_PRIVATE"),
    ("bitmex", "get_futures_fee_rates", {}, "NATIVE_PRIVATE"),
    ("bybit", "get_spot_fee_rates", {}, "NATIVE_PRIVATE"),
    ("bybit", "get_linear_fee_rates", {}, "NATIVE_PRIVATE"),
    ("bybit", "get_inverse_fee_rates", {}, "NATIVE_PRIVATE"),
    ("bybit", "get_option_fee_rates", {}, "NATIVE_PRIVATE"),
    ("hyperliquid", "get_spot_fee_rates", {"user": "0x0000000000000000000000000000000000000001"}, "NATIVE_PUBLIC"),
    ("hyperliquid", "get_futures_fee_rates", {"user": "0x0000000000000000000000000000000000000001"}, "NATIVE_PUBLIC"),
    ("kucoin", "get_spot_fee_rates", {"product_symbol": "BTC-USDT-SPOT"}, "NATIVE_PRIVATE"),
    ("kucoin", "get_futures_fee_rates", {"product_symbol": "BTC-USDT-SWAP"}, "NATIVE_PRIVATE"),
    ("okx", "get_spot_fee_rates", {}, "NATIVE_PRIVATE"),
    ("okx", "get_margin_fee_rates", {}, "NATIVE_PRIVATE"),
    ("okx", "get_swap_fee_rates", {}, "NATIVE_PRIVATE"),
    ("okx", "get_futures_fee_rates", {}, "NATIVE_PRIVATE"),
    ("okx", "get_option_fee_rates", {}, "NATIVE_PRIVATE"),
)


@pytest.mark.parametrize(("exchange", "method_name", "kwargs", "request_type"), FEE_RATE_CASES)
def test_sync_fee_rate_wrappers_use_native_fee_endpoint(
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
            "query": list(
                (key, str(value).lower() if isinstance(value, bool) else str(value))
                for key, value in kwargs.items()
            ),
        }
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(("exchange", "method_name", "kwargs", "request_type"), FEE_RATE_CASES)
async def test_async_fee_rate_wrappers_use_native_fee_endpoint(
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
            "query": list(
                (key, str(value).lower() if isinstance(value, bool) else str(value))
                for key, value in kwargs.items()
            ),
        }
    ]
