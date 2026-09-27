"""Signed RPC frames against a local peer; no exchange credentials or trades."""

# ruff: noqa: D103
import importlib
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import pytest
from aiohttp import WSMsgType, web
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from dcex.ws.arcus import PrivateClient as ArcusWebSocket
from dcex.ws.hyperliquid import PrivateClient as HyperliquidWebSocket
from dcex.ws.hyperliquid import PublicClient as HyperliquidPublicWebSocket
from dcex.ws.lighter import PrivateClient as LighterWebSocket
from tests.unit.native_http_helpers import _http_server

ADDRESS = "0x" + "44" * 20
MARKETS = {
    "markets": [
        {
            "marketId": 7,
            "marketDisplayName": "BTC-USD",
            "tickSize": "0.1",
            "stepSize": "0.001",
            "minOrderSize": "0.001",
            "maxOrderSize": "100",
            "minOrderNotional": "1",
        }
    ]
}


@asynccontextmanager
async def peer() -> AsyncIterator[str]:
    async def socket(request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for message in ws:
            if message.type == WSMsgType.TEXT:
                await ws.send_str(message.data)
        return ws

    app = web.Application()
    app.router.add_get("/ws", socket)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    try:
        yield f"ws://127.0.0.1:{runner.addresses[0][1]}/ws"
    finally:
        await runner.cleanup()


@pytest.mark.asyncio
async def test_hyperliquid_preserves_signed_action_nonce_and_info_payload() -> None:
    async with peer() as url:
        clients = [
            HyperliquidPublicWebSocket(base_url=url, timeout=2),
            HyperliquidWebSocket(ADDRESS, base_url=url, timeout=2),
        ]
        try:
            for client in clients:
                await client.connect()
                info = {"type": "l2Book", "coin": "BTC", "nSigFigs": 5, "mantissa": None}
                await client.post_info(123, info)
                assert await client.recv() == {
                    "method": "post",
                    "id": 123,
                    "request": {"type": "info", "payload": info},
                }
            private = clients[1]
            assert isinstance(private, HyperliquidWebSocket)
            payload = {
                "action": {"type": "cancel", "cancels": [{"a": 0, "o": 123}]},
                "nonce": 1700000000000,
                "signature": {"r": "0x" + "11" * 32, "s": "0x" + "22" * 32, "v": 27},
                "vaultAddress": None,
                "expiresAfter": 1700000001000,
            }
            await private.post_action(124, payload)
            assert await private.recv() == {
                "method": "post",
                "id": 124,
                "request": {"type": "action", "payload": payload},
            }
            with pytest.raises((RuntimeError, ValueError), match="signature"):
                await private.post_action(125, {"action": {"type": "cancel"}, "nonce": 1})
            with pytest.raises((RuntimeError, ValueError), match="explorer"):
                await private.post_info(126, {"type": "explorer"})
        finally:
            for client in clients:
                await client.close()


@pytest.mark.asyncio
async def test_lighter_single_and_batch_use_distinct_json_encoding() -> None:
    async with peer() as url:
        client = LighterWebSocket(
            1, 2, "01" + "00" * 39, ws_base_url=url, http_base_url="http://127.0.0.1:1", timeout=2
        )
        infos = [
            json.dumps(
                {
                    "AccountIndex": 1,
                    "ApiKeyIndex": 2,
                    "Nonce": n,
                    "ExpiredAt": 1700000100000,
                    "Sig": "signed",
                    "MarketIndex": 0,
                    "Index": 123,
                }
            )
            for n in [1, 2]
        ]
        try:
            await client.connect()
            await client.send_tx("single", 15, infos[0])
            assert await client.recv() == {
                "type": "jsonapi/sendtx",
                "data": {"id": "single", "tx_type": 15, "tx_info": json.loads(infos[0])},
            }
            await client.send_tx_batch("batch", [15, 15], infos)
            frame = await client.recv()
            assert isinstance(frame, dict)
            assert frame["type"] == "jsonapi/sendtxbatch"
            assert json.loads(frame["data"]["tx_types"]) == [15, 15]
            assert json.loads(frame["data"]["tx_infos"]) == infos
            for types, values in [([], []), ([15], []), ([15] * 16, infos[:1] * 16)]:
                with pytest.raises((RuntimeError, ValueError), match="1..15"):
                    await client.send_tx_batch("invalid", types, values)
            wrong = json.loads(infos[0])
            wrong["AccountIndex"] = 2
            with pytest.raises((RuntimeError, ValueError), match="AccountIndex"):
                await client.send_tx("wrong-account", 15, json.dumps(wrong))
        finally:
            await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_arcus_native_signing_to_websocket_preserves_typed_signature(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in ["ARCUS_API_KEY", "ARCUS_API_SIGNING_KEY", "ARCUS_ADDRESS"]:
        monkeypatch.delenv(name, raising=False)
    module = importlib.import_module(
        "dcex.arcus.client" if mode == "sync" else "dcex.async_support.arcus.client"
    )
    with _http_server(MARKETS) as (http_url, received):
        rest = module.Client(api_secret="05" * 32, address=ADDRESS, base_url=http_url)
        async with peer() as url:
            client = ArcusWebSocket(ADDRESS, base_url=url, timeout=2)
            try:
                if mode == "async":
                    await rest.async_init()
                await client.connect()
                for method, params in [
                    ("cancel_order", {"product_symbol": "BTC-USD", "order_id": "ord-1"}),
                    (
                        "batch_cancel_orders",
                        {
                            "cancels": [
                                {"product_symbol": "BTC-USD", "order_id": "ord-1"},
                                {"product_symbol": "BTC-USD", "order_id": "ord-2"},
                            ]
                        },
                    ),
                    ("disarm_scheduled_cancel", {}),
                ]:
                    frame = rest.sign_websocket_request(123, method, **params)
                    if mode == "async":
                        frame = await frame
                    request = frame["request"]
                    timestamp = int(request["timestamp"])
                    public_key = Ed25519PublicKey.from_public_bytes(
                        bytes.fromhex(request["apiKey"])
                    )
                    if method == "disarm_scheduled_cancel":
                        compact = json.dumps(
                            request["payload"], sort_keys=True, separators=(",", ":")
                        )
                        public_key.verify(
                            bytes.fromhex(request["signature"]),
                            f"{timestamp}scheduleCancel{compact}".encode(),
                        )
                    else:
                        entries = request["payload"].get("cancels", [request["payload"]])
                        for entry in entries:
                            canonical = {
                                "ad": ADDRESS,
                                "ai": 0,
                                "ct": timestamp,
                                "id": entry["orderId"],
                                "m": 7,
                                "op": 2,
                                "v": 1,
                            }
                            signature = entry.get("signature", request["signature"])
                            public_key.verify(
                                bytes.fromhex(signature),
                                json.dumps(
                                    canonical, sort_keys=True, separators=(",", ":")
                                ).encode(),
                            )
                    await client.post_request(frame)
                    assert await client.recv() == frame
                await client.get_request(124, "markets", {})
                assert await client.recv() == {
                    "type": "get",
                    "id": 124,
                    "request": {"type": "markets", "payload": {}},
                }
                await client.subscribe_settle_loan_results()
                assert await client.recv() == {
                    "type": "subscribe",
                    "channel": "settleLoanResults",
                    "id": ADDRESS,
                }
            finally:
                await client.close()
                if mode == "async":
                    await rest.close()
                else:
                    rest.close()
        requests = []
        while not received.empty():
            requests.append(received.get_nowait())
        assert len(requests) == 3
        assert all(request["path"] == "/v1/markets" for request in requests)
