"""Subscribe to a KuCoin public WebSocket stream."""

import asyncio

from dcex.ws import kucoin


async def main() -> None:
    """Subscribe to KuCoin spot trades and print one message."""
    async with kucoin.public() as ws:
        await ws.subscribe_trades("BTC-USDT-SPOT")
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
