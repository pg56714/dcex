"""Replay official Kraken V1 requests and protocol events over native sockets."""

import asyncio
import copy

import pytest

from dcex.ws.kraken import FuturesPublicClient, PublicClient, V1Client
from tests.unit.ws_inventory_peer import echo_peer
from tests.unit.ws_official_examples import json_examples, load_operations

OPERATIONS = load_operations("kraken")
REQUEST_EVENTS = {
    "subscribe",
    "unsubscribe",
    "ping",
    "addOrder",
    "amendOrder",
    "editOrder",
    "cancelOrder",
    "cancelAll",
    "cancelAllOrdersAfter",
}
CASES = [
    (op["row"], msg)
    for op in OPERATIONS
    if 4573 <= op["row"] <= 4590
    for msg in json_examples(op["text"])
    if isinstance(msg, dict) and msg.get("event") in REQUEST_EVENTS
]
EVENT_CASES = [
    (op["row"], msg)
    for op in OPERATIONS
    if op["row"] in {4580, 4586, 4587, 4607}
    for msg in json_examples(op["text"])
]


@pytest.mark.asyncio
@pytest.mark.parametrize(("row", "message"), CASES)
async def test_v1_official_message(row, message):
    message = copy.deepcopy(message)
    private = "token" in message or "token" in message.get("subscription", {})
    token = "offline-session-token" if private else None
    if "token" in message:
        message["token"] = token
    if "token" in message.get("subscription", {}):
        message["subscription"]["token"] = token
    async with echo_peer() as (url, received):
        client = V1Client(token, base_url=url, timeout=2)
        try:
            await asyncio.wait_for(client.connect(), 3)
            await client.send_message(
                message, all_symbols=message["event"] in {"cancelAll", "cancelAllOrdersAfter"}
            )
            assert await asyncio.wait_for(client.recv(), 3) == message
        finally:
            await client.close()
    assert received == [message], row


@pytest.mark.asyncio
@pytest.mark.parametrize(("row", "event"), EVENT_CASES)
async def test_unsolicited_protocol_event(row, event):
    async with echo_peer(events=[event]) as (url, received):
        client = (
            PublicClient(base_url=url, timeout=2)
            if row == 4607
            else V1Client(base_url=url, timeout=2)
        )
        try:
            await client.connect()
            assert await asyncio.wait_for(client.recv(), 3) == event
        finally:
            await client.close()
    assert received == []


@pytest.mark.asyncio
async def test_futures_heartbeat_and_spot_v2_ping():
    for futures in (True, False):
        async with echo_peer() as (url, received):
            client = (
                FuturesPublicClient(base_url=url, timeout=2)
                if futures
                else PublicClient(base_url=url, timeout=2)
            )
            try:
                await client.connect()
                if futures:
                    await client.subscribe_heartbeat()
                    expected = {"event": "subscribe", "feed": "heartbeat"}
                else:
                    request_id = await client.ping()
                    expected = {"method": "ping", "req_id": request_id}
                assert await asyncio.wait_for(client.recv(), 3) == expected
            finally:
                await client.close()
        assert received == [expected]


@pytest.mark.asyncio
async def test_account_wide_cancel_requires_explicit_scope():
    async with echo_peer() as (url, received):
        client = V1Client("token", base_url=url, timeout=2)
        try:
            await client.connect()
            for event in ("cancelAll", "cancelAllOrdersAfter"):
                with pytest.raises(ValueError, match="all_symbols"):
                    await client.send_message({"event": event, "timeout": 60})
        finally:
            await client.close()
    assert received == []


def test_v1_default_urls():
    assert V1Client()._native_client.url() == "wss://ws.kraken.com/"
    assert V1Client("token")._native_client.url() == "wss://ws-auth.kraken.com/"
