"""Read Backpack private account data asynchronously."""

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
    """Run the async Backpack private read-only example."""
    client = await dcex.backpack(
        api_key=require_env("BACKPACK_API_KEY"),
        api_secret=require_env("BACKPACK_API_SECRET"),
        preload_product_table=False,
    )
    try:
        account = await client.get_account()
        print(account)

        balances = await client.get_balances()
        print(balances)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
