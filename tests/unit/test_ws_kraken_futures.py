"""Exercise Kraken Derivatives native streams against a local WebSocket peer."""

# ruff: noqa: D103
from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Any

import pytest
from aiohttp import WSMsgType, web

from dcex.ws.kraken import FuturesPrivateClient, FuturesPublicClient


@pytest.mark.asyncio
@pytest.mark.parametrize("private", [False, True])
async def test_futures_feeds_and_challenge_signature(private: bool) -> None:
    received: list[dict[str, Any]] = []
    challenge = "226aee50-88fc-4618-a42a-34f7709570b2"
    expected = base64.b64encode(
        hmac.new(b"secret", hashlib.sha256(challenge.encode()).digest(), hashlib.sha512).digest()
    ).decode()

    async def handler(request: web.Request) -> web.WebSocketResponse:
        peer = web.WebSocketResponse()
        await peer.prepare(request)
        async for message in peer:
            if message.type != WSMsgType.TEXT:
                continue
            data = message.json()
            received.append(data)
            if data.get("event") == "challenge":
                assert data == {"event": "challenge", "api_key": "key"}
                await peer.send_json({"event": "challenge", "message": challenge})
            else:
                await peer.send_json({"event": "subscribed", "feed": data["feed"]})
        return peer

    app = web.Application()
    app.router.add_get("/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    url = f"ws://127.0.0.1:{runner.addresses[0][1]}/"
    client = (
        FuturesPrivateClient("key", base64.b64encode(b"secret").decode(), base_url=url)
        if private
        else FuturesPublicClient(base_url=url)
    )
    try:
        await client.connect()
        for feed in ["book", "ticker", "ticker_lite", "trade", "heartbeat"]:
            products = None if feed == "heartbeat" else ["BTC-USD-SWAP", "PI_XBTUSD"]
            await client.subscribe(feed, products)
            assert (await client.recv())["feed"] == feed
            assert "api_key" not in received[-1]
            if products:
                assert received[-1]["product_ids"] == ["PF_XBTUSD", "PI_XBTUSD"]
        if private:
            for feed in [
                "fills",
                "open_orders",
                "open_orders_verbose",
                "open_position",
                "balances",
                "account_log",
                "notifications",
            ]:
                await client.subscribe(feed)
                await client.recv()
                assert received[-1] == {
                    "event": "subscribe",
                    "feed": feed,
                    "api_key": "key",
                    "original_challenge": challenge,
                    "signed_challenge": expected,
                }
                await client.unsubscribe(feed)
                await client.recv()
                assert received[-1]["event"] == "unsubscribe"
                assert received[-1]["signed_challenge"] == expected
        else:
            with pytest.raises(Exception, match="credentials"):
                await client.subscribe("fills")
        with pytest.raises(Exception, match="product_ids"):
            await client.subscribe("balances", ["PF_XBTUSD"])
        with pytest.raises(Exception, match="unsupported feed"):
            await client.subscribe("sendorder")
    finally:
        await client.close()
        await runner.cleanup()
