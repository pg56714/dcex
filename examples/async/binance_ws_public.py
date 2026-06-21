"""Read Binance public WebSocket trade events."""

import asyncio

from dcex.ws import binance


async def main() -> None:
    """Subscribe to Binance aggregate trades and print two messages."""
    async with binance.public() as ws:
        await ws.subscribe_agg_trades("BTC-USDT-SPOT")
        print(await ws.recv())
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
