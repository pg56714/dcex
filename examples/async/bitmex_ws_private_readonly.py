"""Open a BitMEX private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import bitmex


async def main() -> None:
    """Open the private stream, subscribe to margin updates, and print one message."""
    api_key = os.environ["BITMEX_API_KEY"]
    api_secret = os.environ["BITMEX_API_SECRET"]

    async with bitmex.private(api_key=api_key, api_secret=api_secret) as ws:
        await ws.subscribe_margin()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
