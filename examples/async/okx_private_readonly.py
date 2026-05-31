import asyncio
import os

import dcex.async_support as dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    client = await dcex.okx(
        api_key=require_env("OKX_API_KEY"),
        api_secret=require_env("OKX_API_SECRET"),
        passphrase=require_env("OKX_PASSPHRASE"),
    )
    try:
        balance = await client.get_account_balance()
        print(balance)

        orders = await client.get_order_list(product_symbol="BTC-USDT-SPOT")
        print(orders)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
