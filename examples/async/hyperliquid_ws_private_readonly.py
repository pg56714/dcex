"""Open a Hyperliquid private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import hyperliquid


async def main() -> None:
    """Open the private stream, subscribe to user events, and print one message."""
    user = os.environ["HYPERLIQUID_USER_ADDRESS"]

    async with hyperliquid.private(user=user) as ws:
        await ws.subscribe_user_events()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
