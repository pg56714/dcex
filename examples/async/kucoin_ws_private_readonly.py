"""Open a KuCoin private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import kucoin


async def main() -> None:
    """Open the private stream, subscribe to order updates, and print one message."""
    api_key = os.environ["KUCOIN_API_KEY"]
    api_secret = os.environ["KUCOIN_API_SECRET"]
    passphrase = os.environ["KUCOIN_API_PASSPHRASE"]

    async with kucoin.private(
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
    ) as ws:
        await ws.subscribe_orders()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
