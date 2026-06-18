import asyncio
import os

import dcex.async_support as dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    client = await dcex.kraken(
        api_key=require_env("KRAKEN_API_KEY"),
        api_secret=require_env("KRAKEN_API_SECRET"),
    )
    try:
        balance = await client.get_spot_account_balance()
        print(balance)

        open_orders = await client.get_spot_open_orders()
        print(open_orders)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
