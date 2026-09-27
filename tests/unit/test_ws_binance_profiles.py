"""Exercise Binance market routing and listen-key lifecycle through native clients."""

# ruff: noqa: D103
from __future__ import annotations

import asyncio
from typing import Any

import pytest
from aiohttp import WSMsgType, web

from dcex.ws.binance import PrivateClient, PublicClient


@pytest.mark.parametrize(
    ("profile", "url"),
    [
        ("spot", "wss://stream.binance.com:9443/ws"),
        ("futures_public", "wss://fstream.binance.com/public/ws"),
        ("futures_market", "wss://fstream.binance.com/market/ws"),
        ("coin_futures", "wss://dstream.binance.com/ws"),
        ("options_public", "wss://fstream.binance.com/public/ws"),
        ("options_market", "wss://fstream.binance.com/market/ws"),
    ],
)
def test_public_profile_defaults(profile: str, url: str) -> None:
    assert PublicClient(profile=profile).url == url


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("profile", "streams", "symbol", "expected"),
    [
        (
            "spot",
            ["btcusdt@bookTicker", "!miniTicker@arr", "btcusdt@depth5"],
            "BTC-USDT-SPOT",
            "btcusdt@ticker",
        ),
        (
            "futures_market",
            [
                "btcusdt@markPrice",
                "btcusdt@continuousKline_1m",
                "!forceOrder@arr",
                "!contractInfo",
                "!assetIndex@arr",
            ],
            "BTC-USDT-SWAP",
            "btcusdt@ticker",
        ),
        (
            "coin_futures",
            ["btcusd_perp@indexPrice", "btcusd_perp@depth", "!forceOrder@arr"],
            "BTCUSD_PERP",
            "btcusd_perp@ticker",
        ),
        (
            "options_public",
            ["btc-261225-90000-c@depth10", "btc-261225-90000-c@trade"],
            "BTC-261225-90000-C",
            "btc-261225-90000-c@ticker",
        ),
        ("options_market", ["btc@optionMarkPrice", "!optionOpenInterest@arr"], None, None),
        ("futures_public", ["btcusdt@depth", "btcusdt@rpiDepth@500ms", "!bookTicker"], None, None),
    ],
)
async def test_native_subscription_and_unsubscription(
    profile: str, streams: list[str], symbol: str | None, expected: str | None
) -> None:
    received: list[dict[str, Any]] = []

    async def handler(request: web.Request) -> web.WebSocketResponse:
        peer = web.WebSocketResponse()
        await peer.prepare(request)
        async for message in peer:
            if message.type == WSMsgType.TEXT:
                payload = message.json()
                received.append(payload)
                await peer.send_json({"id": payload["id"], "result": None})
        return peer

    app = web.Application()
    app.router.add_get("/ws", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    client = PublicClient(profile=profile, base_url=f"ws://127.0.0.1:{runner.addresses[0][1]}/ws")
    try:
        await client.connect()
        request_id = await client.subscribe(streams)
        assert (await asyncio.wait_for(client.recv(), 2))["id"] == request_id
        assert received[-1] == {"method": "SUBSCRIBE", "params": streams, "id": request_id}
        await client.unsubscribe(streams)
        await client.recv()
        assert received[-1]["method"] == "UNSUBSCRIBE"
        if symbol:
            await client.subscribe_ticker(symbol)
            await client.recv()
            assert received[-1]["params"] == [expected]
    finally:
        await client.close()
        await runner.cleanup()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("profile", "http_path", "ws_path"),
    [
        ("futures", "/fapi/v1/listenKey", "/private/ws/listen-key"),
        ("coin_futures", "/dapi/v1/listenKey", "/ws/listen-key"),
        ("options", "/eapi/v1/listenKey", "/private/ws/listen-key"),
        ("portfolio_margin", "/papi/v1/listenKey", "/pm/ws/listen-key"),
        ("margin_risk", "/sapi/v1/margin/listen-key", "/ws/listen-key"),
    ],
)
async def test_native_private_profile_lifecycle(profile: str, http_path: str, ws_path: str) -> None:
    requests: list[tuple[str, str]] = []
    payloads: list[dict[str, str]] = []

    async def handler(request: web.Request) -> web.StreamResponse:
        requests.append((request.method, request.path))
        if request.path == ws_path:
            peer = web.WebSocketResponse()
            await peer.prepare(request)
            await peer.send_json({"e": "ACCOUNT_UPDATE"})
            async for _ in peer:
                pass
            return peer
        assert request.path == http_path
        assert request.headers["X-MBX-APIKEY"] == "key"
        params = dict(request.query)
        params.update(await request.post())
        payloads.append(params)
        assert "signature" not in params
        return web.json_response({"listenKey": "listen-key"})

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    base = f"http://127.0.0.1:{runner.addresses[0][1]}"
    prefix = ws_path.removesuffix("/ws/listen-key")
    client = PrivateClient(
        "key",
        "secret",
        profile=profile,
        spot_http_base_url=base,
        futures_http_base_url=base,
        coin_futures_http_base_url=base,
        options_http_base_url=base,
        portfolio_margin_http_base_url=base,
        ws_base_url=base.replace("http://", "ws://") + prefix,
    )
    try:
        assert await client.connect() == "listen-key"
        assert (await client.recv())["e"] == "ACCOUNT_UPDATE"
        await client.keep_alive()
        if profile == "margin_risk":
            assert payloads[-1]["listenKey"] == "listen-key"
        await client.close()
        assert client.listen_key() is None
        assert requests == [
            ("POST", http_path),
            ("GET", ws_path),
            ("PUT", http_path),
            ("DELETE", http_path),
        ]
    finally:
        await client.close()
        await runner.cleanup()


@pytest.mark.asyncio
async def test_profiles_reject_invalid_routing_and_limits_before_network() -> None:
    with pytest.raises(ValueError, match="profile"):
        PublicClient(profile="unknown")
    with pytest.raises(ValueError, match="profile"):
        PrivateClient("key", "secret", profile="spot")
    with pytest.raises(ValueError, match="futures_market"):
        await PublicClient(profile="futures_public").subscribe(["btcusdt@markPrice"])
    with pytest.raises(ValueError, match="futures_public"):
        await PublicClient(profile="futures_market").subscribe(["btcusdt@depth"])
    with pytest.raises(ValueError, match="200"):
        await PublicClient(profile="options_public").subscribe([f"s{i}@trade" for i in range(201)])


@pytest.mark.parametrize(("key", "secret"), [("", "secret"), ("key", " ")])
def test_private_profiles_preserve_credential_validation(key: str, secret: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        PrivateClient(key, secret)
