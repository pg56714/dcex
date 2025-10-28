import asyncio
import os

from dotenv import load_dotenv

import dcex.async_support as dcex

load_dotenv()

OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_API_SECRET = os.getenv("OKX_API_SECRET")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")


async def main():
    client = await dcex.okx(
        api_key=OKX_API_KEY,
        api_secret=OKX_API_SECRET,
        passphrase=OKX_PASSPHRASE,
    )

    try:
        # res = await client.get_order_list(
        #     product_symbol="BTC-USDT-SPOT",
        # )
        # print(res)

        # res = await client.get_orders_history(
        #     instType="SPOT",
        # )
        # print(res)

        # res = await client.get_orders_history_archive(
        #     instType="SPOT",
        # )
        # print(res)

        # res = await client.get_fills()
        # print(res)

        # res = await client.get_fills_history(
        #     instType="SPOT",
        # )
        # print(res)

        # res = await client.get_account_rate_limit()
        # print(res)

        res = await client.place_limit_buy_order(
            product_symbol="DOGE-USDT-SWAP",
            tdMode="cross",
            sz="0.01",
            px="0.1",
        )
        print(res)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
