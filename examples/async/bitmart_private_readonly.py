import asyncio
import os

import dcex.async_support as dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    client = await dcex.bitmart(
        api_key=require_env("BITMART_API_KEY"),
        api_secret=require_env("BITMART_API_SECRET"),
        memo=require_env("BITMART_MEMO"),
    )
    try:
        balance = await client.get_account_balance()
        print(balance)

        wallet = await client.get_spot_wallet()
        print(wallet)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
