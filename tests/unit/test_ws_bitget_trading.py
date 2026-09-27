"""Exercise native Bitget trading frames and partial acknowledgements locally."""

# ruff: noqa: D103
import json
from typing import Any

import pytest
from aiohttp import WSMsgType, web

from dcex.ws.bitget import PrivateClient


@pytest.mark.asyncio
@pytest.mark.parametrize("uta", [False, True])
async def test_trading_wire_protocol_and_partial_results(uta: bool) -> None:
    frames: list[dict[str, Any]] = []
    partial = {
        "event": "trade",
        "id": "batch",
        "code": "0",
        "args": [{"code": "0", "orderId": "1"}, {"code": "25571", "msg": "unchanged"}],
    }

    async def socket(request: web.Request) -> web.WebSocketResponse:
        peer = web.WebSocketResponse()
        await peer.prepare(request)
        async for message in peer:
            if message.type != WSMsgType.TEXT:
                continue
            frame = message.json()
            if frame["op"] == "login":
                assert frame["args"][0]["apiKey"] == "key"
                await peer.send_json({"event": "login", "code": "0"})
            else:
                frames.append(frame)
                await peer.send_json(partial if frame.get("topic") == "batch-modify" else frame)
        return peer

    app = web.Application()
    path = "/v3/ws/private" if uta else "/v2/ws/private"
    app.router.add_get(path, socket)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    client = PrivateClient(
        "key",
        "secret",
        "pass",
        timeout=2,
        base_url=f"ws://127.0.0.1:{runner.addresses[0][1]}{path}",
    )
    try:
        await client.connect()
        if uta:
            order = {
                "symbol": "BTCUSDT",
                "orderType": "limit",
                "price": "123.4500",
                "qty": "0.001",
                "side": "buy",
                "receiveWindow": "5000",
            }
            await client.place_order("single", order, category="spot", request_time=1700000000000)
            assert await client.recv() == {
                "op": "trade",
                "id": "single",
                "topic": "place-order",
                "category": "spot",
                "requestTime": "1700000000000",
                "args": [order],
            }
            batch_order = {k: v for k, v in order.items() if k != "receiveWindow"}
            await client.place_batch_orders("place", [batch_order], category="spot")
            assert (await client.recv())["topic"] == "batch-place"
            await client.modify_order(
                "modify", {"orderId": "1", "price": "124", "requestId": 123}, category="spot"
            )
            assert (await client.recv())["args"][0]["requestId"] == 123
            await client.modify_batch_orders(
                "batch", [{"orderId": "1", "qty": "2"}, {"orderId": "2", "qty": "3"}]
            )
            assert await client.recv() == partial
            await client.cancel_order("cancel", {"clientOid": "client-1"})
            assert (await client.recv())["args"] == [{"clientOid": "client-1"}]
            await client.cancel_batch_orders("cancels", [{"orderId": "1"}, {"orderId": "2"}])
            assert (await client.recv())["topic"] == "batch-cancel"
        else:
            for inst_type in ["SPOT", "USDT-FUTURES"]:
                params = {
                    "orderType": "limit",
                    "side": "buy",
                    "size": "0.001",
                    "price": "123.4500",
                    "force": "gtc",
                }
                if inst_type != "SPOT":
                    params.update(marginCoin="USDT", marginMode="crossed", reduceOnly="YES")
                for channel, payload in [
                    ("place-order", params),
                    ("cancel-order", {"clientOid": "client-1"}),
                ]:
                    await client.classic_trade_request(
                        "classic", inst_type, "BTCUSDT", channel, payload
                    )
                    assert await client.recv() == {
                        "op": "trade",
                        "args": [
                            {
                                "id": "classic",
                                "instType": inst_type,
                                "instId": "BTCUSDT",
                                "channel": channel,
                                "params": payload,
                            }
                        ],
                    }
    finally:
        await client.close()
        await runner.cleanup()
    assert len(frames) == (6 if uta else 4)
    assert all("apiCode" not in json.dumps(frame) for frame in frames)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("topic", "category", "args", "request_time", "message"),
    [
        ("place-order", "SPOT", [], None, "category"),
        ("batch-place", "spot", [], None, "number"),
        ("batch-cancel", None, [{"orderId": "1"}, {"clientOid": "2"}], None, "identifier type"),
        ("batch-cancel", None, [{"orderId": "1"}] * 21, None, "number"),
        ("modify-order", "spot", [{"orderId": "1", "price": "NaN"}], None, "positive"),
        (
            "modify-order",
            "spot",
            [{"orderId": "1", "price": "1", "requestId": "123"}],
            None,
            "integer",
        ),
        ("modify-order", "coin-futures", [{"orderId": "1", "price": "1"}], None, "COIN-M"),
        (
            "place-order",
            "spot",
            [{"symbol": "BTCUSDT", "qty": "1", "side": "buy", "orderType": "limit"}],
            None,
            "price",
        ),
        (
            "place-order",
            "spot",
            [
                {
                    "symbol": "BTCUSDT",
                    "qty": "1",
                    "side": "buy",
                    "orderType": "market",
                    "receiveWindow": "5000",
                }
            ],
            None,
            "requestTime",
        ),
    ],
)
async def test_invalid_trade_frames_fail_before_transport(
    topic: str,
    category: str | None,
    args: list[dict[str, Any]],
    request_time: int | None,
    message: str,
) -> None:
    client = PrivateClient("key", "secret", "pass", base_url="ws://127.0.0.1:1/v3/ws/private")
    try:
        with pytest.raises((ValueError, RuntimeError), match=message):
            await client.trade_request(
                "test", topic, args, category=category, request_time=request_time
            )
    finally:
        await client.close()
