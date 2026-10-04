"""Order flags: documented values reach the wire; unsupported ones fail before any request."""

# ruff: noqa: D103
from __future__ import annotations

import base64
import json
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server

native = pytest.importorskip("dcex._native")


def _binance(base: str) -> Any:
    return native.BinanceHttpClient(
        api_key="api-key",
        api_secret="secret",
        timeout=10,
        spot_base_url=base,
        futures_base_url=base,
    )


def _bitget(base: str) -> Any:
    return native.BitgetHttpClient(
        api_key="api-key", api_secret="secret", passphrase="pass", timeout=10, base_url=base
    )


def _bybit(base: str) -> Any:
    return native.BybitHttpClient(
        api_key="api-key",
        api_secret="secret",
        recv_window=5000,
        sync_server_time=False,
        timeout=10,
        base_url=base,
    )


def _okx(base: str) -> Any:
    return native.OkxHttpClient(
        api_key="api-key",
        api_secret="secret",
        passphrase="pass",
        flag="1",
        timeout=10,
        base_url=base,
    )


def _kraken(base: str) -> Any:
    secret = base64.b64encode(b"secret").decode()
    return native.KrakenHttpClient(
        spot_api_key="api-key",
        spot_api_secret=secret,
        futures_api_key="api-key",
        futures_api_secret=secret,
        timeout=10,
        spot_base_url=base,
        futures_base_url=base,
    )


def _mexc(base: str) -> Any:
    return native.MexcHttpClient(
        api_key="api-key", api_secret="secret", timeout=10, base_url=base, contract_base_url=base
    )


def _backpack(base: str) -> Any:
    return native.BackpackHttpClient(
        api_key=base64.b64encode(b"2" * 32).decode(),
        api_secret=base64.b64encode(b"1" * 32).decode(),
        window=5000,
        timeout=10,
        base_url=base,
    )


def _order_requests(received: Any) -> list[dict[str, Any]]:
    requests = []
    while not received.empty():
        item = received.get_nowait()
        if not urlsplit(item["path"]).path.endswith("/time"):
            requests.append(item)
    return requests


def _fields(request: dict[str, Any]) -> dict[str, Any]:
    body = request["body"]
    if body.startswith("{"):
        return json.loads(body)
    return dict(parse_qsl(urlsplit(request["path"]).query or body))


BINANCE_SPOT = [("product_symbol", "BTC-USDT-SPOT"), ("side", "BUY"), ("quantity", "1")]
BINANCE_SWAP = [("product_symbol", "BTC-USDT-SWAP"), ("side", "BUY"), ("quantity", "1")]
BITGET_SWAP = [
    ("product_symbol", "BTC-USDT-SWAP"),
    ("category", "USDT-FUTURES"),
    ("side", "buy"),
    ("orderType", "limit"),
    ("qty", "1"),
    ("price", "100"),
]
BITGET_SPOT = [
    ("product_symbol", "BTC-USDT-SPOT"),
    ("category", "SPOT"),
    ("side", "buy"),
    ("orderType", "limit"),
    ("qty", "1"),
    ("price", "100"),
]
BYBIT = [
    ("product_symbol", "BTC-USDT-SWAP"),
    ("side", "Buy"),
    ("orderType", "Limit"),
    ("qty", "1"),
    ("price", "100"),
]
OKX = [
    ("product_symbol", "BTC-USDT-SWAP"),
    ("tdMode", "cross"),
    ("side", "buy"),
    ("ordType", "limit"),
    ("sz", "1"),
    ("px", "100"),
]
KRAKEN_FUTURES = [
    ("product_symbol", "PF_XBTUSD"),
    ("side", "buy"),
    ("orderType", "lmt"),
    ("size", "1"),
    ("limitPrice", "100"),
]
MEXC = [
    ("product_symbol", "BTC_USDT"),
    ("side", "4"),
    ("type", "1"),
    ("openType", "1"),
    ("vol", "1"),
    ("price", "100"),
]
BACKPACK_SPOT = [("product_symbol", "BTC-USDC-SPOT"), ("side", "Ask"), ("quantity", "1")]

VALID = [
    (
        "binance-spot",
        _binance,
        "place_order",
        [*BINANCE_SPOT, ("type_", "LIMIT"), ("price", "100"), ("timeInForce", "FOK")],
        {"timeInForce": "FOK"},
    ),
    (
        "binance-usdm",
        _binance,
        "place_order",
        [
            *BINANCE_SWAP,
            ("type_", "LIMIT"),
            ("price", "100"),
            ("timeInForce", "GTX"),
            ("reduceOnly", "true"),
        ],
        {"timeInForce": "GTX", "reduceOnly": "true"},
    ),
    (
        "bitget-uta",
        _bitget,
        "place_uta_order",
        [*BITGET_SWAP, ("timeInForce", "post_only"), ("reduceOnly", "yes"), ("stpMode", "none")],
        {"timeInForce": "post_only", "reduceOnly": "yes", "stpMode": "none"},
    ),
    (
        "bitget-uta-spot-auto-borrow",
        _bitget,
        "place_uta_order",
        [*BITGET_SPOT, ("autoBorrow", "no"), ("pxAmendType", "yes")],
        {"autoBorrow": "no", "pxAmendType": "yes"},
    ),
    (
        "okx-amend",
        _okx,
        "amend_order",
        [
            ("product_symbol", "BTC-USDT-SWAP"),
            ("ordId", "1"),
            ("newSz", "2"),
            ("cxlOnFail", "true"),
            ("reqId", "r1"),
        ],
        {"newSz": "2", "cxlOnFail": True, "reqId": "r1"},
    ),
    (
        "bybit-amend",
        _bybit,
        "amend_order",
        [("product_symbol", "BTC-USDT-SWAP"), ("orderId", "1"), ("price", "101")],
        {"orderId": "1", "price": "101"},
    ),
    (
        "bybit",
        _bybit,
        "place_order",
        [*BYBIT, ("timeInForce", "PostOnly"), ("orderLinkId", "c1"), ("smpType", "CancelMaker")],
        {"timeInForce": "PostOnly", "orderLinkId": "c1", "smpType": "CancelMaker"},
    ),
    (
        "okx",
        _okx,
        "place_order",
        [
            *OKX[:3],
            ("ordType", "post_only"),
            *OKX[4:],
            ("clOrdId", "c1"),
            ("stpMode", "cancel_maker"),
        ],
        {"clOrdId": "c1", "stpMode": "cancel_maker", "ordType": "post_only"},
    ),
    (
        "kraken-futures",
        _kraken,
        "place_futures_order",
        [*KRAKEN_FUTURES[:2], ("orderType", "fok"), *KRAKEN_FUTURES[3:], ("reduceOnly", "true")],
        {"orderType": "fok", "reduceOnly": "true"},
    ),
    (
        "mexc-contract",
        _mexc,
        "place_contract_order",
        [*MEXC, ("reduceOnly", "true")],
        {"reduceOnly": True},
    ),
]

INVALID = [
    (
        "binance-spot-gtx",
        _binance,
        "place_order",
        [*BINANCE_SPOT, ("type_", "LIMIT"), ("price", "100"), ("timeInForce", "GTX")],
    ),
    (
        "binance-spot-reduce",
        _binance,
        "place_order",
        [*BINANCE_SPOT, ("type_", "MARKET"), ("reduceOnly", "true")],
    ),
    (
        "binance-usdm-reduce",
        _binance,
        "place_order",
        [*BINANCE_SWAP, ("type_", "MARKET"), ("reduceOnly", "yes")],
    ),
    (
        "binance-post-only-spot",
        _binance,
        "place_post_only_limit_order",
        [*BINANCE_SPOT, ("price", "100"), ("positionSide", "LONG")],
    ),
    (
        "bitget-batch-spot-reduce",
        _bitget,
        "place_uta_batch_orders",
        [
            (
                "orderList",
                json.dumps([{**dict(BITGET_SPOT[1:]), "symbol": "BTCUSDT", "reduceOnly": "yes"}]),
            )
        ],
    ),
    (
        "bitget-auto-borrow-futures",
        _bitget,
        "place_uta_order",
        [*BITGET_SWAP, ("autoBorrow", "yes")],
    ),
    (
        "bybit-batch-tif",
        _bybit,
        "place_batch_order",
        [
            ("category", "linear"),
            (
                "request",
                json.dumps([{**dict(BYBIT[1:]), "symbol": "BTCUSDT", "timeInForce": "GTX"}]),
            ),
        ],
    ),
    (
        "bybit-amend-batch-unknown",
        _bybit,
        "amend_batch_order",
        [
            ("category", "linear"),
            ("request", json.dumps([{"symbol": "BTCUSDT", "orderId": "1", "side": "Buy"}])),
        ],
    ),
    (
        "bybit-amend-unknown",
        _bybit,
        "amend_order",
        [("product_symbol", "BTC-USDT-SWAP"), ("orderId", "1"), ("timeInForce", "IOC")],
    ),
    (
        "okx-batch-unknown",
        _okx,
        "place_batch_orders",
        [
            (
                "orders",
                json.dumps([{**dict(OKX[1:]), "instId": "BTC-USDT-SWAP", "timeInForce": "GTC"}]),
            )
        ],
    ),
    (
        "okx-amend-unknown",
        _okx,
        "amend_order",
        [
            ("product_symbol", "BTC-USDT-SWAP"),
            ("ordId", "1"),
            ("newSz", "2"),
            ("newOrdType", "ioc"),
        ],
    ),
    ("bitget-unknown", _bitget, "place_uta_order", [*BITGET_SWAP, ("presetStopLossPrice", "1")]),
    ("bitget-tif", _bitget, "place_uta_order", [*BITGET_SWAP, ("timeInForce", "GTC")]),
    ("bitget-spot-reduce", _bitget, "place_uta_order", [*BITGET_SPOT, ("reduceOnly", "yes")]),
    ("bybit-unknown", _bybit, "place_order", [*BYBIT, ("clientOrderId", "c1")]),
    ("bybit-tif", _bybit, "place_order", [*BYBIT, ("timeInForce", "GTX")]),
    (
        "bybit-post-only-conflict",
        _bybit,
        "place_post_only_limit_order",
        [*BYBIT[:1], *BYBIT[1:2], *BYBIT[3:], ("timeInForce", "IOC")],
    ),
    ("okx-unknown", _okx, "place_order", [*OKX, ("timeInForce", "GTC")]),
    ("okx-ordtype", _okx, "place_order", [*OKX[:3], ("ordType", "gtc"), *OKX[4:]]),
    ("kraken-unknown", _kraken, "place_futures_order", [*KRAKEN_FUTURES, ("postOnly", "true")]),
    ("kraken-reduce", _kraken, "place_futures_order", [*KRAKEN_FUTURES, ("reduceOnly", "yes")]),
    ("mexc-reduce", _mexc, "place_contract_order", [*MEXC, ("reduceOnly", "yes")]),
    (
        "backpack-spot-reduce",
        _backpack,
        "place_market_order",
        [*BACKPACK_SPOT, ("reduceOnly", "true")],
    ),
]


@pytest.mark.parametrize(
    ("name", "factory", "method", "params", "expected"), VALID, ids=[c[0] for c in VALID]
)
def test_documented_order_flags_reach_the_wire(
    name: str, factory: Any, method: str, params: list[tuple[str, str]], expected: dict[str, Any]
) -> None:
    del name
    with _http_server() as (base, received):
        client = factory(base)
        try:
            client.private_request_json(method, params)
        except Exception:  # noqa: BLE001, S110 - response shape is irrelevant; the wire is checked.
            pass
        requests = _order_requests(received)
    assert len(requests) == 1, requests
    fields = _fields(requests[0])
    for key, value in expected.items():
        assert fields.get(key) == value, (key, fields)


@pytest.mark.parametrize(
    ("name", "factory", "method", "params"), INVALID, ids=[c[0] for c in INVALID]
)
def test_unsupported_order_flags_fail_before_any_request(
    name: str, factory: Any, method: str, params: list[tuple[str, str]]
) -> None:
    del name
    with _http_server() as (base, received):
        client = factory(base)
        with pytest.raises(ValueError):
            client.private_request_json(method, params)
        assert _order_requests(received) == []


def test_bitget_python_wrapper_sends_auto_borrow_and_px_amend_type() -> None:
    from dcex.bitget.client import Client

    with _http_server({"code": "00000", "data": {}}) as (base, received):
        client = Client(
            api_key="key", api_secret="secret", passphrase="pass", preload_product_table=False
        )
        client._native_client = _bitget(base)
        client.place_uta_order(
            category="SPOT",
            product_symbol="BTC-USDT-SPOT",
            side="buy",
            order_type="limit",
            qty="1",
            price="100",
            auto_borrow="no",
            px_amend_type="yes",
        )
        fields = _fields(_order_requests(received)[0])
    assert fields["autoBorrow"] == "no"
    assert fields["pxAmendType"] == "yes"
