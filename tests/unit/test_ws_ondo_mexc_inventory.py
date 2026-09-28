"""Exercise authenticated protocol events and complete Ondo subscription shapes."""

import asyncio
import hashlib
import hmac
import json
from contextlib import asynccontextmanager

import pytest
from aiohttp import WSMsgType, web

from dcex.ws import mexc, ondo

ONDO_PUBLIC = [
    "topOfBooksPerps",
    "depthBooksPerps",
    "tradesPerps",
    "fundingRatesPerps",
    "markPricesPerps",
    "kLinePerps",
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
            ondo.PrivateClient("key", "secret", base_url=url, timeout=2)
            if private
            else ondo.PublicClient(base_url=url, timeout=2)
        )
        try:
            await asyncio.wait_for(client.connect(), 3)
            assert client.is_connected()
            await client.ping()
            assert await asyncio.wait_for(client.recv(), 3) == {"op": "ping"}
            expected = {"op": "subscribe", "channel": channel}
            if channel == "cancelAllOrdersAfterPerps":
                await client.subscribe_cancel_all_orders_after(60)
                expected["timeout_seconds"] = 60
            elif channel == "kLinePerps":
                await client.subscribe_klines("BTC-PERP", "1H")
                expected.update(markets=["BTC-PERP"], resolution="1H")
            else:
                await client.subscribe(
                    channel,
                    ["BTC-PERP"] if channel == "ordersSummariesPerps" or not private else None,
                )
                if channel == "ordersSummariesPerps" or not private:
                    expected["markets"] = ["BTC-PERP"]
            assert await asyncio.wait_for(client.recv(), 3) == expected
        finally:
            await client.close()
        assert not client.is_connected()
    assert received[-1] == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("channel", ["push.personal.plan.order", "push.personal.position"])
async def test_mexc_deduction_event_preserved(channel):
    # The official page names different channels in its sample and prose.
    # Preserve either raw event; ledger records that unresolved inconsistency.
    event = {
        "channel": channel,
        "data": {"currency": "USDT", "deductFee": 0.1125, "convertSettleFee": 0.1125},
        "ts": 1760942212000,
    }
    async with authenticated_peer("mexc", events=[event]) as (url, received):
        client = mexc.FuturesPrivateClient("key", "secret", base_url=url, timeout=2)
        try:
            await asyncio.wait_for(client.connect(), 3)
            assert await asyncio.wait_for(client.recv(), 3) == event
        finally:
            await client.close()
    assert len(received) == 1


@pytest.mark.asyncio
async def test_mexc_spot_subscription_and_protobuf_passthrough():
    from tests.unit.ws_inventory_peer import echo_peer

    # Valid opaque protobuf bytes: this SDK returns frames for caller-side decoding.
    frame = b"\x08\x96\x01"
    stream = "spot@public.aggre.depth.v3.api.pb@100ms@BTCUSDT"
    async with echo_peer("/ws", events=[frame]) as (url, received):
        client = mexc.PublicClient(base_url=url, timeout=2)
        try:
            await asyncio.wait_for(client.connect(), 3)
            assert await asyncio.wait_for(client.recv(), 3) == frame
            for method, action in (
                (client.subscribe, "SUBSCRIPTION"),
                (client.unsubscribe, "UNSUBSCRIPTION"),
            ):
                await method([stream])
                event = await asyncio.wait_for(client.recv(), 3)
                assert event["method"] == action
                assert event["params"] == [stream]
            await client.ping()
            assert (await asyncio.wait_for(client.recv(), 3))["method"] == "PING"
        finally:
            await client.close()
    assert len(received) == 3
