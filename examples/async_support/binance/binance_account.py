import asyncio
import os

from dotenv import load_dotenv

import dcex.async_support as dcex

load_dotenv()


BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")


async def main():
    client = await dcex.binance(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
    )

    try:
        result = await client.get_account_balance(market_type="swap")
        print(result)

        result = await client.get_income_history()
        print(result)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
