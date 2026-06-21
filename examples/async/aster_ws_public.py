"""Read Aster public WebSocket trade events."""

import asyncio

from dcex.ws import aster


async def main() -> None:
    """Subscribe to Aster futures aggregate trades and print two messages."""
    async with aster.public(market="futures") as ws:
        await ws.subscribe_agg_trades("BTC-USDT-SWAP")
        print(await ws.recv())
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
