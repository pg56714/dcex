"""Offline wrapper tests for newly connected BingX swap market endpoints."""

import asyncio
from unittest.mock import AsyncMock, Mock
from urllib.parse import parse_qsl, urlsplit

import pytest

from dcex.async_support.bingx._account_http import AccountHTTP as AsyncAccountHTTP
from dcex.async_support.bingx._market_http import MarketHTTP as AsyncMarketHTTP
from dcex.bingx._account_http import AccountHTTP
from dcex.bingx._market_http import MarketHTTP
from tests.unit.native_http_helpers import _http_server


def test_sync_swap_market_and_commission_wrappers() -> None:
    """Synchronous BingX methods pass market and fee parameters to Rust."""
    market = object.__new__(MarketHTTP)
    market._native_public = Mock(return_value={"code": 0})
    market.get_swap_premium_index("BTC-USDT-SWAP")
    market.get_swap_funding_rate("BTC-USDT-SWAP", 1000, 2000, 10)
    market.get_swap_book_ticker("BTC-USDT-SWAP")
    market.get_swap_trading_rules("BTC-USDT-SWAP")
    calls = market._native_public.call_args_list
    assert [call.args[0] for call in calls] == [
        "get_swap_premium_index",
        "get_swap_funding_rate",
        "get_swap_book_ticker",
        "get_swap_trading_rules",
    ]
    assert calls[1].args[1] == [
        ("product_symbol", "BTC-USDT-SWAP"),
        ("start_time", "1000"),
        ("end_time", "2000"),
        ("limit", "10"),
    ]
    account = object.__new__(AccountHTTP)
    account._native_private = Mock(return_value={"code": 0})
    account.get_swap_commission_rate(5000)
    assert account._native_private.call_args.args == (
        "get_swap_commission_rate",
        [("recvWindow", "5000")],
    )


def test_async_swap_market_and_commission_wrappers() -> None:
    """Asynchronous BingX methods expose the same Rust request names."""

    async def check() -> None:
        market = object.__new__(AsyncMarketHTTP)
        market._native_public = AsyncMock(return_value={"code": 0})
        await market.get_swap_premium_index()
        await market.get_swap_funding_rate()
        await market.get_swap_book_ticker("BTC-USDT-SWAP")
        await market.get_swap_trading_rules("BTC-USDT-SWAP")
        assert [call.args[0] for call in market._native_public.call_args_list] == [
            "get_swap_premium_index",
            "get_swap_funding_rate",
            "get_swap_book_ticker",
            "get_swap_trading_rules",
        ]
        account = object.__new__(AsyncAccountHTTP)
        account._native_private = AsyncMock(return_value={"code": 0})
        await account.get_swap_commission_rate()
        assert account._native_private.call_args.args == ("get_swap_commission_rate", [])

    asyncio.run(check())


def test_bingx_native_swap_queries_reach_http() -> None:
    """PyO3 forwards the documented paths and auto-adds trading-rules timestamp."""
    native = pytest.importorskip("dcex._native")
    with _http_server({"code": 0, "data": {}}) as (base_url, received):
        public = native.BingxHttpClient(timeout=2, base_url=base_url)
        for method in (
            "get_swap_premium_index",
            "get_swap_funding_rate",
            "get_swap_book_ticker",
            "get_swap_trading_rules",
        ):
            public.public_request_json(method, [("product_symbol", "BTC-USDT-SWAP")])
        private = native.BingxHttpClient(
            api_key="api-key", api_secret="secret", timeout=2, base_url=base_url
        )
        private.private_request_json("get_swap_commission_rate", [])
    paths = [urlsplit(received.get_nowait()["path"]) for _ in range(5)]
    assert [path.path for path in paths] == [
        "/openApi/swap/v2/quote/premiumIndex",
        "/openApi/swap/v2/quote/fundingRate",
        "/openApi/swap/v2/quote/bookTicker",
        "/openApi/swap/v1/tradingRules",
        "/openApi/swap/v2/user/commissionRate",
    ]
    assert dict(parse_qsl(paths[3].query))["symbol"] == "BTC-USDT"
    assert int(dict(parse_qsl(paths[3].query))["timestamp"]) > 0
    assert "signature" in dict(parse_qsl(paths[4].query))
