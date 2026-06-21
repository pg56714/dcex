"""Open a Bitget private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import bitget


async def main() -> None:
    """Open the private stream, subscribe to account updates, and print one message."""
    api_key = os.environ["BITGET_API_KEY"]
    api_secret = os.environ["BITGET_API_SECRET"]
    passphrase = os.environ["BITGET_PASSPHRASE"]

    async with bitget.private(
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
    ) as ws:
        print(await ws.recv())
        await ws.subscribe_account()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
