"""Subscribe to a BingX public WebSocket stream."""

import asyncio

from dcex.ws import bingx


async def main() -> None:
    """Subscribe to BingX spot trades and print one message."""
    async with bingx.public() as ws:
        await ws.subscribe_trades("BTC-USDT-SPOT")
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
