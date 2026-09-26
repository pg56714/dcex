"""
Offline coverage for Binance wrappers that the generic endpoint suite skips.

``_coin_futures_http.py`` and ``_convert_http.py`` do not match the shared
``ENDPOINT_FILE_SUFFIXES`` list, so these tests check that each sync and async
wrapper forwards the documented native method name and parameters, that the
Rust validation rejects unsafe COIN-M orders before any request is sent, and
that Convert wrappers reach the official ``/sapi/v1/convert`` paths on the wire.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

from dcex.async_support.binance.client import Client as AsyncClient
from dcex.binance.client import Client
from tests.unit.native_http_helpers import _http_server

TIME_PATHS = {"/api/v3/time", "/fapi/v1/time"}


@dataclass
class _Call:
    kind: str
    name: str
    params: list[tuple[str, str]]


@dataclass
class _FakeSyncNative:
    calls: list[_Call] = field(default_factory=list)

    def public_request_json(
        self, name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(_Call("public", name, list(params)))
        return 200, {}, {"ok": True}

    def private_request_json(
        self, name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(_Call("private", name, list(params)))
        return 200, {}, {"ok": True}


@dataclass
class _FakeAsyncNative:
    calls: list[_Call] = field(default_factory=list)

    async def public_request_json_async(
        self, name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(_Call("public", name, list(params)))
        return 200, {}, {"ok": True}

    async def private_request_json_async(
        self, name: str, params: list[tuple[str, str]]
    ) -> tuple[int, dict[str, str], object]:
        self.calls.append(_Call("private", name, list(params)))
        return 200, {}, {"ok": True}


@dataclass(frozen=True)
class WrapperCase:
    """One wrapper call and the native dispatch it must produce."""

    method: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    kind: str
    native_name: str
    params: list[tuple[str, str]]

    @property
    def id(self) -> str:
        """Return the pytest id for this case."""
        return self.method


WRAPPER_CASES = [
    # COIN-M futures (dapi)
    WrapperCase(
        "get_coin_futures_exchange_info",
        (),
        {},
        "public",
        "get_coin_futures_exchange_info",
        [],
    ),
    WrapperCase(
        "get_coin_futures_orderbook",
        ("BTCUSD_PERP",),
        {"limit": 5},
        "public",
        "get_coin_futures_orderbook",
        [("symbol", "BTCUSD_PERP"), ("limit", "5")],
    ),
    WrapperCase(
        "get_coin_futures_trades",
        ("BTCUSD_PERP",),
        {"limit": 10},
        "public",
        "get_coin_futures_trades",
        [("symbol", "BTCUSD_PERP"), ("limit", "10")],
    ),
    WrapperCase(
        "get_coin_futures_klines",
        ("BTCUSD_PERP", "1m"),
        {"startTime": 1, "endTime": 2, "limit": 3},
        "public",
        "get_coin_futures_klines",
        [
            ("symbol", "BTCUSD_PERP"),
            ("interval", "1m"),
            ("startTime", "1"),
            ("endTime", "2"),
            ("limit", "3"),
        ],
    ),
    WrapperCase(
        "get_coin_futures_ticker",
        (),
        {"pair": "BTCUSD"},
        "public",
        "get_coin_futures_ticker",
        [("pair", "BTCUSD")],
    ),
    WrapperCase(
        "get_coin_futures_mark_price",
        (),
        {"symbol": "BTCUSD_PERP"},
        "public",
        "get_coin_futures_mark_price",
        [("symbol", "BTCUSD_PERP")],
    ),
    WrapperCase(
        "get_coin_futures_funding_rate",
        ("BTCUSD_PERP",),
        {"limit": 100},
        "public",
        "get_coin_futures_funding_rate",
        [("symbol", "BTCUSD_PERP"), ("limit", "100")],
    ),
    WrapperCase(
        "get_coin_futures_balance",
        (),
        {},
        "private",
        "get_coin_futures_balance",
        [],
    ),
    WrapperCase(
        "get_coin_futures_account",
        (),
        {},
        "private",
        "get_coin_futures_account",
        [],
    ),
    WrapperCase(
        "get_coin_futures_positions",
        (),
        {"marginAsset": "BTC"},
        "private",
        "get_coin_futures_positions",
        [("marginAsset", "BTC")],
    ),
    WrapperCase(
        "get_coin_futures_open_orders",
        (),
        {"symbol": "BTCUSD_PERP"},
        "private",
        "get_coin_futures_open_orders",
        [("symbol", "BTCUSD_PERP")],
    ),
    WrapperCase(
        "get_coin_futures_order",
        ("BTCUSD_PERP",),
        {"orderId": 7},
        "private",
        "get_coin_futures_order",
        [("symbol", "BTCUSD_PERP"), ("orderId", "7")],
    ),
    WrapperCase(
        "place_coin_futures_order",
        ("BTCUSD_PERP", "BUY", "LIMIT", "1"),
        {"price": "50000", "timeInForce": "GTC", "reduceOnly": True, "newClientOrderId": "c1"},
        "private",
        "place_coin_futures_order",
        [
            ("symbol", "BTCUSD_PERP"),
            ("side", "BUY"),
            ("type", "LIMIT"),
            ("quantity", "1"),
            ("price", "50000"),
            ("timeInForce", "GTC"),
            ("reduceOnly", "true"),
            ("newClientOrderId", "c1"),
        ],
    ),
    WrapperCase(
        "cancel_coin_futures_order",
        ("BTCUSD_PERP",),
        {"origClientOrderId": "c1"},
        "private",
        "cancel_coin_futures_order",
        [("symbol", "BTCUSD_PERP"), ("origClientOrderId", "c1")],
    ),
    WrapperCase(
        "cancel_all_coin_futures_orders",
        ("BTCUSD_PERP",),
        {},
        "private",
        "cancel_all_coin_futures_orders",
        [("symbol", "BTCUSD_PERP")],
    ),
    # Convert (sapi)
    WrapperCase(
        "get_convert_pairs",
        (),
        {"fromAsset": "BTC"},
        "public",
        "get_convert_pairs",
        [("fromAsset", "BTC")],
    ),
    WrapperCase(
        "get_convert_asset_info",
        (),
        {},
        "private",
        "get_convert_asset_info",
        [],
    ),
    WrapperCase(
        "get_convert_quote",
        ("BTC", "USDT"),
        {"fromAmount": "0.1", "walletType": "SPOT", "validTime": "10s"},
        "private",
        "get_convert_quote",
        [
            ("fromAsset", "BTC"),
            ("toAsset", "USDT"),
            ("fromAmount", "0.1"),
            ("walletType", "SPOT"),
            ("validTime", "10s"),
        ],
    ),
    WrapperCase(
        "accept_convert_quote",
        ("q-1",),
        {},
        "private",
        "accept_convert_quote",
        [("quoteId", "q-1")],
    ),
    WrapperCase(
        "get_convert_order_status",
        (),
        {"quoteId": "q-1"},
        "private",
        "get_convert_order_status",
        [("quoteId", "q-1")],
    ),
    WrapperCase(
        "get_convert_trade_history",
        (1_700_000_000_000, 1_700_086_400_000),
        {"limit": 50},
        "private",
        "get_convert_trade_history",
        [("startTime", "1700000000000"), ("endTime", "1700086400000"), ("limit", "50")],
    ),
    WrapperCase(
        "place_convert_limit_order",
        ("BTC", "USDT", "60000", "BUY", "1_D"),
        {"quoteAmount": "100"},
        "private",
        "place_convert_limit_order",
        [
            ("baseAsset", "BTC"),
            ("quoteAsset", "USDT"),
            ("limitPrice", "60000"),
            ("side", "BUY"),
            ("expiredType", "1_D"),
            ("quoteAmount", "100"),
        ],
    ),
    WrapperCase(
        "cancel_convert_limit_order",
        (123,),
        {},
        "private",
        "cancel_convert_limit_order",
        [("orderId", "123")],
    ),
    WrapperCase(
        "get_open_convert_limit_orders",
        (),
        {},
        "private",
        "get_open_convert_limit_orders",
        [],
    ),
]


def test_wrapper_cases_cover_every_coin_futures_and_convert_method() -> None:
    """Every public method in the two uncovered wrapper modules has a case."""
    from dcex.binance._coin_futures_http import CoinFuturesHTTP
    from dcex.binance._convert_http import ConvertHTTP

    expected = {
        name
        for cls in (CoinFuturesHTTP, ConvertHTTP)
        for name, value in vars(cls).items()
        if callable(value) and not name.startswith("_")
    }
    assert expected == {case.method for case in WRAPPER_CASES}


@pytest.mark.parametrize("case", WRAPPER_CASES, ids=lambda case: case.id)
def test_sync_wrapper_forwards_native_name_and_params(case: WrapperCase) -> None:
    """Sync wrappers call the documented native dispatch name with exact params."""
    client = Client(api_key="api-key", api_secret="api-secret", preload_product_table=False)
    fake = _FakeSyncNative()
    client._native_client = fake
    try:
        result = getattr(client, case.method)(*case.args, **case.kwargs)
    finally:
        client._native_client = None
    assert result == {"ok": True}
    assert fake.calls == [_Call(case.kind, case.native_name, case.params)]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", WRAPPER_CASES, ids=lambda case: case.id)
async def test_async_wrapper_forwards_native_name_and_params(case: WrapperCase) -> None:
    """Async wrappers call the documented native dispatch name with exact params."""
    client = AsyncClient(api_key="api-key", api_secret="api-secret", preload_product_table=False)
    await client.async_init()
    fake = _FakeAsyncNative()
    client._native_client = fake
    try:
        result = await getattr(client, case.method)(*case.args, **case.kwargs)
    finally:
        client._native_client = None
    assert result == {"ok": True}
    assert fake.calls == [_Call(case.kind, case.native_name, case.params)]


INVALID_COIN_FUTURES_CASES = [
    pytest.param(
        "place_coin_futures_order",
        ("BTCUSD_PERP", "BUY", "LIMIT", "1"),
        {},
        "price",
        id="limit-without-price",
    ),
    pytest.param(
        "place_coin_futures_order",
        ("BTCUSD_PERP", "BUY", "STOP", "1"),
        {"price": "1"},
        "type",
        id="unsupported-order-type",
    ),
    pytest.param(
        "place_coin_futures_order",
        ("BTCUSD_PERP", "HOLD", "MARKET", "1"),
        {},
        "side",
        id="invalid-side",
    ),
    pytest.param(
        "place_coin_futures_order",
        ("BTCUSD_PERP", "BUY", "MARKET", "-1"),
        {},
        "quantity must be positive",
        id="negative-quantity",
    ),
    pytest.param(
        "place_coin_futures_order",
        ("BTC-USD-SWAP", "BUY", "MARKET", "1"),
        {},
        "native Binance symbol",
        id="canonical-symbol",
    ),
    pytest.param(
        "cancel_coin_futures_order",
        ("BTCUSD_PERP",),
        {},
        "orderId or origClientOrderId",
        id="cancel-without-id",
    ),
    pytest.param(
        "get_coin_futures_order",
        ("BTCUSD_PERP",),
        {},
        "orderId or origClientOrderId",
        id="lookup-without-id",
    ),
    pytest.param(
        "get_coin_futures_open_orders",
        (),
        {"symbol": "BTCUSD_PERP", "pair": "BTCUSD"},
        "cannot be sent together",
        id="open-orders-symbol-and-pair",
    ),
    pytest.param(
        "get_coin_futures_klines",
        ("BTCUSD_PERP", "1m"),
        {"limit": 5000},
        "limit",
        id="klines-limit-out-of-range",
    ),
]


@pytest.mark.parametrize(("method", "args", "kwargs", "message"), INVALID_COIN_FUTURES_CASES)
def test_sync_coin_futures_validation_rejects_before_network(
    method: str, args: tuple[Any, ...], kwargs: dict[str, Any], message: str
) -> None:
    """Rust validation rejects unsafe COIN-M requests before any HTTP call."""
    client = Client(api_key="api-key", api_secret="api-secret", preload_product_table=False)
    try:
        with pytest.raises(ValueError, match=message):
            getattr(client, method)(*args, **kwargs)
    finally:
        client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(("method", "args", "kwargs", "message"), INVALID_COIN_FUTURES_CASES)
async def test_async_coin_futures_validation_rejects_before_network(
    method: str, args: tuple[Any, ...], kwargs: dict[str, Any], message: str
) -> None:
    """Async Rust validation rejects unsafe COIN-M requests before any HTTP call."""
    client = AsyncClient(api_key="api-key", api_secret="api-secret", preload_product_table=False)
    await client.async_init()
    try:
        with pytest.raises(ValueError, match=message):
            await getattr(client, method)(*args, **kwargs)
    finally:
        await client.close()


INVALID_CONVERT_CASES = [
    pytest.param("get_convert_pairs", (), {}, "fromAsset or toAsset", id="pairs-no-asset"),
    pytest.param(
        "get_convert_quote",
        ("BTC", "USDT"),
        {},
        "exactly one",
        id="quote-without-amount",
    ),
    pytest.param(
        "get_convert_quote",
        ("BTC", "USDT"),
        {"fromAmount": "1", "validTime": "5m"},
        "validTime",
        id="quote-invalid-valid-time",
    ),
    pytest.param(
        "get_convert_order_status",
        (),
        {},
        "orderId or quoteId",
        id="status-without-id",
    ),
    pytest.param(
        "get_convert_trade_history",
        (1_700_000_000_000, 1_700_000_000_000 + 31 * 24 * 60 * 60 * 1000),
        {},
        "30 days",
        id="history-range-too-long",
    ),
    pytest.param(
        "place_convert_limit_order",
        ("BTC", "USDT", "60000", "BUY", "1_D"),
        {"baseAmount": "1", "quoteAmount": "1"},
        "exactly one",
        id="limit-both-amounts",
    ),
    pytest.param(
        "place_convert_limit_order",
        ("BTC", "USDT", "60000", "BUY", "2_D"),
        {"baseAmount": "1"},
        "expiredType",
        id="limit-invalid-expiry",
    ),
]


@pytest.mark.parametrize(("method", "args", "kwargs", "message"), INVALID_CONVERT_CASES)
def test_sync_convert_validation_rejects_before_network(
    method: str, args: tuple[Any, ...], kwargs: dict[str, Any], message: str
) -> None:
    """Rust validation rejects malformed Convert requests before any HTTP call."""
    client = Client(api_key="api-key", api_secret="api-secret", preload_product_table=False)
    try:
        with pytest.raises(ValueError, match=message):
            getattr(client, method)(*args, **kwargs)
    finally:
        client.close()


CONVERT_WIRE_CASES = [
    pytest.param(
        "get_convert_pairs",
        (),
        {"toAsset": "USDT"},
        "/sapi/v1/convert/exchangeInfo",
        False,
        id="pairs",
    ),
    pytest.param(
        "get_convert_asset_info", (), {}, "/sapi/v1/convert/assetInfo", True, id="asset-info"
    ),
    pytest.param(
        "get_convert_quote",
        ("BTC", "USDT"),
        {"toAmount": "100"},
        "/sapi/v1/convert/getQuote",
        True,
        id="quote",
    ),
    pytest.param(
        "accept_convert_quote", ("q-1",), {}, "/sapi/v1/convert/acceptQuote", True, id="accept"
    ),
    pytest.param(
        "get_convert_order_status",
        (),
        {"orderId": "9"},
        "/sapi/v1/convert/orderStatus",
        True,
        id="status",
    ),
    pytest.param(
        "get_convert_trade_history",
        (1_700_000_000_000, 1_700_086_400_000),
        {},
        "/sapi/v1/convert/tradeFlow",
        True,
        id="history",
    ),
    pytest.param(
        "place_convert_limit_order",
        ("BTC", "USDT", "60000", "SELL", "7_D"),
        {"baseAmount": "0.01"},
        "/sapi/v1/convert/limit/placeOrder",
        True,
        id="limit-place",
    ),
    pytest.param(
        "cancel_convert_limit_order",
        (5,),
        {},
        "/sapi/v1/convert/limit/cancelOrder",
        True,
        id="limit-cancel",
    ),
    pytest.param(
        "get_open_convert_limit_orders",
        (),
        {},
        "/sapi/v1/convert/limit/queryOpenOrders",
        True,
        id="limit-open",
    ),
]


def _last_business_request(received: Any) -> dict[str, Any]:  # noqa: ANN401
    requests: list[dict[str, Any]] = []
    while not received.empty():
        request = received.get_nowait()
        if urlsplit(request["path"]).path not in TIME_PATHS:
            requests.append(request)
    assert len(requests) == 1, requests
    return requests[0]


@pytest.mark.parametrize(("method", "args", "kwargs", "path", "signed"), CONVERT_WIRE_CASES)
def test_sync_convert_wrappers_reach_official_paths(
    method: str, args: tuple[Any, ...], kwargs: dict[str, Any], path: str, signed: bool
) -> None:
    """Convert wrappers hit the documented /sapi/v1/convert path through native HTTP."""
    native = pytest.importorskip("dcex._native")
    with _http_server() as (base_url, received):
        client = Client(api_key="api-key", api_secret="api-secret", preload_product_table=False)
        client._native_client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="api-secret",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        try:
            assert getattr(client, method)(*args, **kwargs) == {"ok": True}
        finally:
            client.close()
        request = _last_business_request(received)

    split = urlsplit(request["path"])
    assert split.path == path
    query = dict(parse_qsl(split.query))
    query.update(dict(parse_qsl(request["body"])))
    assert ("signature" in query) is signed
    if signed:
        assert request["api_key"] == "api-key"
        assert "timestamp" in query


@pytest.mark.asyncio
@pytest.mark.parametrize(("method", "args", "kwargs", "path", "signed"), CONVERT_WIRE_CASES)
async def test_async_convert_wrappers_reach_official_paths(
    method: str, args: tuple[Any, ...], kwargs: dict[str, Any], path: str, signed: bool
) -> None:
    """Async Convert wrappers hit the documented /sapi/v1/convert path."""
    native = pytest.importorskip("dcex._native")
    with _http_server() as (base_url, received):
        client = AsyncClient(
            api_key="api-key", api_secret="api-secret", preload_product_table=False
        )
        await client.async_init()
        client._native_client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="api-secret",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        try:
            assert await getattr(client, method)(*args, **kwargs) == {"ok": True}
        finally:
            await client.close()
        request = _last_business_request(received)

    split = urlsplit(request["path"])
    assert split.path == path
    query = dict(parse_qsl(split.query))
    query.update(dict(parse_qsl(request["body"])))
    assert ("signature" in query) is signed


@pytest.mark.parametrize("method", ["keep_alive_listen_key", "close_listen_key"])
def test_sync_futures_listen_key_calls_send_no_parameters(method: str) -> None:
    """PUT/DELETE /fapi/v1/listenKey take no parameters; the key is not sent."""
    native = pytest.importorskip("dcex._native")
    with _http_server() as (base_url, received):
        client = Client(api_key="api-key", api_secret="api-secret", preload_product_table=False)
        client._native_client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="api-secret",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        try:
            getattr(client, method)("listen-key")
        finally:
            client.close()
        request = _last_business_request(received)

    assert request["path"] == "/fapi/v1/listenKey"
    assert request["body"] == ""
