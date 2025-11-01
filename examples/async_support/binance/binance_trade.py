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
        result = await client.place_market_buy_order(
            product_symbol="USDC-USDT-SPOT",
            quantity="10",
        )
        print(result)

        result = await client.place_market_sell_order(
            product_symbol="USDC-USDT-SPOT",
            quantity="10",
        )
        print(result)

        result = await client.place_market_buy_order(
            product_symbol="XRP-USDT-SWAP",
            quantity="5",
        )
        print(result)

        result = await client.place_market_sell_order(
            product_symbol="XRP-USDT-SWAP",
            quantity="5",
        )
        print(result)

        result = await client.place_limit_buy_order(
            product_symbol="XRP-USDT-SWAP",
            quantity="5",
            price="2.2768",
        )
        print(result)

        result = await client.place_limit_sell_order(
            product_symbol="XRP-USDT-SWAP",
            quantity="5",
            price="2.277",
        )
        print(result)

        result = await client.place_post_only_limit_buy_order(
            product_symbol="XRP-USDT-SWAP",
            quantity="5",
            price="2.26",
        )
        print(result)

        result = await client.place_post_only_limit_sell_order(
            product_symbol="XRP-USDT-SWAP",
            quantity="5",
            price="2.278",
        )
        print(result)

        result = await client.cancel_all_open_orders(
            product_symbol="USDC-USDT-SPOT",
        )
        print(result)

        result = await client.cancel_order(
            product_symbol="XRP-USDT-SWAP",
            orderId=100916566432,
        )
        print(result)

        result = await client.get_order(
            product_symbol="XRP-USDT-SWAP",
            orderId=100916566432,
        )
        print(result)

        result = await client.cancel_all_open_orders(
            product_symbol="XRP-USDT-SWAP",
        )
        print(result)

        result = await client.get_future_all_order(
            product_symbol="XRP-USDT-SWAP",
        )
        print(result)

        result = await client.get_open_orders(
            product_symbol="XRP-USDT-SPOT",
        )
        print(result)

        result = await client.get_future_position(
            product_symbol="XRP-USDT-SWAP",
        )
        print(result)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
