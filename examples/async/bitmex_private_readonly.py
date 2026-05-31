import asyncio
import os

import dcex.async_support as dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


async def main() -> None:
    client = await dcex.bitmex(
        api_key=require_env("BITMEX_API_KEY"),
        api_secret=require_env("BITMEX_API_SECRET"),
    )
    try:
        wallet = await client.get_wallet_summary()
        print(wallet)

        positions = await client.get_positions()
        print(positions)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
