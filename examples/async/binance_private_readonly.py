import asyncio
import os

import dcex.async_support as dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    client = await dcex.binance(
        api_key=require_env("BINANCE_API_KEY"),
        api_secret=require_env("BINANCE_API_SECRET"),
    )
    try:
        balance = await client.get_account_balance(market_type="spot")
        print(balance)

        income = await client.get_income_history()
        print(income)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
