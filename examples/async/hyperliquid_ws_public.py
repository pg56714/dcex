"""Read Hyperliquid public WebSocket trade events."""

import asyncio

from dcex.ws import hyperliquid


async def main() -> None:
    """Subscribe to Hyperliquid trades and print two messages."""
    async with hyperliquid.public() as ws:
        await ws.subscribe_trades("BTC")
        print(await ws.recv())
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
