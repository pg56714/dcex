"""Read Lighter public WebSocket trade events."""

import asyncio

from dcex.ws import lighter


async def main() -> None:
    """Subscribe to Lighter trades and print two messages."""
    async with lighter.public() as ws:
        await ws.subscribe_trades(0)
        print(await ws.recv())
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
