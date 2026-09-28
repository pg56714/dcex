# ruff: noqa: D103
"""
Offline wire coverage for every Arcus Perps sync and async wrapper.

``dcex/arcus/client.py`` does not match the shared ``ENDPOINT_FILE_SUFFIXES``
list, so the generic endpoint suite never exercises Arcus.  These tests drive
each Perps wrapper through the real Rust client against a local HTTP server and
assert the documented Arcus route (https://docs.arcus.xyz/api-reference) and
key fields arrive on the wire, and that trading calls carry the Ed25519
``X-API-Key`` / ``X-Timestamp`` / ``X-Signature`` headers.
"""

from __future__ import annotations

import json
import queue
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.wire_expectations import EXPECTED_VERBS as _ALL_VERBS

EXPECTED_VERBS = _ALL_VERBS["arcus"]

from dcex.arcus.client import Client
from dcex.async_support.arcus.client import Client as AsyncClient
from dcex.utils.errors import FailedRequestError
from tests.unit.native_http_helpers import _http_server

SECRET = "05" * 32
ADDRESS = "0x" + "44" * 20
MARKETS: dict[str, Any] = {
    "markets": [
        {
            "marketId": 7,
            "marketDisplayName": "BTC-USD",
            "tickSize": "0.1",
            "stepSize": "0.001",
            "minOrderSize": "0.001",
            "maxOrderSize": "100",
            "minOrderNotional": "1",
        }
    ]
}
ACCOUNT = {"address": ADDRESS, "accountIndex": "0"}


def _good_til() -> int:
    return int(time.time() * 1_000_000) + 40 * 86_400 * 1_000_000


@dataclass(frozen=True)
class WireCase:
    """One wrapper call and the final request it must produce."""

    method: str
    kwargs: dict[str, Any]
    http_method_path: str
    query: dict[str, str]
    body: dict[str, Any] | None = None
    signed: bool = False
    lookups: int = 0

    @property
    def id(self) -> str:
        """Return the pytest id for this case."""
        return self.method


def read(method: str, path: str, query: dict[str, str] | None = None, **kwargs: Any) -> WireCase:  # noqa: ANN401
    """Build a read-only GET case."""
    return WireCase(method, kwargs, path, query or {})


def signed(
    method: str,
    path: str,
    body: dict[str, Any],
    lookups: int = 1,
    **kwargs: Any,  # noqa: ANN401
) -> WireCase:
    """Build a signed POST case; ``body`` lists fields that must match."""
    return WireCase(method, kwargs, path, {"address": ADDRESS}, body, signed=True, lookups=lookups)


WALLET_KEY_BODY = {
    "address": ADDRESS,
    "publicKey": "33" * 32,
    "apiWalletName": "trade",
    "accountIndex": 255,
    "nonce": "nonce1",
    "signature": {"r": "11" * 32, "s": "22" * 32, "v": "1b"},
}

CASES = [
    read(
        "get_leaderboard",
        "/v1/leaderboard",
        {"window": "30d", "sortBy": "pnl", "limit": "10"},
        window="30d",
        sort_by="pnl",
        limit=10,
    ),
    read("get_market_metadata", "/v1/api-meta/markets", {"market": "BTC-USD"}, market="BTC-USD"),
    read("get_market_overview", "/v1/api-meta/overview"),
    read("get_spot_market_overview", "/v1/api-meta/spot/overview"),
    read(
        "get_metadata_candles",
        "/v1/api-meta/candles",
        {"market": "BTC-USD", "timeframe": "1m", "to": "1700000060", "countback": "10"},
        market="BTC-USD",
        timeframe="1m",
        to=1700000060,
        countback=10,
    ),
    read("get_user_preferences", "/v1/api-meta/userPreferences", {"address": ADDRESS}),
    WireCase(
        "upsert_user_preferences",
        {"preferences": {"colorTheme": "dark", "favoritePerpMarkets": ["BTC-USD"]}},
        "/v1/api-meta/userPreferences",
        {},
        {"colorTheme": "dark", "favoritePerpMarkets": ["BTC-USD"]},
        signed=True,
    ),
    WireCase(
        "delete_user_preference_signed",
        {"key": "colorTheme", "timestamp": 1700000000000000000, "signature": "11" * 64},
        "/v1/api-meta/userPreferences",
        {"key": "colorTheme"},
        signed=True,
    ),
    read("get_api_keys", "/v1/apiKeys", {"address": ADDRESS}),
    read("get_api_keys", "/v1/apiKeys", {"address": ADDRESS, "accountIndex": "2"}, account_index=2),
    WireCase(
        "create_api_key_signed", {"body": WALLET_KEY_BODY}, "/v1/createApiKey", {}, WALLET_KEY_BODY
    ),
    WireCase(
        "revoke_api_key_signed", {"body": WALLET_KEY_BODY}, "/v1/revokeApiKey", {}, WALLET_KEY_BODY
    ),
    read("get_markets", "/v1/markets"),
    read("get_spot_assets", "/v1/spotAssets"),
    read("get_fee_tiers", "/v1/feetiers"),
    read("get_bbo", "/v1/bbo/BTC-USD", market="BTC-USD"),
    read(
        "get_l2_orderbook", "/v1/l2OrderBook/ETH-USD", {"nLevels": "5"}, market="ETH-USD", depth=5
    ),
    read("get_account", "/v1/account", ACCOUNT),
    read("get_positions", "/v1/positions", ACCOUNT),
    read("get_open_orders", "/v1/openOrders", ACCOUNT),
    read("get_order_status", "/v1/order/ord-1", ACCOUNT, order_id="ord-1"),
    read("get_fills", "/v1/fills", ACCOUNT),
    read("get_transfer_updates", "/v1/accountTransferUpdates", ACCOUNT),
    read("get_leverages", "/v1/leverages", ACCOUNT),
    signed(
        "place_order",
        "/v1/placeOrder",
        {
            "marketId": 7,
            "orderSide": "BUY",
            "orderType": "LIMIT",
            "price": "100",
            "quantity": "0.01",
        },
        product_symbol="BTC-USD-SWAP",
        side="BUY",
        price="100",
        quantity="0.01",
    ),
    signed(
        "cancel_order",
        "/v1/cancelOrder",
        {"marketId": 7, "kind": "orderId", "orderId": "ord-1"},
        product_symbol="BTC-USD",
        order_id="ord-1",
    ),
    signed(
        "cancel_all_orders",
        "/v1/cancelAllOrders",
        {"marketId": 7},
        product_symbol="BTC-USD",
    ),
    signed(
        "disarm_scheduled_cancel",
        "/v1/scheduleCancel",
        {"accountIndex": 0},
        lookups=0,
    ),
    signed(
        "adjust_isolated_margin",
        "/v1/adjustIsolatedMargin",
        {"marketId": 7, "amount": "-5"},
        product_symbol="BTC-USD",
        amount="-5",
    ),
    signed(
        "set_leverage",
        "/v1/setLeverage",
        {"marketId": 7, "leverage": 5, "isolated": False},
        product_symbol="BTC-USD",
        leverage=5,
        isolated=False,
    ),
    signed(
        "batch_place_orders",
        "/v1/batchPlaceOrders",
        {},
        orders=[{"product_symbol": "BTC-USD", "side": "SELL", "price": "200", "quantity": "0.01"}],
    ),
    signed(
        "batch_cancel_orders",
        "/v1/batchCancelOrders",
        {},
        cancels=[{"product_symbol": "BTC-USD", "order_id": "ord-2"}],
    ),
]

TRANSFER = {
    "ethereumAddress": ADDRESS,
    "fromAccountIndex": 0,
    "toAccountIndex": 1,
    "amount": "1000000",
    "nonce": "1718644999000",
    "signature": {"r": "0x" + "ab" * 32, "s": "0x" + "cd" * 32, "v": "0x1b"},
}


CASES.extend(
    [
        read(
            "get_trade",
            "/v1/trade/123",
            {"market": "BTC-USD"},
            **{"trade_id": "123", "market": "BTC-USD"},
        ),
        read(
            "get_account_stats",
            "/v1/account/stats",
            {"address": ADDRESS, "include": "feeTier,volumes", "windows": "24h,7d"},
            **{"include": ["feeTier", "volumes"], "windows": ["24h", "7d"]},
        ),
        read("get_mid_prices", "/v1/mids", {"market": "BTC-USD"}, **{"market": "BTC-USD"}),
        read("get_compliance", "/v1/compliance", {"address": ADDRESS}, **{}),
        read("get_rate_limit", "/v1/rateLimit", {"address": ADDRESS, "accountIndex": "0"}, **{}),
        read("get_time", "/v1/time", {}, **{}),
        read(
            "get_fill",
            "/v1/fill/123",
            {"address": ADDRESS, "accountIndex": "0"},
            **{"trade_id": "123"},
        ),
        read(
            "get_funding",
            "/v1/funding",
            {
                "address": ADDRESS,
                "accountIndex": "0",
                "market": "BTC-USD",
                "from": "1700000000000000",
                "to": "1700000060000000",
                "limit": "20",
            },
            **{
                "market": "BTC-USD",
                "start_time": 1700000000000000,
                "end_time": 1700000060000000,
                "limit": 20,
            },
        ),
        read(
            "get_interest",
            "/v1/interest",
            {
                "address": ADDRESS,
                "accountIndex": "0",
                "from": "1700000000000000",
                "to": "1700000060000000",
                "limit": "20",
            },
            **{"start_time": 1700000000000000, "end_time": 1700000060000000, "limit": 20},
        ),
        read("get_live_prices", "/v1/prices", {"market": "BTC-USD"}, **{"market": "BTC-USD"}),
        read(
            "get_funding_rates",
            "/v1/fundingRates",
            {
                "market": "BTC-USD",
                "from": "1700000000000000",
                "to": "1700000060000000",
                "limit": "20",
            },
            **{
                "market": "BTC-USD",
                "start_time": 1700000000000000,
                "end_time": 1700000060000000,
                "limit": 20,
            },
        ),
        read(
            "get_candles",
            "/v1/candles",
            {"market": "BTC-USD", "timeframe": "1m", "to": "1700000060000000", "countback": "20"},
            **{
                "market": "BTC-USD",
                "timeframe": "1m",
                "end_time": 1700000060000000,
                "countback": 20,
            },
        ),
        read(
            "get_order_history",
            "/v1/orders",
            {
                "address": ADDRESS,
                "accountIndex": "0",
                "market": "BTC-USD",
                "side": "BUY",
                "status": "OPEN,UNTRIGGERED",
                "limit": "20",
                "from": "1700000000000000",
                "to": "1700000060000000",
            },
            **{
                "market": "BTC-USD",
                "side": "BUY",
                "status": ["OPEN", "UNTRIGGERED"],
                "limit": 20,
                "start_time": 1700000000000000,
                "end_time": 1700000060000000,
            },
        ),
        read(
            "get_portfolio_history",
            "/v1/portfolio",
            {"address": ADDRESS, "accountIndex": "0"},
            **{},
        ),
        read(
            "get_trades",
            "/v1/trades",
            {
                "market": "BTC-USD",
                "limit": "20",
                "from": "1700000000000000",
                "to": "1700000060000000",
            },
            **{
                "market": "BTC-USD",
                "limit": 20,
                "start_time": 1700000000000000,
                "end_time": 1700000060000000,
            },
        ),
        read(
            "get_spot_fills",
            "/v1/spotFills",
            {
                "address": ADDRESS,
                "accountIndex": "0",
                "limit": "20",
                "from": "1700000000000000",
                "to": "1700000060000000",
            },
            **{"limit": 20, "start_time": 1700000000000000, "end_time": 1700000060000000},
        ),
        read(
            "get_spot_positions",
            "/v1/spotPositions",
            {"address": ADDRESS, "accountIndex": "0"},
            **{},
        ),
        read("health", "/health", {}, **{}),
        read("get_service_info", "/", {}, **{}),
    ]
)


COMPLETION_CASES = json.loads(
    (Path(__file__).parents[1] / "fixtures/arcus_request_cases.json").read_text(encoding="utf-8")
)
CASES.extend(
    WireCase(
        c["method"],
        c["kwargs"],
        c["path"],
        {k: str(v) for k, v in c["query"].items()},
        c["body"],
        c["signed"],
    )
    for c in COMPLETION_CASES
)


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {"api_secret": SECRET, "address": ADDRESS, "base_url": base_url}


@pytest.fixture(scope="module")
def server() -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    """Share one recording server across the module to keep the suite fast."""
    with _http_server(MARKETS) as (base_url, received):
        yield base_url, received


@pytest.fixture(autouse=True)
def _no_env_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("ARCUS_API_KEY", "ARCUS_API_SIGNING_KEY", "ARCUS_ADDRESS"):
        monkeypatch.delenv(name, raising=False)


def _drain(received: queue.Queue[dict[str, Any]]) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    while not received.empty():
        requests.append(received.get_nowait())
    return requests


def _assert_wire(wire: WireCase, requests: list[dict[str, Any]]) -> dict[str, Any]:
    paths = [urlsplit(request["path"]).path for request in requests]
    assert paths[: wire.lookups] == ["/v1/markets"] * wire.lookups, paths
    assert len(requests) == wire.lookups + 1, paths
    assert all(request["method"] == "GET" for request in requests[: wire.lookups])
    final = requests[-1]
    assert final["method"] == EXPECTED_VERBS[wire.method]
    target = urlsplit(final["path"])
    assert target.path == wire.http_method_path
    query = dict(parse_qsl(target.query))
    for key, value in wire.query.items():
        assert query.get(key) == value, (key, query)
    completion = next((c for c in COMPLETION_CASES if c["method"] == wire.method), None)
    if completion is not None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        assert final["method"] == completion["http_method"]
        assert query == wire.query
        sent = json.loads(final["body"]) if wire.body is not None else None
        assert sent == wire.body
        if wire.signed:
            timestamp = final["x-timestamp"]
            action = target.path.rsplit("/", 1)[-1]
            if wire.method == "create_withdrawal":
                typed = {
                    "ad": ADDRESS,
                    "ai": 0,
                    "ct": int(timestamp),
                    "n": wire.body["nonce"],
                    "op": 5,
                    "q": int(wire.body["amount"]),
                    "v": 1,
                }
                message = json.dumps(typed, sort_keys=True, separators=(",", ":")).encode()
            elif sent is None:
                message = (timestamp + action).encode()
            else:
                message = (
                    timestamp + action + json.dumps(sent, sort_keys=True, separators=(",", ":"))
                ).encode()
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(final["x-api-key"])).verify(
                bytes.fromhex(final["x-signature"]), message
            )
        else:
            assert not final.get("x-api-key")
            assert not final.get("x-signature")
        return sent or {}
    if wire.method in {"get_api_keys", "create_api_key_signed", "revoke_api_key_signed"}:
        assert not final.get("x-api-key")
        assert not final.get("x-signature")
        assert query == wire.query
        if wire.body is not None:
            assert json.loads(final["body"]) == wire.body
            return wire.body
        assert final["body"] == ""
        return {}
    if wire.http_method_path.startswith("/v1/api-meta/"):
        assert query == wire.query
        if wire.method == "upsert_user_preferences":
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

            assert final["method"] == "PATCH"
            sent = json.loads(final["body"])
            assert sent == wire.body
            message = (
                final["x-timestamp"]
                + "userPreferences"
                + json.dumps(sent, sort_keys=True, separators=(",", ":"))
            ).encode()
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(final["x-api-key"])).verify(
                bytes.fromhex(final["x-signature"]), message
            )
            return sent
        if wire.method == "delete_user_preference_signed":
            assert final["method"] == "DELETE"
            assert final["x-signature"] == "11" * 64
            assert final["x-timestamp"] == "1700000000000000000"
            assert final["body"] == ""
            return {}
        assert final["method"] == "GET"
        assert final["body"] == ""
        assert not final.get("x-signature")
        return {}
    assert final.get("x-api-key")
    if wire.signed:
        assert len(final["x-signature"]) == 128
        assert final["x-timestamp"].isdigit()
        sent = json.loads(final["body"])
        items = next(
            (sent[key] for key in ("orders", "cancels", "modifies") if key in sent), [sent]
        )
        assert all(item["address"] == ADDRESS for item in items)
        for key, value in (wire.body or {}).items():
            assert sent[key] == value, (key, sent)
        return sent
    assert final["body"] == ""
    return {}


def test_every_perps_wrapper_has_a_wire_case() -> None:
    wrappers = {
        name for name, value in vars(Client).items() if not name.startswith("_") and callable(value)
    }
    extra = {"schedule_cancel", "modify_order", "batch_modify_orders", "submit_internal_transfer"}
    generic = {"sign_websocket_request", "public_request", "private_request", "close"}
    assert wrappers - generic - extra - {wire.method for wire in CASES} == set()


@pytest.mark.parametrize("wire", CASES, ids=[wire.id for wire in CASES])
def test_sync_wrapper_reaches_documented_route(
    wire: WireCase, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    try:
        assert getattr(client, wire.method)(**wire.kwargs) == MARKETS
    finally:
        client.close()
    sent = _assert_wire(wire, _drain(received))
    if wire.method.startswith("batch_"):
        key = "orders" if "place" in wire.method else "cancels"
        assert all(len(item["signature"]) == 128 for item in sent[key])


@pytest.mark.asyncio
@pytest.mark.parametrize("wire", CASES, ids=[wire.id for wire in CASES])
async def test_async_wrapper_reaches_documented_route(
    wire: WireCase, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    base_url, received = server
    _drain(received)
    client = await AsyncClient(**_client_kwargs(base_url)).async_init()
    try:
        assert await getattr(client, wire.method)(**wire.kwargs) == MARKETS
    finally:
        await client.close()
    _assert_wire(wire, _drain(received))


def _time_sensitive_cases() -> list[tuple[str, dict[str, Any], WireCase]]:
    deadline = int(time.time() * 1_000_000) + 60_000_000
    good_til = _good_til()
    modify = {
        "product_symbol": "BTC-USD",
        "side": "SELL",
        "price": "101",
        "quantity": "0.02",
        "good_til_time": good_til,
        "time_in_force": "GTT",
        "reduce_only": False,
    }
    return [
        (
            "schedule_cancel",
            {"time": deadline},
            signed("schedule_cancel", "/v1/scheduleCancel", {"time": deadline}, lookups=0),
        ),
        (
            "modify_order",
            {**modify, "order_id": "ord-3"},
            signed("modify_order", "/v1/modifyOrder", {"orderId": "ord-3", "side": "SELL"}),
        ),
        (
            "batch_modify_orders",
            {"modifies": [{**modify, "order_id": "ord-4"}]},
            signed("batch_modify_orders", "/v1/batchModifyOrders", {}),
        ),
    ]


def test_sync_time_sensitive_wrappers(server: tuple[str, queue.Queue[dict[str, Any]]]) -> None:
    base_url, received = server
    client = Client(**_client_kwargs(base_url))
    try:
        for method, kwargs, wire in _time_sensitive_cases():
            _drain(received)
            assert getattr(client, method)(**kwargs) == MARKETS
            sent = _assert_wire(wire, _drain(received))
            if method == "batch_modify_orders":
                assert sent["modifies"][0]["orderId"] == "ord-4"
    finally:
        client.close()


@pytest.mark.asyncio
async def test_async_time_sensitive_wrappers(
    server: tuple[str, queue.Queue[dict[str, Any]]],
) -> None:
    base_url, received = server
    client = await AsyncClient(**_client_kwargs(base_url)).async_init()
    try:
        for method, kwargs, wire in _time_sensitive_cases():
            _drain(received)
            assert await getattr(client, method)(**kwargs) == MARKETS
            _assert_wire(wire, _drain(received))
    finally:
        await client.close()


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_internal_transfer_is_wallet_signed_without_api_headers(
    mode: str, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    import asyncio

    base_url, received = server
    _drain(received)
    if mode == "sync":
        client = Client(**_client_kwargs(base_url))
        client.submit_internal_transfer(TRANSFER)
        client.close()
    else:

        async def call() -> None:
            async_client = await AsyncClient(**_client_kwargs(base_url)).async_init()
            await async_client.submit_internal_transfer(TRANSFER)
            await async_client.close()

        asyncio.run(call())
    [request] = _drain(received)
    assert request["path"] == "/v1/transfer"
    assert "x-signature" not in request
    assert json.loads(request["body"]) == TRANSFER


def test_unsafe_orders_are_rejected_before_state_changes(
    server: tuple[str, queue.Queue[dict[str, Any]]],
) -> None:
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    errors = (ValueError, FailedRequestError)
    try:
        with pytest.raises(errors):
            client.place_order("BTC-USD", "BUY", "100", "0.01", order_type="MARKET")
        with pytest.raises(errors):
            client.place_order("BTC-USD", "BUY", "100.05", "0.01")
        with pytest.raises(errors):
            client.place_order("BTC-USD", "BUY", "100", "101")
        with pytest.raises(errors):
            client.set_leverage("BTC-USD", 0)
        with pytest.raises(errors):
            client.schedule_cancel(1)
        with pytest.raises(errors):
            client.batch_place_orders([])
    finally:
        client.close()
    paths = {urlsplit(request["path"]).path for request in _drain(received)}
    assert paths <= {"/v1/markets"}


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("grouping", ["partialTpsl", "positionTpsl", "entryTpsl"])
async def test_tpsl_grouping_preserves_zero_size_and_triggers(
    asynchronous: bool, grouping: str, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    import inspect

    base, received = server
    _drain(received)
    quantity = "0" if grouping == "positionTpsl" else "0.01"
    orders = [
        {
            "product_symbol": "BTC-USD",
            "side": "SELL",
            "price": "100",
            "quantity": quantity,
            "reduce_only": True,
            "tpsl_type": kind,
            "stop_price": stop,
        }
        for kind, stop in [("TAKE_PROFIT", "110"), ("STOP_LOSS", "90")]
    ]
    if grouping == "entryTpsl":
        orders.insert(
            0, {"product_symbol": "BTC-USD", "side": "BUY", "price": "100", "quantity": "0.01"}
        )
    client = AsyncClient(**_client_kwargs(base)) if asynchronous else Client(**_client_kwargs(base))
    try:
        if asynchronous:
            await client.async_init()
        result = client.batch_place_orders(orders, grouping=grouping)
        if inspect.isawaitable(result):
            await result
    finally:
        result = client.close()
        if inspect.isawaitable(result):
            await result
    requests = [request for request in _drain(received) if request["method"] == "POST"]
    assert len(requests) == 1
    payload = json.loads(requests[0]["body"])
    assert payload["grouping"] == grouping
    children = payload["orders"][1:] if grouping == "entryTpsl" else payload["orders"]
    assert [leg["tpslType"] for leg in children] == ["TAKE_PROFIT", "STOP_LOSS"]
    assert [leg["stopPrice"] for leg in children] == ["110", "90"]
    assert all(leg["quantity"] == quantity and leg["reduceOnly"] for leg in children)
    assert all(len(leg["signature"]) == 128 for leg in payload["orders"])
