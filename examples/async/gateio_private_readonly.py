import asyncio
import os

import dcex.async_support as dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    client = await dcex.gateio(
        api_key=require_env("GATEIO_API_KEY"),
        api_secret=require_env("GATEIO_API_SECRET"),
    )
    try:
        futures_account = await client.get_futures_account()
        print(futures_account)

        spot_account = await client.get_spot_account(ccy="btc")
        print(spot_account)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
