import asyncio
import os

import dcex.async_support as dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    wallet_address = require_env("HYPERLIQUID_WALLET_ADDRESS")
    client = await dcex.hyperliquid()
    try:
        state = await client.clearinghouse_state(user=wallet_address)
        print(state)

        open_orders = await client.open_orders(user=wallet_address)
        print(open_orders)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
