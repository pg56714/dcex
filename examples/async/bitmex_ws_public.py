"""Subscribe to a BitMEX public WebSocket stream."""

import asyncio

from dcex.ws import bitmex


async def main() -> None:
    """Subscribe to BitMEX trades and print the subscription response."""
    async with bitmex.public() as ws:
        await ws.subscribe_trades("XBTUSD")
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
