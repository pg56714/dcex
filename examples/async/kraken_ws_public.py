"""Read Kraken public WebSocket trade events."""

import asyncio

from dcex.ws import kraken


async def main() -> None:
    """Subscribe to Kraken spot trades and print two messages."""
    async with kraken.public() as ws:
        await ws.subscribe_trades("BTC-USD-SPOT")
        print(await ws.recv())
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
