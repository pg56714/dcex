import asyncio
import os

import dcex.async_support as dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    client = await dcex.bitget(
        api_key=require_env("BITGET_API_KEY"),
        api_secret=require_env("BITGET_API_SECRET"),
        passphrase=require_env("BITGET_PASSPHRASE"),
    )
    try:
        spot_assets = await client.get_spot_account_assets(coin="USDT")
        print(spot_assets)

        futures_positions = await client.get_futures_positions(marginCoin="USDT")
        print(futures_positions)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
