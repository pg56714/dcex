"""Native Coin-M streams against a local gzip WebSocket and listen-key peer."""

# ruff: noqa: D103
import gzip
import json
from typing import Any

import pytest
from aiohttp import WSMsgType, web

from dcex.ws.bingx import PrivateClient, PublicClient


@pytest.mark.asyncio
async def test_coin_swap_channels_and_automatic_private_events() -> None:
    subscriptions: list[str] = []
    token_calls: list[str] = []
    private_event = {"e": "ACCOUNT_UPDATE", "a": {"B": [{"a": "BTC", "wb": "0.1"}]}}

    async def token(request: web.Request) -> web.Response:
        assert request.headers["X-BX-APIKEY"] == "key"
        token_calls.append(request.method)
        return web.json_response({"listenKey": "coin-token"})

    async def socket(request: web.Request) -> web.WebSocketResponse:
        peer = web.WebSocketResponse()
        await peer.prepare(request)
        if request.query.get("listenKey"):
            assert request.query["listenKey"] == "coin-token"
            await peer.send_bytes(gzip.compress(b"Ping"))
        async for message in peer:
            if message.type != WSMsgType.TEXT:
                continue
            if message.data == "Pong":
                await peer.send_bytes(gzip.compress(json.dumps(private_event).encode()))
                continue
            data: dict[str, Any] = message.json()
            subscriptions.append(data["dataType"])
            await peer.send_bytes(gzip.compress(json.dumps(data).encode()))
        return peer

    app = web.Application()
    app.router.add_route("*", "/openApi/user/auth/userDataStream", token)
    app.router.add_get("/market", socket)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = runner.addresses[0][1]
    ws_url = f"ws://127.0.0.1:{port}/market"
    public = PublicClient(market="coin_swap", base_url=ws_url, timeout=10)
    private = PrivateClient(
        "key",
        "secret",
        market="coin_swap",
        http_base_url=f"http://127.0.0.1:{port}",
        ws_base_url=ws_url,
        timeout=10,
    )
    try:
        await public.connect()
        for method, args, channel in [
            ("subscribe_trades", ("BTC-USD-SWAP",), "BTC-USD@trade"),
            ("subscribe_ticker", ("BTC-USD-SWAP",), "BTC-USD@ticker"),
            ("subscribe_orderbook", ("BTC-USD-SWAP", 20), "BTC-USD@depth20"),
            ("subscribe_klines", ("BTC-USD-SWAP", "1m"), "BTC-USD@kline_1m"),
            ("subscribe_last_price", ("BTC-USD-SWAP",), "BTC-USD@lastPrice"),
            ("subscribe_mark_price", ("BTC-USD-SWAP",), "BTC-USD@markPrice"),
            ("subscribe_book_ticker", ("BTC-USD-SWAP",), "BTC-USD@bookTicker"),
        ]:
            await getattr(public, method)(*args)
            event = await public.recv()
            assert isinstance(event, dict) and event["dataType"] == channel
        with pytest.raises((ValueError, RuntimeError), match="BASE-USD"):
            await public.subscribe_trades("BTC-USDT-SWAP")
        with pytest.raises((ValueError, RuntimeError), match="speed"):
            await public.subscribe_orderbook("BTC-USD-SWAP", 20, "200ms")
        assert await private.connect() == "coin-token"
        assert await private.recv() == private_event
        await private.keep_alive()
        with pytest.raises((ValueError, RuntimeError), match="automatically"):
            await private.subscribe_orders()
    finally:
        await public.close()
        await private.close()
        await runner.cleanup()
    assert len(subscriptions) == 7
    assert token_calls[:2] == ["POST", "PUT"]
