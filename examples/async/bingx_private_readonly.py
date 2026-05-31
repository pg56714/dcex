import asyncio
import os

import dcex.async_support as dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    client = await dcex.bingx(
        api_key=require_env("BINGX_API_KEY"),
        api_secret=require_env("BINGX_API_SECRET"),
    )
    try:
        balance = await client.get_account_balance()
        print(balance)

        positions = await client.get_open_positions(product_symbol="BTC-USDT-SWAP")
        print(positions)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
