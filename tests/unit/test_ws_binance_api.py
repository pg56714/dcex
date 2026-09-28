"""Validate native Binance WS signing, duplex I/O and complete response delivery."""

# ruff: noqa: D103
from __future__ import annotations

import asyncio
import hashlib
import hmac
from typing import Any

import pytest
from aiohttp import WSMsgType, web

from dcex.ws.binance import FuturesApiClient, SpotApiClient


@pytest.mark.asyncio
@pytest.mark.parametrize("futures", [False, True])
async def test_signed_api_and_concurrent_receive(futures: bool) -> None:
    received: list[dict[str, Any]] = []

    async def handler(request: web.Request) -> web.WebSocketResponse:
        peer = web.WebSocketResponse()
        await peer.prepare(request)
        async for message in peer:
            if message.type != WSMsgType.TEXT:
                continue
            data = message.json()
            received.append(data)
            params = dict(data["params"])
            signature = params.pop("signature", None)
            if data["method"] not in {"depth", "userDataStream.start"}:
                payload = "&".join(
                    f"{key}={str(value).lower() if isinstance(value, bool) else value}"
                    for key, value in sorted(params.items())
                )
                assert (
                    signature == hmac.new(b"secret", payload.encode(), hashlib.sha256).hexdigest()
                )
                assert params["apiKey"] == "key"
                assert isinstance(params["timestamp"], int)
            else:
                assert signature is None
            if data["method"] == "order.place":
                assert params["quantity"] == "0.01000000"
                assert params["price"] == "52000.00"
                # The event and error must both survive; neither is a success ack.
                await peer.send_json({"event": {"e": "executionReport"}, "subscriptionId": 7})
                await peer.send_json(
                    {
                        "id": data["id"],
                        "status": 400,
                        "error": {"code": -2010, "msg": "rejected"},
                        "rateLimits": [{"count": 1}],
                    }
                )
            else:
                await peer.send_json({"id": data["id"], "status": 200, "result": {}})
        return peer

    app = web.Application()
    app.router.add_get("/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    url = f"ws://127.0.0.1:{runner.addresses[0][1]}/"
    client = (
        FuturesApiClient("key", "secret", base_url=url, timeout=30)
        if futures
        else SpotApiClient("key", "secret", base_url=url, timeout=30)
    )
    receive_started = asyncio.Event()
    pending = None

    async def receive_first() -> dict[str, Any]:
        receive_started.set()
        return await client.recv()

    try:
        await client.connect()
        # A pending read must not lock out a trading write.
        pending = asyncio.create_task(receive_first())
        await receive_started.wait()
        request_id = await asyncio.wait_for(
            client.place_order(
                {
                    "symbol": "BTCUSDT",
                    "side": "SELL",
                    "type": "LIMIT",
                    "timeInForce": "GTC",
                    "quantity": "0.01000000",
                    "price": "52000.00",
                    "timestamp": 1645423376532,
                }
            ),
            30,
        )
        assert (await pending)["event"]["e"] == "executionReport"
        response = await client.recv()
        assert response == {
            "id": request_id,
            "status": 400,
            "error": {"code": -2010, "msg": "rejected"},
            "rateLimits": [{"count": 1}],
        }
        next_id = await client.get_account()
        assert next_id > request_id
        assert (await client.recv())["id"] == next_id
        assert received[-1]["method"] == ("v2/account.status" if futures else "account.status")
        await client.get_orderbook({"symbol": "BTCUSDT", "limit": 10})
        await client.recv()
        assert received[-1]["params"] == {"symbol": "BTCUSDT", "limit": 10}
        if futures:
            await client.create_listen_key()
            await client.recv()
            assert received[-1]["params"] == {"apiKey": "key"}
        else:
            await client.subscribe_user_data()
            await client.recv()
            assert received[-1]["method"] == "userDataStream.subscribe.signature"
    finally:
        if pending is not None and not pending.done():
            pending.cancel()
            await asyncio.gather(pending, return_exceptions=True)
        await client.close()
        await runner.cleanup()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("futures", "method", "params", "message"),
    [
        (
            False,
            "order.place",
            {"symbol": "BTCUSDT", "side": "BUY", "type": "LIMIT", "quantity": 1.0},
            "decimal",
        ),
        (False, "order.cancel", {"symbol": "BTCUSDT"}, "required"),
        (
            False,
            "order.place",
            {"symbol": "BTCUSDT", "side": "BUY", "type": "LIMIT", "quantity": "1", "price": "2"},
            "timeInForce",
        ),
        (False, "order.cancel", {"symbol": "BTCUSDT", "orderId": "123"}, "JSON"),
        (False, "session.logon", {}, "Ed25519"),
        (False, "order.place", {"apiKey": "override"}, "managed"),
        (False, "orderList.place", {}, "unsupported"),
        (True, "account.status", {}, "unsupported"),
        (
            True,
            "order.place",
            {"symbol": "BTCUSDT", "side": "BUY", "type": "STOP_MARKET", "quantity": "1"},
            "algoOrder",
        ),
        (
            True,
            "algoOrder.place",
            {
                "algoType": "CONDITIONAL",
                "symbol": "BTCUSDT",
                "side": "SELL",
                "type": "STOP_MARKET",
                "closePosition": "true",
                "quantity": "1",
                "triggerPrice": "100",
            },
            "closePosition",
        ),
    ],
)
async def test_rejects_invalid_requests_before_network(
    futures: bool, method: str, params: dict[str, Any], message: str
) -> None:
    client = FuturesApiClient("key", "secret") if futures else SpotApiClient("key", "secret")
    with pytest.raises(ValueError, match=message):
        await client.request(method, params)


@pytest.mark.asyncio
async def test_coin_futures_methods_and_authentication() -> None:
    from dcex.ws.binance import CoinFuturesApiClient

    received: list[dict[str, Any]] = []

    async def handler(request: web.Request) -> web.WebSocketResponse:
        peer = web.WebSocketResponse()
        await peer.prepare(request)
        async for message in peer:
            if message.type != WSMsgType.TEXT:
                continue
            data = message.json()
            received.append(data)
            params = dict(data["params"])
            signature = params.pop("signature", None)
            assert params["apiKey"] == "key"
            if data["method"].startswith("userDataStream."):
                assert signature is None
                assert "timestamp" not in params
            else:
                assert isinstance(params["timestamp"], int)
                text = "&".join(
                    f"{k}={str(v).lower() if isinstance(v, bool) else v}"
                    for k, v in sorted(params.items())
                )
                assert signature == hmac.new(b"secret", text.encode(), hashlib.sha256).hexdigest()
            await peer.send_json(
                {"id": data["id"], "status": 200, "result": {"fixture": data["method"]}}
            )
        return peer

    app = web.Application()
    app.router.add_get("/ws-dapi/v1", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    client = CoinFuturesApiClient(
        "key", "secret", base_url=f"ws://127.0.0.1:{runner.addresses[0][1]}/ws-dapi/v1"
    )
    cases = [
        (
            "place_order",
            "order.place",
            {
                "symbol": "BTCUSD_PERP",
                "side": "BUY",
                "type": "LIMIT",
                "timeInForce": "GTC",
                "price": "60000",
                "quantity": "1",
            },
        ),
        (
            "amend_order",
            "order.modify",
            {
                "symbol": "BTCUSD_PERP",
                "side": "BUY",
                "quantity": "2",
                "priceMatch": "QUEUE",
                "orderId": 123,
            },
        ),
        ("cancel_order", "order.cancel", {"symbol": "BTCUSD_PERP", "orderId": 123}),
        ("get_order", "order.status", {"symbol": "BTCUSD_PERP", "orderId": 123}),
        ("get_account", "account.status", {}),
        ("get_balance", "account.balance", {}),
        ("get_positions", "account.position", {"marginAsset": "BTC", "pair": "BTCUSD"}),
        ("create_listen_key", "userDataStream.start", {}),
        ("keep_alive_listen_key", "userDataStream.ping", {}),
        ("close_listen_key", "userDataStream.stop", {}),
    ]
    try:
        with pytest.raises(ValueError):
            await client.place_order(
                {"symbol": "BTCUSD_PERP", "side": "SELL", "type": "STOP_MARKET", "quantity": "1"}
            )
        await client.connect()
        for wrapper, method, params in cases:
            request_id = await getattr(client, wrapper)(params)
            assert await client.recv() == {
                "id": request_id,
                "status": 200,
                "result": {"fixture": method},
            }
            actual = dict(received[-1]["params"])
            for key in ["apiKey", "timestamp", "signature"]:
                actual.pop(key, None)
            assert actual == params
    finally:
        await client.close()
        await runner.cleanup()


@pytest.mark.asyncio
async def test_margin_listen_token_without_session_credentials() -> None:
    received: list[dict[str, Any]] = []

    async def handler(request: web.Request) -> web.WebSocketResponse:
        peer = web.WebSocketResponse()
        await peer.prepare(request)
        async for message in peer:
            data = message.json()
            received.append(data)
            await peer.send_json({"id": data["id"], "status": 200, "result": {"subscriptionId": 9}})
        return peer

    app = web.Application()
    app.router.add_get("/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    client = SpotApiClient(base_url=f"ws://127.0.0.1:{runner.addresses[0][1]}/")
    try:
        await client.connect()
        request_id = await client.subscribe_user_data_listen_token("token+value/=")
        assert (await client.recv())["id"] == request_id
        assert received == [
            {
                "id": request_id,
                "method": "userDataStream.subscribe.listenToken",
                "params": {"listenToken": "token+value/="},
            }
        ]
        with pytest.raises(ValueError, match="listenToken"):
            await client.request("userDataStream.subscribe.listenToken", {})
    finally:
        await client.close()
        await runner.cleanup()
