"""Offline coverage for ws ondo."""

import asyncio
import hashlib
import hmac
import json
from contextlib import asynccontextmanager

import pytest
from aiohttp import WSMsgType, web

from dcex.ws import ondo

ONDO_PUBLIC = [
    "topOfBooksPerps",
    "depthBooksPerps",
    "tradesPerps",
    "fundingRatesPerps",
    "markPricesPerps",
    "kLinePerps",
    "topOfBooksSpot",
    "depthBooksSpot",
    "tradesSpot",
]

ONDO_PRIVATE = [
    "ordersPerps",
    "fillsPerps",
    "positionsPerps",
    "balancePerps",
    "liquidationPerps",
    "liquidationAnnouncementsPerps",
    "marginTransfersPerps",
    "ordersSummariesPerps",
    "fundingPaymentsPerps",
    "deposits",
    "withdrawals",
    "cancelAllOrdersAfterPerps",
]


@asynccontextmanager
async def authenticated_peer(exchange, events=()):
    received = []

    async def socket(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for frame in ws:
            if frame.type != WSMsgType.TEXT:
                continue
            message = json.loads(frame.data)
            received.append(message)
            if message.get("op", message.get("method")) == "login":
                if exchange == "ondo":
                    args = message["args"]
                    assert args["key"] == "key"
                    assert (
                        args["sign"]
                        == hmac.new(
                            b"secret",
                            (args["time"] + "ondo_perps_ws_login").encode(),
                            hashlib.sha256,
                        ).hexdigest()
                    )
                    await ws.send_json({"type": "loggedIn"})
                else:
                    args = message["param"]
                    assert args["apiKey"] == "key"
                    assert (
                        args["signature"]
                        == hmac.new(
                            b"secret", ("key" + args["reqTime"]).encode(), hashlib.sha256
                        ).hexdigest()
                    )
                    await ws.send_json({"channel": "rs.login", "data": "success"})
                for event in events:
                    await ws.send_json(event)
            else:
                await ws.send_json(message)
        return ws

    app = web.Application()
    app.router.add_get("/ws", socket)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    try:
        yield f"ws://127.0.0.1:{runner.addresses[0][1]}/ws", received
    finally:
        await runner.cleanup()


@pytest.mark.asyncio
@pytest.mark.parametrize("channel", ONDO_PUBLIC + ONDO_PRIVATE)
async def test_ondo_connect_login_ping_and_subscriptions(channel):
    private = channel in ONDO_PRIVATE
    async with authenticated_peer("ondo") as (url, received):
        client = (
            ondo.PrivateClient("key", "secret", base_url=url, timeout=10)
            if private
            else ondo.PublicClient(base_url=url, timeout=10)
        )
        try:
            await asyncio.wait_for(client.connect(), 10)
            assert client.is_connected()
            await client.ping()
            assert await asyncio.wait_for(client.recv(), 10) == {"op": "ping"}
            expected = {"op": "subscribe", "channel": channel}
            if channel == "cancelAllOrdersAfterPerps":
                await client.subscribe_cancel_all_orders_after(60)
                expected["timeout_seconds"] = 60
            elif channel == "kLinePerps":
                await client.subscribe_klines("BTC-USD.P", "1H")
                expected.update(markets=["BTC-USD.P"], resolution="1H")
            else:
                market = "SPY-USDC" if channel.endswith("Spot") else "BTC-USD.P"
                await client.subscribe(
                    channel,
                    [market] if channel == "ordersSummariesPerps" or not private else None,
                )
                if channel == "ordersSummariesPerps" or not private:
                    expected["markets"] = [market]
            assert await asyncio.wait_for(client.recv(), 10) == expected
        finally:
            await client.close()
        assert not client.is_connected()
    assert received[-1] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("method,channel", [
    ("subscribe_spot_top_of_book", "topOfBooksSpot"),
    ("subscribe_spot_depth", "depthBooksSpot"),
    ("subscribe_spot_trades", "tradesSpot"),
])
@pytest.mark.parametrize("markets,expected", [
    ("SPY-USDC", ["SPY-USDC"]),
    ("SPY-USDC-SPOT", ["SPY-USDC"]),
    (["SPY-USDC-SPOT", "QQQ-USDC"], ["SPY-USDC", "QQQ-USDC"]),
])
async def test_ondo_public_spot_helpers_send_no_authentication(method, channel, markets, expected):
    async with authenticated_peer("ondo") as (url, received):
        client = ondo.PublicClient(base_url=url, timeout=10)
        try:
            await client.connect()
            await getattr(client, method)(markets)
            assert await client.recv() == {"op": "subscribe", "channel": channel, "markets": expected}
            await client.unsubscribe(channel, markets)
            assert await client.recv() == {"op": "unsubscribe", "channel": channel, "markets": expected}
            assert all(event["op"] != "login" for event in received)
        finally:
            await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("method,channel", [
    ("subscribe_top_of_book", "topOfBooksPerps"),
    ("subscribe_depth", "depthBooksPerps"),
    ("subscribe_trades", "tradesPerps"),
    ("subscribe_funding_rates", "fundingRatesPerps"),
    ("subscribe_mark_prices", "markPricesPerps"),
])
async def test_ondo_public_perp_helpers_map_unified_symbols(method, channel):
    async with authenticated_peer("ondo") as (url, received):
        client = ondo.PublicClient(base_url=url, timeout=10)
        try:
            await client.connect()
            await getattr(client, method)(["BTC-USD-SWAP", "ETH-USD.P"])
            assert await client.recv() == {
                "op": "subscribe",
                "channel": channel,
                "markets": ["BTC-USD.P", "ETH-USD.P"],
            }
            with pytest.raises(ValueError, match="invalid Ondo product symbol"):
                await getattr(client, method)("BTC-USD")
            assert all(event["op"] != "login" for event in received)
        finally:
            await client.close()
