"""Read Lighter private account state asynchronously."""

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
    """Run the async private read-only Lighter example."""
    account_index = int(require_env("LIGHTER_ACCOUNT_INDEX"))
    api_key_index = int(require_env("LIGHTER_API_KEY_INDEX"))
    api_private_key = require_env("LIGHTER_API_PRIVATE_KEY")

    client = await dcex.lighter(
        account_index=account_index,
        api_key_index=api_key_index,
        api_private_key=api_private_key,
    )
    try:
        account = await client.get_account(by="index", value=str(account_index))
        print(account)

        limits = await client.get_account_limits()
        print(limits)

        active_orders = await client.get_account_active_orders()
        print(active_orders)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
