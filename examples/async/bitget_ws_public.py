"""Read Bitget public WebSocket trade events."""

import asyncio

from dcex.ws import bitget


async def main() -> None:
    """Subscribe to Bitget spot trades and print two messages."""
    async with bitget.public(inst_type="SPOT") as ws:
        await ws.subscribe_trades("BTC-USDT-SPOT")
        print(await ws.recv())
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
