"""A receive waiting on a quiet stream must not hold back pings or subscriptions."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest
import websockets


@pytest.mark.asyncio
async def test_ping_is_sent_while_a_receive_is_pending() -> None:
    """The ping goes out at once and the interrupted receive still gets the reply."""
    from dcex import _native

    sent: asyncio.Queue[str] = asyncio.Queue()

    async def peer(connection: Any) -> None:  # noqa: ANN401
        async for message in connection:
            await sent.put(message)
            await connection.send('{"op":"pong"}')

    async with websockets.serve(peer, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        # The receive timeout is far longer than the waits below: a ping that only
        # leaves once the receive gives up fails the test.
        client = _native.BybitPublicWebSocketClient(
            "linear", timeout=30, base_url=f"ws://127.0.0.1:{port}"
        )
        await client.connect()
        try:
            pending = asyncio.ensure_future(client.recv())
            await asyncio.sleep(0.2)  # the receive is now waiting on a silent stream
            await asyncio.wait_for(client.ping(), 3)
            assert json.loads(await asyncio.wait_for(sent.get(), 3))["op"] == "ping"
            assert json.loads(bytes(await asyncio.wait_for(pending, 3))) == {"op": "pong"}
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_pings_do_not_postpone_the_receive_timeout() -> None:
    """A silent connection still times out while pings keep interrupting the receive."""
    from dcex import _native

    async def peer(connection: Any) -> None:  # noqa: ANN401
        async for _ in connection:
            pass

    async with websockets.serve(peer, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        client = _native.BybitPublicWebSocketClient(
            "linear", timeout=1, base_url=f"ws://127.0.0.1:{port}"
        )
        await client.connect()
        try:

            async def pinger() -> None:
                while True:
                    await client.ping()
                    await asyncio.sleep(0.1)

            task = asyncio.ensure_future(pinger())
            try:
                with pytest.raises(RuntimeError, match="receive timed out"):
                    await asyncio.wait_for(client.recv(), 5)
            finally:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_messages_survive_interrupted_receives() -> None:
    """Sends racing a receive loop never drop or reorder a message."""
    from dcex import _native

    total = 200

    async def peer(connection: Any) -> None:  # noqa: ANN401
        for index in range(total):
            await connection.send(json.dumps({"n": index}))
            if index % 10 == 0:
                await asyncio.sleep(0)
        async for _ in connection:
            pass

    async with websockets.serve(peer, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        client = _native.BybitPublicWebSocketClient(
            "linear", timeout=30, base_url=f"ws://127.0.0.1:{port}"
        )
        await client.connect()
        try:

            async def pinger() -> None:
                while True:
                    await client.ping()
                    await asyncio.sleep(0)

            task = asyncio.ensure_future(pinger())
            try:
                seen = [
                    json.loads(bytes(await asyncio.wait_for(client.recv(), 10)))["n"]
                    for _ in range(total)
                ]
            finally:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
            assert seen == list(range(total))
        finally:
            await client.close()
