"""Exercise native Kraken Spot v2 trading with an offline HTTP/WS peer."""

# ruff: noqa: D103
from __future__ import annotations

import base64
from typing import Any

import pytest
from aiohttp import WSMsgType, web

from dcex.ws.kraken import PrivateClient


@pytest.mark.asyncio
async def test_trading_token_and_raw_outcomes() -> None:
    received: list[dict[str, Any]] = []

    async def token(request: web.Request) -> web.Response:
        assert request.headers["API-Key"] == "key"
        assert request.headers["API-Sign"]
        return web.json_response({"error": [], "result": {"token": "ws-token", "expires": 900}})

    async def handler(request: web.Request) -> web.WebSocketResponse:
        peer = web.WebSocketResponse()
        await peer.prepare(request)
        async for message in peer:
            if message.type != WSMsgType.TEXT:
                continue
            data = message.json()
            received.append(data)
            assert data["params"]["token"] == "ws-token"
            await peer.send_json({"channel": "executions", "type": "update", "data": []})
            await peer.send_json(
                {
                    "method": data["method"],
                    "req_id": data["req_id"],
                    "success": False,
                    "error": "EOrder:fixture",
                }
            )
        return peer

    app = web.Application()
    app.router.add_post("/0/private/GetWebSocketsToken", token)
    app.router.add_get("/ws", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = runner.addresses[0][1]
    client = PrivateClient(
        "key",
        base64.b64encode(b"secret").decode(),
        spot_http_base_url=f"http://127.0.0.1:{port}",
        ws_base_url=f"ws://127.0.0.1:{port}/ws",
    )
    try:
        assert await client.connect() == "ws-token"
        cases = [
            (
                "add_order",
                {
                    "symbol": "BTC/USD",
                    "order_type": "limit",
                    "side": "buy",
                    "order_qty": 0.5,
                    "limit_price": 100.0,
                    "conditional": {"order_type": "stop-loss", "trigger_price": 90.0},
                },
            ),
            ("amend_order", {"order_id": "ORDERX-IDXXX-XXXXX3", "order_qty": 0.25}),
            ("cancel_order", {"order_userref": [123, 456]}),
            (
                "batch_add",
                {
                    "symbol": "BTC/USD",
                    "orders": [
                        {
                            "order_type": "limit",
                            "side": "buy",
                            "order_qty": 1.0,
                            "limit_price": 100.0,
                        },
                        {
                            "order_type": "limit",
                            "side": "sell",
                            "order_qty": 1.0,
                            "limit_price": 101.0,
                        },
                    ],
                },
            ),
            ("batch_cancel", {"orders": ["123", "ORDERX-IDXXX-XXXXX3"]}),
            ("cancel_all", {}),
            ("cancel_after", {"timeout": 60}),
        ]
        previous = 0
        for method, params in cases:
            request_id = await client.trade_request(method, params)
            assert request_id > previous
            previous = request_id
            assert (await client.recv())["channel"] == "executions"
            assert await client.recv() == {
                "method": method,
                "req_id": request_id,
                "success": False,
                "error": "EOrder:fixture",
            }
            assert received[-1]["params"] == {**params, "token": "ws-token"}
    finally:
        await client.close()
        await runner.cleanup()


@pytest.mark.asyncio
async def test_level3_token_depth_and_raw_book() -> None:
    from dcex.ws.kraken import Level3Client

    received: list[dict[str, Any]] = []
    event = {
        "channel": "level3",
        "type": "snapshot",
        "data": [
            {
                "symbol": "BTC/USD",
                "bids": [
                    {
                        "order_id": "O123",
                        "limit_price": 100.0,
                        "order_qty": 1.0,
                        "timestamp": "2026-09-26T00:00:00.123456789Z",
                    }
                ],
                "asks": [],
                "checksum": 12345,
            }
        ],
    }

    async def token(request: web.Request) -> web.Response:
        assert request.headers["API-Key"] == "key"
        assert request.headers["API-Sign"]
        return web.json_response({"error": [], "result": {"token": "l3-token"}})

    async def handler(request: web.Request) -> web.WebSocketResponse:
        peer = web.WebSocketResponse()
        await peer.prepare(request)
        async for message in peer:
            if message.type == WSMsgType.TEXT:
                data = message.json()
                received.append(data)
                await peer.send_json(
                    {"method": data["method"], "success": True, "req_id": data["req_id"]}
                )
                if data["method"] == "subscribe":
                    await peer.send_json(event)
        return peer

    app = web.Application()
    app.router.add_post("/0/private/GetWebSocketsToken", token)
    app.router.add_get("/l3", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = runner.addresses[0][1]
    client = Level3Client(
        "key",
        base64.b64encode(b"secret").decode(),
        spot_http_base_url=f"http://127.0.0.1:{port}",
        ws_base_url=f"ws://127.0.0.1:{port}/l3",
    )
    try:
        for symbols, depth in [
            ([], 10),
            (["BTC-USD-SPOT"], 25),
            (["BTC-USD-SWAP"], 10),
            (["BTC/USD", "BTC-USD-SPOT"], 10),
        ]:
            with pytest.raises((ValueError, RuntimeError)):
                await client.subscribe_level3(symbols, depth)
        assert not received
        assert await client.connect() == "l3-token"
        req_id = await client.subscribe_level3(["BTC-USD-SPOT"], 100, False)
        assert (await client.recv())["req_id"] == req_id
        assert await client.recv() == event
        assert received[-1]["params"] == {
            "channel": "level3",
            "symbol": ["BTC/USD"],
            "depth": 100,
            "snapshot": False,
            "token": "l3-token",
        }
        req_id = await client.unsubscribe_level3(["BTC-USD-SPOT"], 100)
        assert (await client.recv())["req_id"] == req_id
        assert received[-1]["params"] == {
            "channel": "level3",
            "symbol": ["BTC/USD"],
            "depth": 100,
            "token": "l3-token",
        }
    finally:
        await client.close()
        await runner.cleanup()
