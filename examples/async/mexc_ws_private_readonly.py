"""Open a MEXC private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import mexc


async def main() -> None:
    """Open the private stream, subscribe to account updates, and print one message."""
    api_key = os.environ["MEXC_API_KEY"]
    api_secret = os.environ["MEXC_API_SECRET"]

    async with mexc.private(api_key=api_key, api_secret=api_secret) as ws:
        await ws.keep_alive()
        await ws.subscribe_account()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
