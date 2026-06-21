"""Open a BitMart private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import bitmart


async def main() -> None:
    """Open the private stream, subscribe to balance updates, and print one message."""
    api_key = os.environ["BITMART_API_KEY"]
    api_secret = os.environ["BITMART_API_SECRET"]
    memo = os.environ["BITMART_MEMO"]

    async with bitmart.private(api_key=api_key, api_secret=api_secret, memo=memo) as ws:
        print(await ws.recv())
        await ws.subscribe_balance()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
