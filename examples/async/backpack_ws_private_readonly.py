"""Open a Backpack private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import backpack


async def main() -> None:
    """Open the private stream, subscribe to order updates, and print one message."""
    api_key = os.environ["BACKPACK_API_KEY"]
    api_secret = os.environ["BACKPACK_API_SECRET"]

    async with backpack.private(api_key=api_key, api_secret=api_secret) as ws:
        await ws.subscribe_orders()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
