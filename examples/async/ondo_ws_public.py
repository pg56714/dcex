"""Read Ondo Perps public WebSocket depth events."""

import asyncio

from dcex.ws import ondo


async def main() -> None:
    """Subscribe to a public market and print two protocol messages."""
    async with ondo.public() as ws:
        await ws.subscribe_depth("BTC-USD.P")
        for _ in range(2):
            event = await ws.recv()
            print(event.get("type"), event.get("channel"))


if __name__ == "__main__":
    asyncio.run(main())
