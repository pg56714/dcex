"""Open a MEXC private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import mexc


async def main() -> None:
    """Open the private stream, subscribe to account updates, and print one message."""
    api_key = os.environ["MEXC_API_KEY"]

    async with mexc.private(api_key=api_key) as ws:
        await ws.keep_alive()
        print({"listen_key": ws.listen_key()})
        await ws.subscribe_account()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
