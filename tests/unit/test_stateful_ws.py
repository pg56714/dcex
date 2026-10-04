"""Offline checks for the private-stream order lifecycle observer (fake WS clients only)."""

import asyncio
import json
from decimal import Decimal as D

import pytest

from tests.stateful_lifecycle import LifecycleError, Order, Rules, plan_order
from tests.stateful_ws import (
    CANCELLED,
    FILLED,
    OPEN,
    OrderStream,
    StreamEventMissing,
    StreamUnexpectedState,
    _ack,
    extract_events,
    matches,
    mexc_protobuf_events,
    verify_order_stream,
    write_ws_record,
    ws_record,
)

ORDER_ID = "123"
CLIENT_ID = "0abc"


class FakeWs:
    """Delivers queued payloads; `on_place`/`on_cancel` simulate exchange pushes."""

    def __init__(self):
        self.queue: asyncio.Queue[object] = asyncio.Queue()
        self.closed = False
        self.pings = 0

    async def recv(self):
        return await self.queue.get()

    async def ping(self):
        self.pings += 1

    async def close(self):
        self.closed = True

    def push(self, payload):
        self.queue.put_nowait(payload)


def bybit(order_id, client_id, status):
    return {
        "topic": "order",
        "data": [{"orderId": order_id, "orderLinkId": client_id, "orderStatus": status}],
    }


class FakeAdapter:
    def __init__(self, ws, *, on_place=(), on_cancel=()):
        self.ws = ws
        self.on_place = list(on_place)
        self.on_cancel = list(on_cancel)
        self.client_order_id = CLIENT_ID
        self.plan = plan_order("X", D(100), D(101), Rules(D(".1"), D(".01"), D(".01"), D(10)))
        self.cancelled = False
        self.cancels: list[str] = []
        self.calls: list[str] = []

    async def prepare(self):
        return self.plan, D(1000)

    async def book(self):
        return D(100), D(101)

    async def positions(self):
        return []

    async def open_orders(self):
        return []

    async def recover_order(self):
        return None

    async def place(self, plan):
        self.calls.append("place")
        for payload in self.on_place:
            self.ws.push(payload)
        return ORDER_ID

    async def order(self, identifier):
        state = "cancelled" if self.cancelled else "open"
        p = self.plan
        return Order(identifier, p.symbol, "buy", "limit", p.price, p.size, D(0), state)

    async def cancel(self, identifier):
        assert identifier == ORDER_ID
        self.calls.append("cancel")
        self.cancels.append(identifier)
        self.cancelled = True
        for payload in self.on_cancel:
            self.ws.push(payload)


async def run(adapter, ws, exchange="bybit", *, ack=None, timeout=0.2):
    stream = OrderStream(ws, exchange, ack=ack, heartbeat=None)
    result: dict[str, str] = {}
    try:
        await verify_order_stream(adapter, stream, result, timeout=timeout, poll_delay=0)
    finally:
        await stream.close()
    return result


@pytest.fixture(autouse=True)
def no_settle(monkeypatch):
    monkeypatch.setattr("tests.stateful_ws.PUSH_ONLY_SETTLE", 0)


@pytest.mark.asyncio
async def test_open_then_cancelled_matched_by_order_id_records_latency():
    ws = FakeWs()
    adapter = FakeAdapter(
        ws, on_place=[bybit(ORDER_ID, "", "New")], on_cancel=[bybit(ORDER_ID, "", "Cancelled")]
    )
    result = await run(adapter, ws)
    assert result["stage"] == "complete"
    assert result["case"] == "ws_order_stream"
    assert int(result["ws_open_latency_ms"]) >= 0
    assert int(result["ws_cancel_latency_ms"]) >= 0
    assert adapter.cancels == [ORDER_ID]
    assert ws.closed


@pytest.mark.asyncio
async def test_matched_by_client_id_only():
    ws = FakeWs()
    adapter = FakeAdapter(
        ws,
        on_place=[{"e": "executionReport", "i": "", "c": CLIENT_ID, "X": "NEW"}],
        on_cancel=[{"e": "executionReport", "c": "other", "C": CLIENT_ID, "X": "CANCELED"}],
    )
    result = await run(adapter, ws, "binance")
    assert result["stage"] == "complete"


@pytest.mark.asyncio
async def test_missing_open_event_fails_but_rest_cleanup_still_cancels():
    ws = FakeWs()
    adapter = FakeAdapter(ws, on_cancel=[bybit(ORDER_ID, CLIENT_ID, "Cancelled")])
    with pytest.raises(LifecycleError, match="no 'open' order-update event"):
        await run(adapter, ws)
    # The stream check refused to cancel; run_lifecycle's finally cancelled our order.
    assert adapter.cancels == [ORDER_ID]
    assert ws.closed


@pytest.mark.asyncio
async def test_unrelated_orders_are_ignored():
    ws = FakeWs()
    noise = [bybit("999", "someone-else", "New"), bybit("999", "someone-else", "Filled")]
    adapter = FakeAdapter(ws, on_place=noise, on_cancel=[bybit("999", "x", "Cancelled")])
    with pytest.raises(LifecycleError, match="no 'open'"):
        await run(adapter, ws)
    assert adapter.cancels == [ORDER_ID]


@pytest.mark.asyncio
async def test_missing_cancel_event_fails_after_rest_cancellation():
    ws = FakeWs()
    adapter = FakeAdapter(ws, on_place=[bybit(ORDER_ID, CLIENT_ID, "New")])
    with pytest.raises(StreamEventMissing, match="'cancelled'"):
        await run(adapter, ws)
    assert adapter.cancels == [ORDER_ID]


@pytest.mark.asyncio
async def test_fill_reported_on_stream_is_an_unexpected_fill():
    ws = FakeWs()
    adapter = FakeAdapter(ws, on_place=[bybit(ORDER_ID, CLIENT_ID, "PartiallyFilled")])
    with pytest.raises(LifecycleError, match="UNEXPECTED FILL"):
        await run(adapter, ws)
    assert adapter.cancels == [ORDER_ID]


@pytest.mark.asyncio
async def test_no_order_is_placed_without_subscription_confirmation():
    ws = FakeWs()
    adapter = FakeAdapter(ws)
    with pytest.raises(StreamEventMissing, match="no subscription confirmation"):
        await run(adapter, ws, ack=_ack("bybit", "linear"))
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_rejected_subscription_places_nothing():
    ws = FakeWs()
    ws.push({"op": "subscribe", "success": False, "ret_msg": "denied"})
    adapter = FakeAdapter(ws)
    with pytest.raises(LifecycleError, match="subscription rejected"):
        await run(adapter, ws, ack=_ack("bybit", "linear"))
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_confirmed_subscription_then_lifecycle():
    ws = FakeWs()
    ws.push({"op": "subscribe", "success": True})
    adapter = FakeAdapter(
        ws,
        on_place=[bybit(ORDER_ID, CLIENT_ID, "New")],
        on_cancel=[bybit(ORDER_ID, CLIENT_ID, "Cancelled")],
    )
    result = await run(adapter, ws, ack=_ack("bybit", "linear"))
    assert result["stage"] == "complete"


@pytest.mark.asyncio
async def test_stream_closed_fails_clearly():
    class ClosingWs(FakeWs):
        async def recv(self):
            raise RuntimeError("connection closed")

    ws = ClosingWs()
    adapter = FakeAdapter(ws)
    with pytest.raises(LifecycleError, match="closed"):
        await run(adapter, ws)
    assert adapter.calls == []


@pytest.mark.parametrize(
    "exchange,payload,state",
    [
        (
            "okx",
            {
                "arg": {"channel": "orders"},
                "data": [{"ordId": "1", "clOrdId": "c", "state": "live"}],
            },
            OPEN,
        ),
        (
            "bitget",
            {"data": [{"orderId": "1", "clientOid": "c", "orderStatus": "cancelled"}]},
            CANCELLED,
        ),
        ("binance", {"e": "ORDER_TRADE_UPDATE", "o": {"i": 1, "c": "c", "X": "NEW"}}, OPEN),
        (
            "binance",
            {
                "subscriptionId": 0,
                "event": {"e": "executionReport", "i": 1, "c": "c", "X": "CANCELED"},
            },
            CANCELLED,
        ),
        (
            "bingx",
            {"dataType": "spot.executionReport", "data": {"i": 1, "c": "c", "X": "NEW"}},
            OPEN,
        ),
        (
            "mexc",
            {
                "channel": "push.personal.order",
                "data": {"orderId": "1", "externalOid": "c", "state": 4},
            },
            CANCELLED,
        ),
        (
            "kucoin",
            {
                "type": "message",
                "data": {"orderId": "1", "clientOid": "c", "type": "open", "status": "open"},
            },
            OPEN,
        ),
        (
            "kucoin",
            {
                "type": "message",
                "data": {"orderId": "1", "clientOid": "c", "type": "canceled", "status": "done"},
            },
            CANCELLED,
        ),
        (
            "kraken",
            {
                "channel": "executions",
                "data": [{"order_id": "1", "cl_ord_id": "c", "order_status": "new"}],
            },
            OPEN,
        ),
        (
            "kraken",
            {
                "feed": "open_orders",
                "order_id": "1",
                "cli_ord_id": "c",
                "is_cancel": True,
                "reason": "cancelled_by_user",
            },
            CANCELLED,
        ),
        (
            "kraken",
            {
                "feed": "open_orders",
                "order": {"order_id": "1", "cli_ord_id": "c"},
                "is_cancel": False,
                "reason": "new_placed_order_by_user",
            },
            OPEN,
        ),
        (
            "backpack",
            {
                "stream": "account.orderUpdate",
                "data": {"e": "orderCancelled", "i": "1", "c": 7, "X": "Cancelled"},
            },
            CANCELLED,
        ),
        (
            "extended",
            {"type": "ORDER", "data": {"orders": [{"id": 1, "externalId": "c", "status": "NEW"}]}},
            OPEN,
        ),
        (
            "hyperliquid",
            {
                "channel": "orderUpdates",
                "data": [{"order": {"oid": 1, "cloid": "0xC"}, "status": "canceled"}],
            },
            CANCELLED,
        ),
        (
            "lighter",
            {
                "type": "update/account_all_orders",
                "orders": {
                    "0": [
                        {"order_index": 1, "client_order_index": 5, "status": "canceled-post-only"}
                    ]
                },
            },
            CANCELLED,
        ),
        (
            "ondo",
            {
                "channel": "ordersPerps",
                "data": [{"orderId": "1", "clientOrderId": "c", "status": "OPEN"}],
            },
            OPEN,
        ),
        (
            "arcus",
            {"channel": "orders", "data": {"orderId": "1", "clientId": "c", "status": "filled"}},
            FILLED,
        ),
    ],
)
def test_extract_events_per_exchange(exchange, payload, state):
    events = extract_events(exchange, payload)
    assert [event.state for event in events] == [state]
    assert events[0].order_id == "1"


def test_hyperliquid_cloid_matches_case_insensitively():
    payload = {"data": [{"order": {"oid": 9, "cloid": "0xABCDEF"}, "status": "open"}]}
    (event,) = extract_events("hyperliquid", payload)
    assert matches(event, "", "0xabcdef")
    assert not matches(event, "8", "0xabc")


def _field(number, value):
    def varint(n):
        out = bytearray()
        while True:
            byte = n & 0x7F
            n >>= 7
            out.append(byte | (0x80 if n else 0))
            if not n:
                return bytes(out)

    if isinstance(value, int):
        return varint(number << 3) + varint(value)
    return varint(number << 3 | 2) + varint(len(value)) + value


def test_mexc_spot_protobuf_order_is_decoded_from_the_wrapper():
    order = _field(1, b"C02__1") + _field(2, CLIENT_ID.encode()) + _field(3, b"0.1") + _field(15, 4)
    wrapper = _field(1, b"spot@private.orders.v3.api.pb") + _field(304, order) + _field(6, 17)
    events = mexc_protobuf_events(wrapper, 1.0)
    assert [(e.order_id, e.client_ids, e.state) for e in events] == [
        ("C02__1", (CLIENT_ID,), CANCELLED)
    ]
    assert extract_events("mexc", b"\xff\xff garbage") == []


def _verdict(exchange, market, payload):
    ack = _ack(exchange, market)
    assert ack is not None
    return ack(payload)


def test_ack_detection():
    assert _verdict("okx", "spot", {"event": "subscribe", "arg": {"channel": "orders"}}) == "ok"
    assert _verdict("okx", "spot", {"event": "error", "code": "60011"}) == "error"
    assert _verdict("binance", "spot", {"id": 1, "status": 200, "result": {}}) == "ok"
    assert _verdict("binance", "spot", {"id": 1, "status": 401, "error": {}}) == "error"
    assert _verdict("kraken", "swap", {"event": "subscribed", "feed": "open_orders"}) == "ok"
    assert _verdict("hyperliquid", "swap", {"channel": "subscriptionResponse"}) == "ok"
    assert _verdict("bybit", "linear", {"topic": "order", "data": []}) is None
    assert _ack("binance", "swap") is None  # listenKey push-only
    assert _ack("aster", "spot") is None


def test_record_is_redacted_and_never_contains_payloads(tmp_path, monkeypatch):
    monkeypatch.setenv("BYBIT_API_SECRET", "super-secret-value")
    result = {
        "exchange": "bybit",
        "market": "linear",
        "stage": "ws_wait_open",
        "status": "failed",
        "error_message": "boom super-secret-value apiKey=abcdef",
        "order_id": ORDER_ID,
        "client_order_id": CLIENT_ID,
        "ws_open_latency_ms": "12",
        "raw_payload": json.dumps(bybit(ORDER_ID, CLIENT_ID, "New")),
    }
    row = ws_record(result, "private.subscribe_orders (order)")
    assert row["case"] == "ws_order_stream"
    assert "raw_payload" not in row
    assert "super-secret-value" not in json.dumps(row)
    assert "abcdef" not in row["error_message"]
    assert row["order_id"] == ORDER_ID and row["client_order_id"] == CLIENT_ID
    path = write_ws_record(tmp_path, row)
    written = path.read_text(encoding="utf8")
    assert "super-secret-value" not in written
    assert "orderStatus" not in written
    assert json.loads(written) == [row]


@pytest.mark.asyncio
async def test_unexpected_fill_check_in_find():
    ws = FakeWs()
    stream = OrderStream(ws, "bybit", heartbeat=None)
    stream.feed(bybit(ORDER_ID, "", "Filled"))
    with pytest.raises(StreamUnexpectedState):
        stream.find(ORDER_ID, CLIENT_ID, {OPEN})
    await stream.close()
