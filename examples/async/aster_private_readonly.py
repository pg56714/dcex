"""Read Aster private account data asynchronously."""

import asyncio
import os

import dcex.async_support as dcex


def require_env(name: str) -> str:
    """Read a required environment variable."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    """Run the async Aster private read-only example."""
    client = await dcex.aster(
        user_address=require_env("ASTER_USER_ADDRESS"),
        signer_address=require_env("ASTER_SIGNER_ADDRESS"),
        private_key=require_env("ASTER_PRIVATE_KEY"),
    )
    try:
        spot_account = await client.get_spot_account()
        print(spot_account)

        futures_balance = await client.get_futures_balance()
        print(futures_balance)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
