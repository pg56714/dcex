"""Read OKX public WebSocket trade events."""

import asyncio

from dcex.ws import okx


async def main() -> None:
    """Subscribe to OKX trades and print two messages."""
    async with okx.public() as ws:
        await ws.subscribe_trades("BTC-USDT-SPOT")
        print(await ws.recv())
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
