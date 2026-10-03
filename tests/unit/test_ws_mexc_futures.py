"""MEXC contract WebSocket tests through the real native bridge."""

# ruff: noqa: D103
import hashlib
import hmac
import json
from typing import Any

import pytest
from aiohttp import web

from dcex.ws.mexc import FuturesPrivateClient, FuturesPublicClient


@pytest.mark.asyncio
@pytest.mark.parametrize("private", [False, True])
async def test_contract_stream_wire_protocol(private: bool) -> None:
    received: list[dict[str, Any]] = []

    async def handler(request: web.Request) -> web.WebSocketResponse:
        socket = web.WebSocketResponse()
        await socket.prepare(request)
        async for message in socket:
            event = json.loads(message.data)
            received.append(event)
            if event["method"] == "login":
                param = event["param"]
                expected = hmac.new(
                    b"secret", ("key" + param["reqTime"]).encode(), hashlib.sha256
                ).hexdigest()
                assert param["signature"] == expected
                await socket.send_json({"channel": "rs.login", "data": "success"})
            else:
                await socket.send_json({"channel": "ack", "method": event["method"]})
        return socket

    app = web.Application()
    app.router.add_get("/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = runner.addresses[0][1]
    url = f"ws://127.0.0.1:{port}/"
    client = (
        FuturesPrivateClient("key", "secret", base_url=url)
        if private
        else FuturesPublicClient(base_url=url)
    )
    try:
        await client.connect()
        calls = [
            (client.subscribe_tickers, (), "tickers", {}),
            (client.subscribe_ticker, ("BTC_USDT",), "ticker", {"symbol": "BTC_USDT"}),
            (client.subscribe_trades, ("BTC_USDT",), "deal", {"symbol": "BTC_USDT"}),
            (client.subscribe_orderbook, ("BTC_USDT",), "depth", {"symbol": "BTC_USDT"}),
            (
                client.subscribe_orderbook_step,
                ("BTC_USDT", "10"),
                "depth.step",
                {"symbol": "BTC_USDT", "step": "10"},
            ),
            (
                client.subscribe_klines,
                ("BTC_USDT", "1h"),
                "kline",
                {"symbol": "BTC_USDT", "interval": "Min60"},
            ),
            (
                client.subscribe_funding_rate,
                ("BTC_USDT",),
                "funding.rate",
                {"symbol": "BTC_USDT"},
            ),
            (
                client.subscribe_index_price,
                ("BTC_USDT",),
                "index.price",
                {"symbol": "BTC_USDT"},
            ),
            (client.subscribe_fair_price, ("BTC_USDT",), "fair.price", {"symbol": "BTC_USDT"}),
        ]
        for call, args, channel, params in calls:
            await call(*args)
            await client.recv()
            assert received[-1] == {"method": f"sub.{channel}", "param": params, "gzip": False}
        for channel in ["contract", "event.contract"]:
            await client.subscribe(channel)
            await client.recv()
            assert received[-1] == {"method": f"sub.{channel}"}
            await client.unsubscribe(channel)
            await client.recv()
            assert received[-1] == {"method": f"unsub.{channel}"}
        if isinstance(client, FuturesPrivateClient):
            await client.set_private_filters([{"filter": "position", "rules": ["BTC_USDT"]}])
            await client.recv()
            assert received[-1]["param"]["filters"][0]["rules"] == ["BTC_USDT"]
        await client.unsubscribe("depth", "BTC_USDT")
        await client.recv()
        assert received[-1]["method"] == "unsub.depth"
        await client.ping()
        await client.recv()
        assert received[-1] == {"method": "ping"}
    finally:
        await client.close()
        await runner.cleanup()
