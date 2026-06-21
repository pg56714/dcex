"""Open a Bybit private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import bybit


async def main() -> None:
    """Open the private stream, subscribe to wallet updates, and print one message."""
    api_key = os.environ["BYBIT_API_KEY"]
    api_secret = os.environ["BYBIT_API_SECRET"]

    async with bybit.private(api_key=api_key, api_secret=api_secret) as ws:
        print(await ws.recv())
        await ws.subscribe_wallet()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
