"""Subscribe to a BitMart public WebSocket stream."""

import asyncio

from dcex.ws import bitmart


async def main() -> None:
    """Subscribe to BitMart spot trades and print the subscription response."""
    async with bitmart.public() as ws:
        await ws.subscribe_trades("BTC-USDT-SPOT")
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
