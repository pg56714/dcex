"""Open a Lighter private WebSocket user-data stream."""

import asyncio
import os

from dcex.ws import lighter


def require_env(name: str) -> str:
    """Return a required environment variable."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    """Open the private stream, subscribe to order updates, and print one message."""
    account_index = int(require_env("LIGHTER_ACCOUNT_INDEX"))
    api_key_index = int(require_env("LIGHTER_API_KEY_INDEX"))
    api_private_key = require_env("LIGHTER_API_PRIVATE_KEY")

    async with lighter.private(
        account_index=account_index,
        api_key_index=api_key_index,
        api_private_key=api_private_key,
    ) as ws:
        await ws.subscribe_account_all_orders()
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
