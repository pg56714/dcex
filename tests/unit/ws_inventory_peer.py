"""A local WebSocket peer that records frames and can push exchange events."""

import json
from contextlib import asynccontextmanager

from aiohttp import WSMsgType, web


@asynccontextmanager
async def echo_peer(path="/", events=()):
    received = []

    async def socket(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        for event in events:
            if isinstance(event, bytes):
                await ws.send_bytes(event)
            else:
                await ws.send_json(event)
        async for message in ws:
            if message.type == WSMsgType.TEXT:
                payload = json.loads(message.data)
                received.append(payload)
                await ws.send_json(payload)
        return ws

    app = web.Application()
    app.router.add_get(path, socket)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    try:
        yield f"ws://127.0.0.1:{runner.addresses[0][1]}{path}", received
    finally:
        await runner.cleanup()
