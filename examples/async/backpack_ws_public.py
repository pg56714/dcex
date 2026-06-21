"""Read Backpack public WebSocket trade events."""

import asyncio

from dcex.ws import backpack


async def main() -> None:
    """Subscribe to Backpack trades and print two messages."""
    async with backpack.public() as ws:
        await ws.subscribe_trades("SOL_USDC")
        print(await ws.recv())
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
