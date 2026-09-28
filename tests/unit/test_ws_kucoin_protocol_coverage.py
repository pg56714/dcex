"""KuCoin official Classic and Pro subscription requests reach real native sockets."""

import asyncio
import base64
import hashlib
import hmac
import json
from contextlib import asynccontextmanager

import pytest
from aiohttp import WSMsgType, web

from dcex.ws.kucoin import PrivateClient, ProClient, PublicClient
from tests.unit.ws_official_examples import json_examples, load_operations

OPERATIONS = load_operations("kucoin")
CASES = [
    {"row": op["row"], "message": msg}
    for op in OPERATIONS
    for msg in json_examples(op["text"])
    if isinstance(msg, dict)
    and (
        msg.get("action") == "SUBSCRIBE"
        or msg.get("type") == "subscribe"
        or bool(msg.get("op"))
        and bool(msg.get("args"))
    )
]


def signature(text):
    return base64.b64encode(hmac.new(b"secret", text.encode(), hashlib.sha256).digest()).decode()


@asynccontextmanager
async def peer(profile, reject_auth=False):
    received = []
    requests = []
    welcome = {"message": "welcome", "sessionId": "local", "pingInterval": 18000}

    async def socket(request):
        requests.append({"path": request.path, "query": dict(request.query)})
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        authenticated = False
        challenge = '{ "timestamp": 1742175983882, "sessionId": "local-session" }'
        if profile == "trade_v1":
            await ws.send_str(challenge)
        if profile not in {"trade", "trade_v1", "classic"}:
            await ws.send_json(welcome)
        async for frame in ws:
            if frame.type == WSMsgType.TEXT:
                if profile == "trade_v1" and not authenticated:
                    received.append({"challenge_signature": frame.data})
                    assert frame.data == signature(challenge)
                    authenticated = True
                    await ws.send_json(
                        {"data": "denied" if reject_auth else "welcome", "pingInterval": 18000}
                    )
                    continue
                message = json.loads(frame.data)
                received.append(message)
                if message.get("op") == "auth":
                    if reject_auth:
                        await ws.send_json({"result": False, "message": "auth failed"})
                    elif profile == "trade":
                        await ws.send_json({"data": "welcome", "pingInterval": 18000})
                    else:
                        await ws.send_json({"result": True})
                else:
                    await ws.send_json(message)
        return ws

    async def bullet(request):
        requests.append(
            {"path": request.path, "method": request.method, "headers": dict(request.headers)}
        )
        return web.json_response(
            {
                "code": "200000",
                "data": {
                    "token": "local-token",
                    "instanceServers": [{"endpoint": ws_url}],
                },
            }
        )

    app = web.Application()
    app.router.add_get("/socket", socket)
    app.router.add_post("/api/v1/bullet-public", bullet)
    app.router.add_post("/api/v1/bullet-private", bullet)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    url = f"http://127.0.0.1:{runner.addresses[0][1]}"
    ws_url = url.replace("http:", "ws:") + "/socket"
    try:
        yield url, ws_url, received, requests
    finally:
        await runner.cleanup()


def profile_for(case):
    msg = case["message"]
    if "op" in msg:
        return "trade_v1" if case["row"] in {4668, 4669, 4684, 4685, 4686} else "trade"
    if "topic" in msg:
        return "classic"
    if case["row"] in {*range(4618, 4625), *range(4670, 4677)}:
        return "private"
    return (
        "public_futures"
        if msg.get("tradeType") == "FUTURES"
        or msg.get("channel") in {"mark-price", "funding-fee", "funding-fee-all-symbols"}
        else "public_spot"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CASES, ids=lambda c: str(c["row"]))
async def test_official_message(case):
    profile = profile_for(case)
    msg = case["message"]
    async with peer(profile) as (url, ws_url, received, requests):
        if profile == "classic":
            private = msg.get("privateChannel", False) or case["row"] in {
                *range(4640, 4644),
                *range(4646, 4652),
                *range(4662, 4668),
            }
            market = "futures" if 4652 <= case["row"] <= 4667 else "spot"
            kwargs = {
                "timeout": 2,
                "market": market,
                "spot_http_base_url": url,
                "futures_http_base_url": url,
            }
            client = (
                PrivateClient("key", "secret", "passphrase", **kwargs)
                if private
                else PublicClient(**kwargs)
            )
        else:
            client = ProClient(
                profile,
                api_key="key",
                api_secret="secret",
                passphrase="passphrase",
                base_url=ws_url,
                timeout=2,
            )
        try:
            await asyncio.wait_for(client.connect(), 3)
            if profile == "classic":
                request_id = await client.subscribe(msg["topic"])
                expected = {
                    "id": request_id,
                    "type": "subscribe",
                    "topic": msg["topic"],
                    "privateChannel": bool(private),
                    "response": True,
                }
            elif profile in {"trade", "trade_v1"}:
                await client.send_operation(msg["id"], msg["op"], msg["args"])
                expected = msg
            else:
                await client.subscribe(msg)
                expected = msg
            assert await asyncio.wait_for(client.recv(), 3) == expected
            assert received[-1] == expected
            if profile not in {"trade", "trade_v1"}:
                if profile == "classic":
                    expected = {
                        **expected,
                        "id": await client.unsubscribe(msg["topic"]),
                        "type": "unsubscribe",
                    }
                else:
                    await client.unsubscribe(msg)
                    expected = {**msg, "action": "UNSUBSCRIBE"}
                assert await asyncio.wait_for(client.recv(), 3) == expected
        finally:
            await client.close()
    if profile in {"private", "trade"}:
        auth = received[0]
        timestamp = auth["kc-api-timestamp"]
        assert timestamp.isdigit()
        assert auth == {
            "op": "auth",
            "kc-api-key": "key",
            "kc-api-timestamp": timestamp,
            "kc-api-sign": signature(timestamp + "POST/api/websocket/users/verify"),
            "kc-api-passphrase": signature("passphrase"),
        }
    elif profile == "trade_v1":
        query = requests[0]["query"]
        assert query == {
            "apikey": "key",
            "timestamp": query["timestamp"],
            "sign": signature("key" + query["timestamp"]),
            "passphrase": signature("passphrase"),
        }
        assert received[0]["challenge_signature"] == signature(
            '{ "timestamp": 1742175983882, "sessionId": "local-session" }'
        )
    elif profile == "classic":
        assert requests[0]["path"] == "/api/v1/bullet-" + ("private" if private else "public")
        assert requests[0]["method"] == "POST"
        assert requests[1]["query"]["token"] == "local-token"
        if private:
            headers = {k.lower(): v for k, v in requests[0]["headers"].items()}
            assert headers["kc-api-sign"] == signature(
                headers["kc-api-timestamp"] + "POST/api/v1/bullet-private"
            )


@pytest.mark.asyncio
@pytest.mark.parametrize("profile", ["private", "trade", "trade_v1"])
async def test_pro_auth_failure_closes_connection(profile):
    async with peer(profile, reject_auth=True) as (_, url, received, _):
        client = ProClient(
            profile,
            api_key="key",
            api_secret="secret",
            passphrase="passphrase",
            base_url=url,
            timeout=2,
        )
        try:
            with pytest.raises(RuntimeError, match="authentication rejected"):
                await asyncio.wait_for(client.connect(), 3)
            assert client._native_client.is_connected() is False
            assert len(received) == 1
        finally:
            await client.close()


def test_pro_default_urls():
    for profile, url in {
        "public_spot": "wss://x-push-spot.kucoin.com",
        "public_futures": "wss://x-push-futures.kucoin.com",
        "private": "wss://wsapi-push.kucoin.com",
        "trade": "wss://wsapi.kucoin.com/v2/private",
        "trade_v1": "wss://wsapi.kucoin.com/v1/private",
    }.items():
        client = ProClient(profile, api_key="key", api_secret="secret", passphrase="passphrase")
        assert client._native_client.url() == url
