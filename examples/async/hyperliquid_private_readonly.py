"""Read Hyperliquid private account state asynchronously with optional agent resolution."""

import asyncio
import os

import dcex.async_support as dcex


def require_env(name: str) -> str:
    """Return a required environment variable."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    """Run the async private read-only Hyperliquid example."""
    wallet_address = require_env("HYPERLIQUID_WALLET_ADDRESS")
    client = await dcex.hyperliquid()
    try:
        role = await client.user_role(user=wallet_address)
        if isinstance(role, dict) and role.get("role") == "agent":
            wallet_address = role.get("data", {}).get("user", wallet_address)

        state = await client.clearinghouse_state(user=wallet_address)
        print(state)

        spot_state = await client.spot_clearinghouse_state(user=wallet_address)
        print(spot_state)

        open_orders = await client.open_orders(user=wallet_address)
        print(open_orders)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
