"""Regression coverage for the current Hyperliquid REST parameter surface."""

# ruff: noqa: D103

from __future__ import annotations

import inspect
import json

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _wire_async,
    _wire_sync,
)
from tests.unit.native_http_helpers import _http_server

CURRENT_FIELDS = {
    "get_meta_and_asset_ctxs": {"dex"},
    "get_l2book": {"product_symbol", "nSigFigs", "mantissa"},
    "get_candle_snapshot": {"product_symbol", "interval", "startTime", "endTime"},
    "place_future_market_order": {
        "product_symbol",
        "isBuy",
        "size",
        "reduceOnly",
        "slippage",
        "cloid",
        "builder_address",
        "fee_ten_bp",
        "vaultAddress",
        "expiresAfter",
    },
    "place_future_limit_order": {
        "product_symbol",
        "isBuy",
        "price",
        "size",
        "tif",
        "cloid",
        "builder_address",
        "fee_ten_bp",
        "vaultAddress",
        "expiresAfter",
    },
}


@pytest.mark.parametrize(("method_name", "expected"), CURRENT_FIELDS.items())
def test_hyperliquid_sync_and_async_expose_current_official_fields(
    method_name: str, expected: set[str]
) -> None:
    sync_client = _client_class("sync", "hyperliquid")
    async_client = _client_class("async", "hyperliquid")
    sync_fields = set(inspect.signature(getattr(sync_client, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(async_client, method_name)).parameters)

    assert expected <= sync_fields
    assert sync_fields == async_fields


def test_hyperliquid_candle_end_time_is_required() -> None:
    parameter = inspect.signature(
        _client_class("sync", "hyperliquid").get_candle_snapshot
    ).parameters["endTime"]

    assert parameter.default is inspect.Parameter.empty


def test_sync_hyperliquid_forwards_current_fields() -> None:
    client = _client_class("sync", "hyperliquid")(**_client_kwargs("hyperliquid"))
    calls = _wire_sync(client)

    client.get_meta_and_asset_ctxs(dex="xyz")
    client.get_l2book("BTC-USD-SWAP", nSigFigs=5, mantissa=2)
    client.place_future_market_buy_order(
        "BTC-USD-SWAP",
        "0.001",
        slippage=0.01,
        reduceOnly=True,
        cloid="0x1234567890abcdef1234567890abcdef",
    )

    assert dict(calls[0]["query"]) == {"dex": "xyz"}
    assert dict(calls[1]["query"])["nSigFigs"] == "5"
    assert dict(calls[1]["query"])["mantissa"] == "2"
    assert dict(calls[2]["query"])["slippage"] == "0.01"
    assert dict(calls[2]["query"])["reduceOnly"] == "true"


@pytest.mark.asyncio
async def test_async_hyperliquid_forwards_current_fields() -> None:
    client = _client_class("async", "hyperliquid")(**_client_kwargs("hyperliquid"))
    calls = _wire_async(client)

    await client.get_candle_snapshot("BTC-USD-SWAP", "1m", 1_000, 2_000)
    await client.place_future_limit_buy_order(
        "BTC-USD-SWAP",
        "100000",
        "0.001",
        "Alo",
        vaultAddress="0x0000000000000000000000000000000000000002",
    )

    assert dict(calls[0]["query"])["endTime"] == "2000"
    assert dict(calls[1]["query"])["vaultAddress"].endswith("2")


def _native_client(base_url: str, *, private: bool = False) -> object:
    native = pytest.importorskip("dcex._native")
    kwargs = {"timeout": 2, "endpoint": base_url}
    if private:
        kwargs.update(
            wallet_address="0x" + "22" * 20,
            private_key="0x" + "11" * 32,
        )
    return native.HyperliquidHttpClient(**kwargs)


def test_native_hyperliquid_current_info_payloads_match_docs() -> None:
    responses = [
        [{"universe": []}, []],
        {"coin": "BTC", "levels": [[], []], "time": 1},
        [],
        {"userCrossRate": "0.00035"},
    ]
    with _http_server(responses) as (base_url, received):
        client = _native_client(base_url)
        client.public_request_json("get_meta_and_asset_ctxs", [("dex", "xyz")])
        client.public_request_json(
            "get_l2book",
            [("product_symbol", "BTC"), ("nSigFigs", "5"), ("mantissa", "2")],
        )
        client.public_request_json(
            "get_candle_snapshot",
            [
                ("product_symbol", "BTC"),
                ("interval", "1m"),
                ("startTime", "1000"),
                ("endTime", "2000"),
            ],
        )
        client.public_request_json(
            "get_futures_fee_rates",
            [("user", "0x" + "AA" * 20)],
        )

    payloads = [json.loads(received.get_nowait()["body"]) for _ in responses]
    assert payloads == [
        {"type": "metaAndAssetCtxs", "dex": "xyz"},
        {"type": "l2Book", "coin": "BTC", "nSigFigs": 5, "mantissa": 2},
        {
            "type": "candleSnapshot",
            "req": {
                "coin": "BTC",
                "interval": "1m",
                "startTime": 1000,
                "endTime": 2000,
            },
        },
        {"type": "userFees", "user": "0x" + "aa" * 20},
    ]


def test_native_hyperliquid_schedule_cancel_omits_absent_time() -> None:
    with _http_server({"status": "ok"}) as (base_url, received):
        client = _native_client(base_url, private=True)
        client.private_request_json("schedule_cancel", [])

    payload = json.loads(received.get_nowait()["body"])
    assert payload["action"] == {"type": "scheduleCancel"}


def test_native_hyperliquid_normalizes_signed_addresses() -> None:
    with _http_server({"status": "ok"}) as (base_url, received):
        client = _native_client(base_url, private=True)
        client.private_request_json(
            "place_order",
            [
                ("product_symbol", "BTC-USD-SWAP"),
                ("isBuy", "true"),
                ("price", "100000"),
                ("size", "0.001"),
                ("reduceOnly", "false"),
                ("tif", "Gtc"),
                ("builder_address", "0x" + "AA" * 20),
                ("fee_ten_bp", "10"),
                ("vaultAddress", "0x" + "BB" * 20),
            ],
        )

    payload = json.loads(received.get_nowait()["body"])
    assert payload["action"]["builder"]["b"] == "0x" + "aa" * 20
    assert payload["vaultAddress"] == "0x" + "bb" * 20


@pytest.mark.parametrize(
    ("method_name", "params", "message"),
    [
        (
            "get_candle_snapshot",
            [("product_symbol", "BTC"), ("interval", "1m"), ("startTime", "1000")],
            "endTime",
        ),
        (
            "get_l2book",
            [("product_symbol", "BTC"), ("nSigFigs", "4"), ("mantissa", "2")],
            "mantissa",
        ),
        (
            "get_futures_fee_rates",
            [("user", "not-an-address")],
            "20-byte address",
        ),
        (
            "place_order",
            [
                ("product_symbol", "ETH-USD-SWAP"),
                ("isBuy", "true"),
                ("price", "100"),
                ("size", "1"),
                ("reduceOnly", "false"),
                ("tif", "Gtc"),
            ],
            "cannot safely resolve",
        ),
        (
            "place_order",
            [
                ("product_symbol", "BTC-USD-SWAP"),
                ("isBuy", "true"),
                ("price", "100"),
                ("size", "1"),
                ("reduceOnly", "false"),
                ("tif", "DAY"),
            ],
            "tif",
        ),
    ],
)
def test_native_hyperliquid_rejects_invalid_current_parameters_before_transport(
    method_name: str,
    params: list[tuple[str, str]],
    message: str,
) -> None:
    client = _native_client("http://127.0.0.1:1", private=method_name == "place_order")
    request = (
        client.private_request_json
        if method_name == "place_order"
        else client.public_request_json
    )

    with pytest.raises(ValueError, match=message):
        request(method_name, params)


def test_native_hyperliquid_normalizes_batch_modify_wire_order() -> None:
    modifies = [
        {
            "order": {
                "t": {"limit": {"tif": "Gtc"}},
                "r": False,
                "s": "0.001",
                "p": "100000",
                "b": True,
                "a": 0,
            },
            "oid": 42,
        }
    ]
    with _http_server({"status": "ok"}) as (base_url, received):
        client = _native_client(base_url, private=True)
        client.private_request_json(
            "modify_batch_orders",
            [("modifies", json.dumps(modifies, separators=(",", ":")))],
        )

    payload = json.loads(received.get_nowait()["body"])
    assert payload["action"]["modifies"] == [
        {
            "oid": 42,
            "order": {
                "a": 0,
                "b": True,
                "p": "100000",
                "s": "0.001",
                "r": False,
                "t": {"limit": {"tif": "Gtc"}},
            },
        }
    ]
