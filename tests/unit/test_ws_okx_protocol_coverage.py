"""Replay every documented OKX WebSocket request against a real local peer."""

import asyncio
import base64
import hashlib
import hmac
import json
import re
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from aiohttp import WSMsgType, web

from dcex.ws.okx import PrivateClient, PublicClient

ROOT = Path(__file__).resolve().parents[2]
OPERATIONS = json.loads(
    (ROOT / "docs/official-endpoint-inventory/sources/okx-ws.json").read_text(encoding="utf-8")
)
CASES = [
    {
        "row": op["row"],
        "example": example,
        "private": "required login" in op["text"].lower(),
        "path": (re.search(r"/ws/v5/(?:private|public|business)", op["text"]) or ["/ws/v5/public"])[
            0
        ],
    }
    for op in OPERATIONS
    for example in op["examples"]
    if example.get("args") and isinstance(example["args"][0], dict) and example["op"] != "login"
]


@asynccontextmanager
async def peer(path, login_event=None):
    received = []

    async def socket(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for message in ws:
            if message.type == WSMsgType.TEXT:
                payload = json.loads(message.data)
                received.append(payload)
                if payload.get("op") == "login":
                    await ws.send_json({"event": "login", "code": "0"})
                    if login_event is not None:
                        await ws.send_json(login_event)
                else:
                    await ws.send_json(payload)
        return ws

    app = web.Application()
    app.router.add_get(path, socket)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    try:
        yield f"ws://127.0.0.1:{runner.addresses[0][1]}{path}", received
    finally:
        await runner.cleanup()


def assert_login(payload):
    assert payload["op"] == "login"
    assert len(payload["args"]) == 1
    arg = payload["args"][0]
    assert arg["apiKey"] == "key"
    assert arg["passphrase"] == "passphrase"
    assert arg["timestamp"].isdigit()
    preimage = arg["timestamp"] + "GET/users/self/verify"
    assert (
        arg["sign"]
        == base64.b64encode(
            hmac.new(b"secret", preimage.encode(), hashlib.sha256).digest()
        ).decode()
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CASES, ids=lambda c: str(c["row"]) + "-" + c["example"]["op"])
async def test_official_message_shape(case):
    example = case["example"]
    private = case["private"] or example["op"] not in {"subscribe", "unsubscribe"}
    async with peer(case["path"]) as (url, received):
        client = (
            PrivateClient("key", "secret", "passphrase", base_url=url, timeout=2)
            if private
            else PublicClient(base_url=url, timeout=2)
        )
        try:
            await asyncio.wait_for(client.connect(), 3)
            if example["op"] in {"subscribe", "unsubscribe"}:
                await getattr(client, example["op"] + "_args")(example["args"])
                expected = {"op": example["op"], "args": example["args"]}
            else:
                await client.send_operation("test123", example["op"], example["args"])
                expected = {"id": "test123", "op": example["op"], "args": example["args"]}
            assert await asyncio.wait_for(client.recv(), 3) == expected
        finally:
            await client.close()
    assert received[-1] == expected
    if private:
        assert len(received) == 2
        assert_login(received[0])
    else:
        assert len(received) == 1


@pytest.mark.asyncio
async def test_login_and_connection_count_event():
    event = {
        "event": "channel-conn-count",
        "channel": "orders",
        "connCount": "2",
        "connId": "abc123",
    }
    async with peer("/ws/v5/private", event) as (url, received):
        client = PrivateClient("key", "secret", "passphrase", base_url=url, timeout=2)
        try:
            await asyncio.wait_for(client.connect(), 3)
            assert_login(received[0])
            assert await asyncio.wait_for(client.recv(), 3) == event
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_mass_cancel_requires_scope_before_transport():
    async with peer("/ws/v5/private") as (url, received):
        client = PrivateClient("key", "secret", "passphrase", base_url=url, timeout=2)
        try:
            await client.connect()
            with pytest.raises(ValueError, match="all_symbols"):
                await client.send_operation("test", "mass-cancel", [{"instType": "OPTION"}])
            assert len(received) == 1
        finally:
            await client.close()
