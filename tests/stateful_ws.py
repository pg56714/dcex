"""Opt-in check that the private WebSocket stream reports our test order's lifecycle.

The REST lifecycle (`run_lifecycle`) still places, queries and cancels the single
far-from-market post-only order. This module only adds a stream observer: the
private order stream must report the order as open before cancellation is sent and
as cancelled afterwards. Raw stream payloads are never stored or reported.
"""

import asyncio
import importlib
import inspect
import json
import logging
import os
import time
from collections.abc import Awaitable, Callable, Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from dotenv import load_dotenv

from scripts.live.redaction import redact
from tests.live_gate import stateful_tests_enabled
from tests.stateful_lifecycle import (
    InsufficientBalance,
    LifecycleError,
    MarketUnavailable,
    Plan,
    run_lifecycle,
)

CASE = "ws_order_stream"
EVENT_TIMEOUT = 20.0
HEARTBEAT_INTERVAL = 15.0
PUSH_ONLY_SETTLE = 3.0  # Live: BingX swap listenKey push missed an order at 1s.
ARCUS_SPOT_NA = "N/A: Arcus has no spot market for the stateful lifecycle"

OPEN, CANCELLED, FILLED, OTHER = "open", "cancelled", "filled", "other"


class StreamEventMissing(LifecycleError):
    """The private stream did not report the expected order state in time."""


class StreamUnexpectedState(LifecycleError):
    """The private stream reported a fill (or partial fill) for the test order."""


@dataclass(frozen=True)
class OrderEvent:
    """Only identifiers and a normalized state; the raw payload is discarded."""

    order_id: str
    client_ids: tuple[str, ...]
    state: str
    received_at: float
    raw_state: str = ""  # Native status text, kept only for timeout diagnostics.


# --------------------------------------------------------------------------- parsing


@dataclass(frozen=True)
class Fields:
    """Per-stream key names for order rows and the native-to-normalized state map."""

    ids: tuple[str, ...]
    clients: tuple[str, ...]
    statuses: tuple[str, ...]
    states: dict[str, str] = field(default_factory=dict)


_COMMON_STATES = {
    "new": OPEN,
    "open": OPEN,
    "live": OPEN,
    "resting": OPEN,
    "accepted": OPEN,
    "orderaccepted": OPEN,
    "canceled": CANCELLED,
    "cancelled": CANCELLED,
    "ordercancelled": CANCELLED,
    "ordercanceled": CANCELLED,
    "filled": FILLED,
    "partially_filled": FILLED,
    "partiallyfilled": FILLED,
    "partially-filled": FILLED,
    "orderfill": FILLED,
    "match": FILLED,
}
_BINANCE = Fields(("i",), ("c", "C"), ("X",))
_MEXC_SPOT_STATES = {"1": OPEN, "2": FILLED, "3": FILLED, "4": CANCELLED, "5": FILLED}
_MEXC_FUTURES_STATES = {"2": OPEN, "3": FILLED, "4": CANCELLED}

FIELDS: dict[str, Fields] = {
    "binance": _BINANCE,
    "aster": _BINANCE,
    # Live swap ORDER_TRADE_UPDATE reports a resting order as WORKING; REST uses PENDING.
    "bingx": Fields(("i",), ("c", "C"), ("X",), {"working": OPEN, "pending": OPEN}),
    "backpack": Fields(("i",), ("c",), ("X",)),
    "bybit": Fields(("orderId",), ("orderLinkId",), ("orderStatus",)),
    "okx": Fields(("ordId",), ("clOrdId",), ("state",)),
    "bitget": Fields(("orderId",), ("clientOid",), ("orderStatus", "status")),
    "mexc": Fields(("orderId",), ("externalOid",), ("state",), _MEXC_FUTURES_STATES),
    # KuCoin's "type" carries the transition (open/match/filled/canceled).
    "kucoin": Fields(("orderId",), ("clientOid",), ("type",)),
    "kraken": Fields(("order_id",), ("cl_ord_id",), ("order_status",)),
    "extended": Fields(("id",), ("externalId",), ("status",)),
    "ondo": Fields(("orderId", "id"), ("clientOrderId", "clientId"), ("status", "state")),
    "hyperliquid": Fields(("oid",), ("cloid",), ("status",)),
    "lighter": Fields(("order_index",), ("client_order_index",), ("status",)),
    "arcus": Fields(("orderId", "id"), ("clientId", "clientOrderId"), ("status", "state")),
}


def normalize_state(value: object, states: dict[str, str] | None = None) -> str:
    """Map a native status to open/cancelled/filled/other; unknown values are 'other'."""
    text = str(value).strip().lower()
    if states and text in states:
        return states[text]
    if text in _COMMON_STATES:
        return _COMMON_STATES[text]
    # Lighter "canceled-post-only", Hyperliquid "marginCanceled", etc.
    if "cancel" in text:
        return CANCELLED
    return OTHER


def _walk(value: object) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _text(value: object) -> str:
    return "" if value is None or isinstance(value, dict | list) else str(value)


def _key_shape(value: object, depth: int = 0) -> str:
    """Nested key names only (no values), e.g. {e,o:{X,c,i}}."""
    if isinstance(value, dict) and depth < 3:
        parts = [
            f"{key}:{_key_shape(item, depth + 1)}" if isinstance(item, dict | list) else str(key)
            for key, item in list(value.items())[:24]
        ]
        return "{" + ",".join(parts) + "}"
    if isinstance(value, list) and value and depth < 3:
        return "[" + _key_shape(value[0], depth + 1) + "]"
    return "[]" if isinstance(value, list) else "_"


def frame_kind(payload: object) -> str:
    """A diagnostic label: the event-type field or the key names, never values."""
    if isinstance(payload, bytes | bytearray | memoryview):
        return f"bytes[{len(payload)}]"
    if isinstance(payload, str):
        return "text:" + payload[:12] if payload.isalpha() else "text"
    if isinstance(payload, dict):
        for key in ("e", "dataType", "event", "topic", "channel", "type", "op"):
            if isinstance(payload.get(key), str):
                return f"{key}={payload[key][:40]}"
        return "keys=" + "/".join(sorted(map(str, payload))[:6])
    return type(payload).__name__


def extract_events(exchange: str, payload: object, received_at: float = 0.0) -> list[OrderEvent]:
    """Extract order rows from one decoded payload using the exchange's field names."""
    if isinstance(payload, bytes | bytearray | memoryview):
        return mexc_protobuf_events(bytes(payload), received_at)
    if exchange == "kraken" and isinstance(payload, dict) and payload.get("feed") == "open_orders":
        return _kraken_futures_events(payload, received_at)
    spec = FIELDS[exchange]
    events = []
    for row in _walk(payload):
        if exchange == "hyperliquid" and isinstance(row.get("order"), dict):
            row = {**row["order"], **{k: v for k, v in row.items() if k != "order"}}
        status_key = next((key for key in spec.statuses if key in row), None)
        if status_key is None:
            continue
        order_id = next((_text(row[key]) for key in spec.ids if _text(row.get(key))), "")
        clients = tuple(_text(row[key]) for key in spec.clients if _text(row.get(key)))
        if not order_id and not clients:
            continue
        state = normalize_state(row[status_key], spec.states)
        if exchange == "kucoin" and state == OTHER:
            state = normalize_state(row.get("status", ""))
        raw = str(row[status_key])[:24]
        events.append(OrderEvent(order_id, clients, state, received_at, raw))
    return events


def _kraken_futures_events(payload: dict[str, Any], received_at: float) -> list[OrderEvent]:
    raw = payload.get("order")
    order: dict[str, Any] = raw if isinstance(raw, dict) else {}
    order_id = _text(order.get("order_id") or payload.get("order_id"))
    client = _text(order.get("cli_ord_id") or payload.get("cli_ord_id"))
    if not order_id and not client:
        return []
    reason = str(payload.get("reason", "")).lower()
    if payload.get("is_cancel"):
        state = FILLED if "fill" in reason else CANCELLED if "cancel" in reason else OTHER
    else:
        state = FILLED if "fill" in reason else OPEN
    return [OrderEvent(order_id, (client,) if client else (), state, received_at)]


# MEXC spot private streams are protobuf. Rather than depend on generated classes,
# walk the wire format: PrivateOrdersV3Api has id=1, clientId=2 (strings), status=15.


def _varint(data: bytes, index: int) -> tuple[int, int]:
    shift = result = 0
    while True:
        if index >= len(data) or shift > 63:
            raise ValueError("truncated varint")
        byte = data[index]
        index += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, index
        shift += 7


def _protobuf_fields(data: bytes) -> list[tuple[int, int, object]] | None:
    fields: list[tuple[int, int, object]] = []
    index = 0
    try:
        while index < len(data):
            key, index = _varint(data, index)
            number, wire = key >> 3, key & 7
            if number == 0:
                return None
            if wire == 0:
                value, index = _varint(data, index)
                fields.append((number, wire, value))
            elif wire == 1:
                index += 8
            elif wire == 5:
                index += 4
            elif wire == 2:
                length, index = _varint(data, index)
                if index + length > len(data):
                    return None
                fields.append((number, wire, data[index : index + length]))
                index += length
            else:
                return None
        if index != len(data):
            return None
    except ValueError:
        return None
    return fields


def mexc_protobuf_events(data: bytes, received_at: float, depth: int = 0) -> list[OrderEvent]:
    """Find PrivateOrdersV3Api-shaped messages (string 1, string 2, varint 15)."""
    fields = _protobuf_fields(data)
    if fields is None or depth > 4:
        return []
    by_number: dict[int, object] = {}
    for number, _wire, value in fields:
        by_number.setdefault(number, value)
    events = []
    order_id, client, status = by_number.get(1), by_number.get(2), by_number.get(15)
    if isinstance(order_id, bytes) and isinstance(status, int):
        try:
            identifier = order_id.decode()
            client_text = client.decode() if isinstance(client, bytes) else ""
        except UnicodeDecodeError:
            identifier = client_text = ""
        if identifier:
            state = normalize_state(status, _MEXC_SPOT_STATES)
            clients = (client_text,) if client_text else ()
            events.append(OrderEvent(identifier, clients, state, received_at))
    for _number, wire, value in fields:
        if wire == 2 and isinstance(value, bytes) and len(value) > 2:
            events.extend(mexc_protobuf_events(value, received_at, depth + 1))
    return events


# ------------------------------------------------------------------------- collector


class OrderStream:
    """Buffers normalized order events from a private WS client and waits for states."""

    def __init__(
        self,
        ws: Any,  # noqa: ANN401
        exchange: str,
        *,
        ack: Callable[[object], str | None] | None = None,
        heartbeat: float | None = HEARTBEAT_INTERVAL,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.ws = ws
        self.exchange = exchange
        self.ack = ack
        self.heartbeat = heartbeat
        self.clock = clock
        self.events: list[OrderEvent] = []
        self.confirmed = asyncio.Event()
        self.ack_error = ""
        self.error: BaseException | None = None
        self._changed = asyncio.Event()
        self._tasks: list[asyncio.Task[None]] = []
        self.frames = 0
        self.kinds: list[str] = []  # Event type labels only, never payload values.
        self.unparsed: list[str] = []  # Key names of order frames that yielded no event.

    def feed(self, payload: object) -> None:
        """Record order rows; payloads are parsed immediately and never retained."""
        now = self.clock()
        self.frames += 1
        kind = frame_kind(payload)
        if kind not in self.kinds and len(self.kinds) < 12:
            self.kinds.append(kind)
        if self.ack is not None and not self.confirmed.is_set():
            verdict = self.ack(payload)
            if verdict == "error":
                self.ack_error = "subscription rejected by the exchange"
                self.confirmed.set()
            elif verdict == "ok":
                self.confirmed.set()
        try:
            found = extract_events(self.exchange, payload, now)
            self.events.extend(found)
            if not found and "ORDER" in kind.upper() and len(self.unparsed) < 3:
                self.unparsed.append(_key_shape(payload))
        except Exception:  # noqa: BLE001 - a malformed frame must not stop the reader
            pass
        self._changed.set()

    async def _reader(self) -> None:
        try:
            while True:
                self.feed(await self.ws.recv())
        except asyncio.CancelledError:
            raise
        except BaseException as error:  # noqa: BLE001 - surfaced through wait()
            self.error = error
            self._changed.set()
            self.confirmed.set()

    async def _pinger(self) -> None:
        assert self.heartbeat is not None
        while True:
            await asyncio.sleep(self.heartbeat)
            try:
                await self.ws.ping()
            except Exception:  # noqa: BLE001 - a broken socket also stops the reader
                return

    def start(self) -> None:
        self._tasks.append(asyncio.create_task(self._reader()))
        if self.heartbeat and callable(getattr(self.ws, "ping", None)):
            self._tasks.append(asyncio.create_task(self._pinger()))

    async def wait_confirmed(self, timeout: float) -> None:  # noqa: ASYNC109
        """Wait for the exchange's subscription acknowledgement (push-only: settle briefly)."""
        if self.ack is None:
            await asyncio.sleep(min(PUSH_ONLY_SETTLE, timeout))
            self.confirmed.set()
        else:
            try:
                await asyncio.wait_for(self.confirmed.wait(), timeout)
            except TimeoutError:
                raise StreamEventMissing(
                    f"{self.exchange}: no subscription confirmation within {timeout:g}s; "
                    "no order was submitted"
                ) from None
        if self.ack_error:
            raise LifecycleError(f"{self.exchange}: {self.ack_error}; no order was submitted")
        if self.error is not None:
            raise LifecycleError(
                f"{self.exchange}: private stream closed before subscription: " + redact(self.error)
            )

    def describe(self, order_id: str, client_id: str, since: float) -> str:
        """Diagnostics without values: native state, ID match and timing per event."""
        rows = []
        for event in self.events[-6:]:
            id_ok = bool(order_id) and event.order_id.lower() == str(order_id).lower()
            client_ok = bool(client_id) and str(client_id).lower() in {
                c.lower() for c in event.client_ids
            }
            rows.append(
                f"{event.raw_state or '?'}->{event.state}"
                f" id={'ok' if id_ok else f'no(len {len(event.order_id)})'}"
                f" client={'ok' if client_ok else f'no(n {len(event.client_ids)})'}"
                f"{' early' if event.received_at < since else ''}"
            )
        return ", ".join(rows) or "none"

    def find(
        self, order_id: str, client_id: str, states: set[str], since: float = 0.0
    ) -> OrderEvent | None:
        for event in self.events:
            if event.received_at < since or not matches(event, order_id, client_id):
                continue
            if event.state == FILLED:
                raise StreamUnexpectedState(
                    "UNEXPECTED FILL reported by the private stream; manual reconciliation required"
                )
            if event.state in states:
                return event
        return None

    async def wait_for(
        self,
        order_id: str,
        client_id: str,
        state: str,
        timeout: float,  # noqa: ASYNC109
        *,
        since: float = 0.0,
    ) -> OrderEvent:
        """Return the first matching event in `state`; fail clearly on timeout or a fill."""
        deadline = self.clock() + timeout
        while True:
            self._changed.clear()
            found = self.find(order_id, client_id, {state}, since)
            if found is not None:
                return found
            if self.error is not None:
                raise StreamEventMissing(
                    f"{self.exchange}: private stream closed before a '{state}' event for the "
                    "test order: " + redact(self.error)
                )
            remaining = deadline - self.clock()
            if remaining <= 0:
                raise StreamEventMissing(
                    f"{self.exchange}: no '{state}' order-update event for the test order "
                    f"within {timeout:g}s on the private stream (received {self.frames} "
                    f"frames: {', '.join(self.kinds) or 'none'}; "
                    f"order events: {self.describe(order_id, client_id, since)}; "
                    f"unparsed order frames: {' | '.join(self.unparsed) or 'none'})"
                )
            try:
                await asyncio.wait_for(self._changed.wait(), remaining)
            except TimeoutError:
                continue

    async def close(self) -> None:
        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            try:
                await task
            except BaseException:  # noqa: BLE001, S110 - shutting down
                pass
        self._tasks.clear()
        closed = self.ws.close()
        if inspect.isawaitable(closed):
            await closed


def matches(event: OrderEvent, order_id: str, client_id: str) -> bool:
    """Match by exchange order ID or by our client ID; never by symbol or side."""
    if order_id and event.order_id and event.order_id.lower() == str(order_id).lower():
        return True
    return bool(client_id) and str(client_id).lower() in {c.lower() for c in event.client_ids}


# ---------------------------------------------------------------- adapter wrapper


class StreamCheckedAdapter:
    """Delegates to the REST adapter; requires a stream 'open' event before cancelling."""

    def __init__(
        self,
        adapter: Any,  # noqa: ANN401
        stream: OrderStream,
        result: dict[str, str],
        timeout: float = EVENT_TIMEOUT,  # noqa: ASYNC109
    ) -> None:
        self._adapter = adapter
        self._stream = stream
        self._result = result
        self._timeout = timeout
        self.identifier = ""
        self.placed_at = 0.0
        self.cancel_sent_at = 0.0
        self.open_checked = False

    @property
    def client_order_id(self) -> str:
        return self._adapter.client_order_id

    @client_order_id.setter
    def client_order_id(self, value: str) -> None:
        self._adapter.client_order_id = value

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401 - next_price_plan, recover_*
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._adapter, name)

    async def prepare(self) -> tuple[Plan, Any]:
        return await self._adapter.prepare()

    async def book(self) -> Any:  # noqa: ANN401
        return await self._adapter.book()

    async def positions(self) -> list[object]:
        return await self._adapter.positions()

    async def open_orders(self) -> list[object]:
        return await self._adapter.open_orders()

    async def order(self, identifier: str) -> Any:  # noqa: ANN401
        return await self._adapter.order(identifier)

    async def recover_order(self) -> str | None:
        return await self._adapter.recover_order()

    async def place(self, plan: Plan) -> str:
        self.placed_at = self._stream.clock()
        identifier = await self._adapter.place(plan)
        self.identifier = str(identifier or "")
        return identifier

    async def cancel(self, identifier: str) -> None:
        if not self.open_checked and self.identifier and str(identifier) == self.identifier:
            # Only once: a failure here leaves run_lifecycle's finally to cancel via REST,
            # and that cleanup call goes straight through.
            self.open_checked = True
            self._result["stage"] = "ws_wait_open"
            event = await self._stream.wait_for(
                self.identifier, self.client_order_id, OPEN, self._timeout, since=self.placed_at
            )
            self._result["ws_open_latency_ms"] = _ms(event.received_at - self.placed_at)
            self._result["stage"] = "cancel"
        self.cancel_sent_at = self._stream.clock()
        await self._adapter.cancel(identifier)


def _ms(seconds: float) -> str:
    return str(max(0, round(seconds * 1000)))


async def verify_order_stream(
    adapter: Any,  # noqa: ANN401
    stream: OrderStream,
    result: dict[str, str],
    *,
    timeout: float = EVENT_TIMEOUT,  # noqa: ASYNC109
    poll_delay: float = 0.25,
    lifecycle: Callable[..., Awaitable[None]] = run_lifecycle,
) -> None:
    """Confirm subscription, run the unchanged REST lifecycle, then require a cancel event."""
    result["case"] = CASE
    result["stage"] = "ws_subscribe"
    stream.start()
    await stream.wait_confirmed(timeout)
    checked = StreamCheckedAdapter(adapter, stream, result, timeout)
    try:
        await lifecycle(checked, result, poll_delay=poll_delay)
    finally:
        # The REST lifecycle labels its own case; this run is the stream check.
        result["case"] = CASE
    if not checked.open_checked:
        raise LifecycleError("lifecycle completed without cancelling through the stream check")
    result["stage"] = "ws_wait_cancelled"
    try:
        event = await stream.wait_for(
            checked.identifier,
            checked.client_order_id,
            CANCELLED,
            timeout,
            since=checked.placed_at,
        )
    except LifecycleError as error:
        result["error_message"] = redact(error)
        raise
    result["ws_cancel_latency_ms"] = _ms(event.received_at - checked.cancel_sent_at)
    result["stage"] = "complete"


# ------------------------------------------------------------------ stream specs


def _ok_if(condition: bool, error: bool = False) -> str | None:
    return "error" if error else "ok" if condition else None


def _ack(exchange: str, market: str) -> Callable[[object], str | None] | None:
    """Subscription acknowledgement per exchange; None means the stream is push-only."""

    def ack(payload: object) -> str | None:
        if not isinstance(payload, dict):
            return None
        p = payload
        if exchange == "binance":  # Spot WebSocket API response to the subscribe request
            return _ok_if(
                "result" in p and p.get("status") == 200, "status" in p and p.get("status") != 200
            )
        if exchange == "bybit":
            if p.get("op") == "subscribe":
                return _ok_if(p.get("success") is True, p.get("success") is False)
            return _ok_if(False, p.get("op") == "auth" and p.get("success") is False)
        if exchange in {"okx", "bitget"}:
            return _ok_if(p.get("event") == "subscribe", p.get("event") == "error")
        if exchange == "bingx":
            if "code" in p and "id" in p:
                return _ok_if(str(p.get("code")) == "0", str(p.get("code")) != "0")
            return None
        if exchange == "mexc" and market == "spot":
            if "code" in p and "id" in p:
                return _ok_if(str(p.get("code")) == "0", str(p.get("code")) != "0")
            return None
        if exchange == "mexc":
            channel = str(p.get("channel", ""))
            return _ok_if(channel == "rs.personal.filter", channel == "rs.error")
        if exchange == "kucoin":
            return _ok_if(p.get("type") == "ack", p.get("type") == "error")
        if exchange == "kraken" and market == "spot":
            if p.get("method") == "subscribe":
                return _ok_if(p.get("success") is True, p.get("success") is False)
            return None
        if exchange == "kraken":
            event = str(p.get("event", ""))
            return _ok_if(
                event == "subscribed" and p.get("feed") == "open_orders",
                event in {"error", "subscribed_failed", "alert"},
            )
        if exchange == "hyperliquid":
            return _ok_if(p.get("channel") == "subscriptionResponse", p.get("channel") == "error")
        if exchange == "lighter":
            kind = str(p.get("type", ""))
            return _ok_if(
                kind.startswith("subscribed/") or kind.startswith("update/"), kind == "error"
            )
        return None

    push_only = {"aster", "backpack", "extended", "ondo", "arcus"}
    if exchange in push_only or (exchange == "binance" and market != "spot"):
        return None
    if exchange == "bingx" and market != "spot":
        return None
    return ack


@dataclass(frozen=True)
class StreamSpec:
    method: str
    open: Callable[[], Awaitable[Any]]
    ack: Callable[[object], str | None] | None


def stream_spec(exchange: str, market: str, options: dict[str, Any]) -> StreamSpec:
    """Build (but do not connect) the library's private order stream for one market."""
    ws = importlib.import_module("dcex.ws." + exchange)
    spot = market == "spot"
    o = options
    t = EVENT_TIMEOUT

    async def opened(client: Any, subscribe: Callable[[Any], Awaitable[object]] | None) -> Any:  # noqa: ANN401
        try:
            await client.connect()
            if subscribe is not None:
                await subscribe(client)
        except BaseException:
            closed = client.close()
            if inspect.isawaitable(closed):
                await closed
            raise
        return client

    def spec(method: str, factory: Callable[[], Any], subscribe=None) -> StreamSpec:  # noqa: ANN001
        return StreamSpec(method, lambda: opened(factory(), subscribe), _ack(exchange, market))

    key, secret = o.get("api_key", ""), o.get("api_secret", "")
    if exchange == "binance":
        if spot:
            return spec(
                "SpotApiClient.subscribe_user_data (executionReport)",
                lambda: ws.SpotApiClient(key, secret, timeout=t),
                lambda c: c.subscribe_user_data(),
            )
        return spec(
            "private(profile='futures') listenKey (ORDER_TRADE_UPDATE)",
            lambda: ws.private(key, secret, timeout=t, profile="futures"),
        )
    if exchange == "bybit":
        return spec(
            "private.subscribe_orders (order)",
            lambda: ws.private(key, secret, timeout=t),
            lambda c: c.subscribe_orders(),
        )
    if exchange == "okx":
        inst_type = "SPOT" if spot else "SWAP"
        return spec(
            f"private.subscribe_orders(inst_type={inst_type!r})",
            lambda: ws.private(key, secret, o["passphrase"], timeout=t),
            lambda c: c.subscribe_orders(inst_type=inst_type),
        )
    if exchange == "bitget":
        return spec(
            "uta_private.subscribe_orders (UTA order)",
            lambda: ws.uta_private(key, secret, o["passphrase"], timeout=t),
            lambda c: c.subscribe_orders(),
        )
    if exchange == "bingx":
        if spot:
            return spec(
                "private.subscribe_orders (spot.executionReport)",
                lambda: ws.private(key, secret, timeout=t),
                lambda c: c.subscribe_orders(),
            )
        return spec(
            "private(market='swap') listenKey push (ORDER_TRADE_UPDATE)",
            lambda: ws.private(key, secret, timeout=t, market="swap"),
        )
    if exchange == "mexc":
        if spot:
            return spec(
                "private.subscribe_orders (spot@private.orders.v3.api.pb)",
                lambda: ws.private(key, secret, timeout=t),
                lambda c: c.subscribe_orders(),
            )
        return spec(
            "FuturesPrivateClient login + set_private_filters([order])",
            lambda: ws.FuturesPrivateClient(key, secret, timeout=t),
            lambda c: c.set_private_filters([{"filter": "order"}]),
        )
    if exchange == "kucoin":
        return spec(
            "private.subscribe_orders (" + ("spot" if spot else "futures") + " tradeOrders)",
            lambda: ws.private(
                key, secret, o["passphrase"], timeout=t, market="spot" if spot else "futures"
            ),
            lambda c: c.subscribe_orders(),
        )
    if exchange == "kraken":
        if spot:
            return spec(
                "private.subscribe_executions (executions)",
                lambda: ws.private(o["spot_api_key"], o["spot_api_secret"], timeout=t),
                lambda c: c.subscribe_executions(snap_orders=False),
            )
        return spec(
            "FuturesPrivateClient.subscribe_open_orders (open_orders)",
            lambda: ws.FuturesPrivateClient(
                o["futures_api_key"], o["futures_api_secret"], timeout=t
            ),
            lambda c: c.subscribe_open_orders(),
        )
    if exchange == "backpack":
        return spec(
            "private.subscribe_orders (account.orderUpdate)",
            lambda: ws.private(key, secret, timeout=t),
            lambda c: c.subscribe_orders(),
        )
    if exchange == "aster":
        return spec(
            "private(market=%r) listenKey (%s)"
            % ("spot" if spot else "futures", "executionReport" if spot else "ORDER_TRADE_UPDATE"),
            lambda: ws.private(
                o["signer_address"],
                o["private_key"],
                user_address=o["user_address"],
                market="spot" if spot else "futures",
                timeout=t,
            ),
        )
    if exchange == "extended":
        return spec(
            "private.subscribe_account (ORDER)",
            lambda: ws.private(o["api_key"], timeout=t),
            lambda c: c.subscribe_account(),
        )
    if exchange == "ondo":
        return spec(
            "private.subscribe_orders (ordersPerps)",
            lambda: ws.private(o["api_key_id"], o["api_secret"], timeout=t),
            lambda c: c.subscribe_orders(),
        )
    if exchange == "hyperliquid":
        return spec(
            "PrivateClient(user).subscribe_order_updates (orderUpdates)",
            lambda: ws.private(o["wallet_address"], timeout=t),
            lambda c: c.subscribe_order_updates(),
        )
    if exchange == "lighter":
        return spec(
            "private_from_env(network).subscribe_account_all_orders",
            lambda: ws.private_from_env(network=market, timeout=t),
            lambda c: c.subscribe_account_all_orders(),
        )
    if exchange == "arcus":
        return spec(
            "private(address).subscribe_orders (orders)",
            lambda: ws.private(o["address"], timeout=t),
            lambda c: c.subscribe_orders(),
        )
    raise LifecycleError(f"N/A: no private order stream for {exchange}")


# ----------------------------------------------------------------------- reporting


def ws_record(result: dict[str, str], method: str) -> dict[str, str]:
    """A fixed, redacted schema; never includes raw payloads or credentials."""
    keys = (
        "exchange",
        "mode",
        "market",
        "stage",
        "status",
        "error_message",
        "order_id",
        "client_order_id",
        "ws_open_latency_ms",
        "ws_cancel_latency_ms",
        "cleanup",
    )
    row = {
        key: redact(
            result.get(key, ""), mask_environment=key not in {"order_id", "client_order_id"}
        )
        for key in keys
    }
    row["case"] = CASE
    row["stream_method"] = method
    return row


def write_ws_record(directory: Path, row: dict[str, str]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"{stamp}-{CASE}-{uuid4().hex[:8]}.json"
    path.write_text(json.dumps([row], indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    return path


# --------------------------------------------------------------------- entry point


async def run_ws_case(
    exchange: str, market: str, symbol: str, result: dict[str, str]
) -> None:  # pragma: no cover - live only
    """Open the private stream, then run the REST lifecycle while it is observed."""
    from tests.stateful_runner import ADAPTERS, client_options
    from tests.stateful_adapters import CexAdapter

    result.update(exchange=exchange, mode="async", market=market, stage="setup", case=CASE)
    if not stateful_tests_enabled():
        pytest.skip("Set RUN_LIVE_TRADING_TESTS=1 to run stateful tests.")
    if exchange == "arcus" and market == "spot":
        result.update(stage="not_applicable", status="N/A", skip_reason=ARCUS_SPOT_NA)
        pytest.skip(ARCUS_SPOT_NA)
    load_dotenv()
    client = stream = None
    method = ""
    status = "failed"
    try:
        cls = importlib.import_module(f"dcex.async_support.{exchange}.client").Client
        if exchange == "lighter":
            from dcex.lighter.credentials import credential_env_names

            if any(not os.getenv(name) for name in credential_env_names(market)):
                status = "skipped"
                pytest.skip(f"lighter {market}: missing network-scoped credentials")
            logger = logging.Logger("stateful-no-payload-logging")
            logger.disabled = True
            client = cls.from_env(network=market, preload_product_table=False, logger=logger)
            options: dict[str, Any] = {}
        else:
            options = client_options(exchange)
            client = cls(**options)
        await client.async_init()
        adapter = ADAPTERS.get(exchange, CexAdapter)(client, exchange, market, symbol)
        spec = stream_spec(exchange, market, options)
        method = spec.method
        ws = await spec.open()
        stream = OrderStream(ws, exchange, ack=spec.ack)
        await verify_order_stream(adapter, stream, result)
        status = "passed"
    except (InsufficientBalance, MarketUnavailable) as error:
        status = "skipped"
        pytest.skip(redact(error))
    except Exception as error:
        result["error_message"] = result.get("error_message") or redact(error)
        pytest.fail(result["error_message"], pytrace=False)
    finally:
        failures = []
        for resource in (stream, client):
            if resource is None:
                continue
            try:
                closed = resource.close()
                if inspect.isawaitable(closed):
                    await closed
            except Exception as error:  # noqa: BLE001
                failures.append(redact(error))
        if client is None and not result.get("error_message"):
            status = "skipped"  # client_options skipped on missing credentials
        record = dict(result, status=status)
        write_ws_record(
            Path(__file__).resolve().parents[1] / "live-results", ws_record(record, method)
        )
        if failures:
            pytest.fail("Close failed: " + "; ".join(failures), pytrace=False)
