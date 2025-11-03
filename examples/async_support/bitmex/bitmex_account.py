import asyncio
import os
from typing import Any, cast

from dotenv import load_dotenv

import dcex.async_support as dcex

load_dotenv()

BITMEX_API_KEY = os.getenv("BITMEX_API_KEY")
BITMEX_API_SECRET = os.getenv("BITMEX_API_SECRET")


async def main():
    client = await dcex.bitmex(
        api_key=BITMEX_API_KEY,
        api_secret=BITMEX_API_SECRET,
    )

    try:
        wallet_summary = await client.get_wallet_summary()
        # API returns a list of wallet records
        records: list[dict[str, Any]] = cast(
            list[dict[str, Any]],
            wallet_summary if isinstance(wallet_summary, list) else [wallet_summary],
        )
        for record in records:
            record_dict = cast(dict[str, Any], record)
            scaled_amount = record_dict["amount"] / 1000000
            scaled_deposited = record_dict["deposited"] / 1000000

            print(f"Currency: {record_dict['currency']}")
            print(f"Current Balance: {scaled_amount}")
            print(f"Total Deposit: {scaled_deposited}")
            print("---")
    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
