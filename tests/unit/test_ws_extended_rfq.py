"""RFQ book subscriptions must use the real RFQ stream, not the indicative book."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
import websockets


@pytest.mark.asyncio
@pytest.mark.parametrize("depth", [None, 1])
async def test_rfq_book_handshake_and_snapshot(depth: int | None) -> None:
    """The real native connection preserves the stream path and snapshot bytes."""
    from dcex import _native

    paths: asyncio.Queue[str] = asyncio.Queue()
    snapshot = b'{"type":"SNAPSHOT","data":{"market":"AAPL-USD","bid":[],"ask":[]}}'

    async def peer(connection: Any) -> None:  # noqa: ANN401
        await paths.put(connection.request.path)
        await connection.send(snapshot)
        await connection.wait_closed()

    async with websockets.serve(peer, "127.0.0.1", 0) as server:
        port = server.sockets[0].getsockname()[1]
        client = _native.ExtendedPublicWebSocketClient(timeout=2, base_url=f"ws://127.0.0.1:{port}")
        try:
            await client.subscribe_rfq_orderbook("AAPL-USD", depth)
            path = await asyncio.wait_for(paths.get(), 2)
            assert path == "/stream.extended.exchange/v1/orderbooks/rfq/AAPL-USD" + (
                "?depth=1" if depth else ""
            )
            assert await asyncio.wait_for(client.recv(), 2) == snapshot
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_rfq_invalid_depth_is_rejected_before_connecting() -> None:
    """Only full book or depth 1 is documented by Extended."""
    from dcex import _native

    client = _native.ExtendedPublicWebSocketClient(timeout=1, base_url="ws://127.0.0.1:1")
    with pytest.raises(ValueError, match="depth must be 1"):
        await client.subscribe_rfq_orderbook("AAPL-USD", 2)
