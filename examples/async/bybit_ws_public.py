"""Read Bybit public WebSocket trade events."""

import asyncio

from dcex.ws import bybit


async def main() -> None:
    """Subscribe to Bybit spot trades and print two messages."""
    async with bybit.public(category="spot") as ws:
        await ws.subscribe_trades("BTC-USDT-SPOT")
        print(await ws.recv())
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
