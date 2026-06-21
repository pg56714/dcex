"""Subscribe to a MEXC public WebSocket stream."""

import asyncio

from dcex.ws import mexc


async def main() -> None:
    """Subscribe to MEXC spot trades and print the subscription response."""
    async with mexc.public() as ws:
        await ws.subscribe_trades("BTC-USDT-SPOT")
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
