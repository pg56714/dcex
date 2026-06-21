"""Open an Aster private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import aster


async def main() -> None:
    """Open the user-data stream, keep it alive, and print one message."""
    user_address = os.environ["ASTER_USER_ADDRESS"]
    signer_address = os.environ["ASTER_SIGNER_ADDRESS"]
    private_key = os.environ["ASTER_PRIVATE_KEY"]

    async with aster.private(
        user_address=user_address,
        signer_address=signer_address,
        private_key=private_key,
        market="futures",
    ) as ws:
        await ws.keep_alive()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
