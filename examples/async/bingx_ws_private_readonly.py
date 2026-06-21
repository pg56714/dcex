"""Open a BingX private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import bingx


async def main() -> None:
    """Open the private stream, subscribe to order updates, and print one message."""
    api_key = os.environ["BINGX_API_KEY"]
    api_secret = os.environ["BINGX_API_SECRET"]

    async with bingx.private(api_key=api_key, api_secret=api_secret) as ws:
        await ws.subscribe_orders()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
