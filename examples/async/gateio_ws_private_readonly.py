"""Open a Gate.io private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import gateio


async def main() -> None:
    """Open the private stream, subscribe to balance updates, and print one message."""
    api_key = os.environ["GATEIO_API_KEY"]
    api_secret = os.environ["GATEIO_API_SECRET"]

    async with gateio.private(api_key=api_key, api_secret=api_secret) as ws:
        await ws.subscribe_balances()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
