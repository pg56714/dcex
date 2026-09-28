"""Official Alpha, Prediction, Backpack, Bitget and Hyperliquid stream messages."""

import asyncio
import base64
import hashlib
import hmac
import json
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from aiohttp import web
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from dcex.ws import aster, backpack, binance, bitget, hyperliquid
from tests.unit.test_ws_okx_inventory import peer as login_peer
from tests.unit.ws_inventory_peer import echo_peer
from tests.unit.ws_official_examples import load_operations

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / "tests/fixtures/ws_inventory_streams.json").read_text(encoding="utf-8"))
BITGET_CASES = [
    (op["row"], msg)
    for op in load_operations("bitget")
    for msg in op["examples"]
    if msg["op"] == "subscribe"
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CASES, ids=lambda c: str(c["row"]) + "-" + c["stream"])
async def test_documented_stream(case):
    exchange, stream = case["exchange"], case["stream"]
    key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    async with echo_peer() as (url, received):
        private = exchange == "backpack" and stream.startswith("account.")
        if exchange == "binance":
            client = binance.PublicClient(profile="alpha", base_url=url, timeout=2)
        elif exchange == "aster":
            client = aster.PredictionPublicClient(testnet=case["testnet"], base_url=url, timeout=2)
        elif private:
            client = backpack.PrivateClient(
                "offline-key", base64.b64encode(bytes(range(32))).decode(), base_url=url, timeout=2
            )
        else:
            client = backpack.PublicClient(base_url=url, timeout=2)
        try:
            await client.connect()
            for operation in ("subscribe", "unsubscribe"):
                request_id = await getattr(client, operation)([stream])
                event = await asyncio.wait_for(client.recv(), 3)
                expected = {"method": operation.upper(), "params": [stream]}
                if exchange in {"binance", "aster"}:
                    expected["id"] = request_id
                if private and operation == "subscribe":
                    signature = event["signature"]
                    assert signature[0] == "offline-key"
                    assert signature[2].isdigit()
                    assert signature[3] == "5000"
                    payload = f"instruction=subscribe&timestamp={signature[2]}&window=5000"
                    key.public_key().verify(base64.b64decode(signature[1]), payload.encode())
                    expected["signature"] = signature
                assert event == expected
        finally:
            await client.close()
    assert len(received) == 2


def test_alpha_default_url():
    assert (
        binance.PublicClient(profile="alpha")._native_client.url()
        == "wss://nbstream.binance.com/w3w/wsa/stream/stream"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(("row", "message"), BITGET_CASES)
async def test_bitget_margin_and_sbe(row, message):
    arg = message["args"][0]
    private = row in {4482, 4483, 4485, 4486}
    sbe = row >= 4510
    path = "/v3/ws/public/sbe" if sbe else "/v2/ws/private" if private else "/v2/ws/public"
    async with login_peer(path) as (url, received):
        if private:
            client = bitget.PrivateClient("key", "secret", "passphrase", base_url=url, timeout=2)
        elif sbe:
            client = bitget.sbe_public(arg["instType"], base_url=url, timeout=2)
        else:
            client = bitget.PublicClient(arg["instType"], base_url=url, timeout=2)
        try:
            await client.connect()
            for op in ("subscribe", "unsubscribe"):
                method = getattr(client, op + "_channel")
                if private:
                    await method(
                        arg["instType"], arg["channel"], arg.get("instId"), arg.get("coin")
                    )
                else:
                    await method(
                        arg.get("topic", arg.get("channel")), arg.get("symbol", arg.get("instId"))
                    )
                expected = {"op": op, "args": [arg]}
                assert await asyncio.wait_for(client.recv(), 3) == expected
        finally:
            await client.close()
    if private:
        auth = received[0]["args"][0]
        preimage = auth["timestamp"] + "GET/user/verify"
        assert (
            auth["sign"]
            == base64.b64encode(
                hmac.new(b"secret", preimage.encode(), hashlib.sha256).digest()
            ).decode()
        )
    assert received[-1] == {"op": "unsubscribe", "args": [arg]}


@pytest.mark.asyncio
async def test_sbe_preserves_binary_frame():
    # A binary frame must never be coerced through UTF-8/JSON by the wrapper.
    frame = bytes.fromhex("3800ea0301000200") + bytes(range(56)) + b"\x07BTCUSDT"
    async with echo_peer("/v3/ws/public/sbe", events=[frame]) as (url, _):
        client = bitget.sbe_public(base_url=url, timeout=2)
        try:
            await client.connect()
            assert await asyncio.wait_for(client.recv_bytes(), 3) == frame
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_hyperliquid_documented_legacy_web_data():
    subscription = {"type": "webData", "user": "0x" + "11" * 20}
    async with echo_peer() as (url, received):
        client = hyperliquid.PublicClient(base_url=url, timeout=2)
        try:
            await client.connect()
            await client.subscribe(subscription)
            assert await asyncio.wait_for(client.recv(), 3) == {
                "method": "subscribe",
                "subscription": subscription,
            }
        finally:
            await client.close()
    assert len(received) == 1


@asynccontextmanager
async def prediction_peer(event):
    received = []

    async def rest(request):
        params = dict(request.query)
        if not params:
            params = dict(await request.post())
        received.append((request.method, request.path, params))
        return web.json_response(
            {"listenKey": "prediction-key"} if request.method == "POST" else {}
        )

    async def socket(request):
        assert request.path == "/ws/prediction-key"
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        await ws.send_json(event)
        async for _ in ws:
            pass
        return ws

    app = web.Application()
    app.router.add_route("*", "/api/v3/listenKey", rest)
    app.router.add_get("/ws/prediction-key", socket)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    base = f"http://127.0.0.1:{runner.addresses[0][1]}"
    try:
        yield base, base.replace("http:", "ws:"), received
    finally:
        await runner.cleanup()


@pytest.mark.asyncio
@pytest.mark.parametrize("testnet", [False, True])
@pytest.mark.parametrize(
    "event",
    [
        {
            "e": "outboundAccountPosition",
            "B": [{"a": "SLP25", "f": "10282.42029415", "l": "653.00000001"}],
            "T": 1649926447190,
            "E": 1649926447205,
            "m": "WITHDRAW",
        },
        {
            "e": "executionReport",
            "s": "BTC_UP_DOWN_5M_1778483280_YUSDT",
            "X": "PARTIALLY_FILLED",
            "i": 27,
        },
    ],
)
async def test_prediction_private_listen_key_and_events(testnet, event):
    async with prediction_peer(event) as (http_url, ws_url, received):
        client = aster.PredictionPrivateClient(
            "0x" + "11" * 20,
            "0x" + "11" * 32,
            testnet=testnet,
            http_base_url=http_url,
            ws_base_url=ws_url,
            timeout=2,
        )
        try:
            assert await client.connect() == "prediction-key"
            assert await asyncio.wait_for(client.recv(), 3) == event
            await client.keep_alive()
        finally:
            await client.close()
    assert [(method, path) for method, path, _ in received] == [
        (method, "/api/v3/listenKey") for method in ("POST", "PUT", "DELETE")
    ]
    for method, _, params in received:
        assert len(params["signature"]) == 132
        assert params["signer"] == "0x" + "11" * 20
        if method != "POST":
            assert params["listenKey"] == "prediction-key"
