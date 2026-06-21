"""Open a Binance private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import binance


async def main() -> None:
    """Open the user-data stream, keep it alive, and print one message."""
    api_key = os.environ["BINANCE_API_KEY"]
    api_secret = os.environ["BINANCE_API_SECRET"]

    async with binance.private(api_key=api_key, api_secret=api_secret) as ws:
        await ws.keep_alive()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
