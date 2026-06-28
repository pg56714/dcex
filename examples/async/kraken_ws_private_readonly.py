"""Open a Kraken private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import kraken


async def main() -> None:
    """Open the private stream, subscribe to balances, and print one message."""
    api_key = os.environ["KRAKEN_API_KEY"]
    api_secret = os.environ["KRAKEN_API_SECRET"]

    async with kraken.private(api_key=api_key, api_secret=api_secret) as ws:
        print({"token_available": bool(ws.token())})
        await ws.subscribe_balances()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
