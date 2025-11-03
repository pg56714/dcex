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
    )

    try:
        order = await client.place_market_buy_order(
            product_symbol="XRP-USDT-SPOT",
            orderQty=1000000,  # 1000000 XRP = 1 USDT
        )
        print(order)

        order = await client.place_market_sell_order(
            product_symbol="XRP-USDT-SPOT",
            orderQty=1000000,
        )
        print(order)

        order = await client.place_limit_buy_order(
            product_symbol="XRP-USDT-SPOT",
            orderQty=100,
            price=2,
        )
        print(order)
        print(client.get_rate_limit_info())

        order = await client.place_limit_sell_order(
            product_symbol="XRP-USDT-SPOT",
            orderQty=100,
            price=3,
        )
        print(order)
        print(client.get_rate_limit_info())

        order = await client.place_post_only_buy_order(
            product_symbol="XRP-USDT-SPOT",
            orderQty=100,
            price=2,
        )
        print(order)

        order = await client.place_post_only_sell_order(
            product_symbol="XRP-USDT-SPOT",
            orderQty=100,
            price=3,
        )
        print(order)

        order = await client.amend_order(
            orderID="fb83b63d-15b8-46bd-b8df-81192bab82ee",
            price=2.2,
        )
        print(order)

        order = await client.cancel_order(
            orderID="f228d218-c95d-455f-bbaa-6fc108c1d1d5",
        )
        print(order)

        order = await client.cancel_all_orders(
            product_symbol="XRP-USDT-SPOT",
        )
        print(order)

        order = await client.get_order(
            product_symbol="XRP-USDT-SPOT",
        )
        print(order)
        print(client.get_rate_limit_info())
    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
