"""Subscribe to a Gate.io public WebSocket stream."""

import asyncio

from dcex.ws import gateio


async def main() -> None:
    """Subscribe to Gate.io spot trades and print the subscription response."""
    async with gateio.public() as ws:
        await ws.subscribe_trades("BTC-USDT-SPOT")
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
