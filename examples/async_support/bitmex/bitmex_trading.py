import asyncio
import os

from dotenv import load_dotenv

import dcex.async_support as dcex

load_dotenv()

BITMEX_API_KEY = os.getenv("BITMEX_API_KEY")
BITMEX_API_SECRET = os.getenv("BITMEX_API_SECRET")


async def main():
    client = await dcex.bitmex(
        api_key=BITMEX_API_KEY,
        api_secret=BITMEX_API_SECRET,
        preload_product_table=False,
    )

    try:
        # executions = await client.get_executions(product_symbol="XBT-USDT-SWAP", count=5)
        # print(executions)

        # trade_history = await client.get_trade_history(product_symbol="XBT-USDT-SWAP", count=5)
        # print(trade_history)

        trading_volume = await client.get_trading_volume()
        print(trading_volume)

        rate_limit_info = client.get_rate_limit_info()
        print(rate_limit_info)
    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
