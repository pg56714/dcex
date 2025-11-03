import asyncio
import os

from dotenv import load_dotenv

import dcex.async_support as dcex

load_dotenv()

KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")


async def main():
    client = await dcex.kucoin(
        api_key=KUCOIN_API_KEY,
        api_secret=KUCOIN_API_SECRET,
        passphrase=KUCOIN_API_PASSPHRASE,
    )

    try:
        # result = await client.place_spot_market_buy_order(
        #     product_symbol="BOME-USDT-SPOT",
        #     size="1000",
        # )
        # print(result)

        # result = await client.place_spot_market_sell_order(
        #     product_symbol="BOME-USDT-SPOT",
        #     size="1000",
        # )
        # print(result)

        # result = await client.place_spot_limit_buy_order(
        #     product_symbol="BOME-USDT-SPOT",
        #     size="1000",
        #     price="0.0008",
        # )
        # print(result)

        # result = await client.place_spot_limit_sell_order(
        #     product_symbol="BOME-USDT-SPOT",
        #     size="1000",
        #     price="0.0008",
        # )
        # print(result)

        # result = await client.place_spot_post_only_limit_buy_order(
        #     product_symbol="BOME-USDT-SPOT",
        #     size="1000",
        #     price="0.0008",
        # )
        # print(result)

        # limit_orders = [
        #     {
        #         "symbol": "BOME-USDT-SPOT",
        #         "side": "buy",
        #         "size": "1000",
        #         "price": "0.0008",
        #     },
        #     {
        #         "symbol": "USDC-USDT-SPOT",
        #         "side": "buy",
        #         "size": "5",
        #         "price": "0.97",
        #     },
        # ]
        # result = await client.place_spot_batch_limit_orders(limit_orders)
        # print(result)

        # market_orders = [
        #     {
        #         "symbol": "BOME-USDT-SPOT",
        #         "side": "buy",
        #         "size": "1000",
        #     },
        #     {
        #         "symbol": "BOME-USDT-SPOT",
        #         "side": "sell",
        #         "size": "1000",
        #     }
        # ]

        # result = await client.place_spot_batch_market_orders(market_orders)
        # print(result)

        # result = await client.place_spot_limit_buy_order(
        #     product_symbol="BOME-USDT-SPOT",
        #     size="1000",
        #     price="0.0008",
        # )
        # print(result)

        # if isinstance(result, dict) and "data" in result:
        #     order_id = result["data"]["orderId"]
        #     print(f"Order ID: {order_id}")

        #     cancel_result = await client.cancel_spot_order(
        #         orderId=order_id,
        #         product_symbol="BOME-USDT-SPOT",
        #     )
        #     print(cancel_result)
        # else:
        #     print("Could not extract order ID from response")

        # result = await client.cancel_spot_all_orders_by_symbol(
        #     product_symbol="BOME-USDT-SPOT",
        # )
        # print(result)

        # cancel_all_result = await client.cancel_spot_all_orders()
        # print(cancel_all_result)

        # result = await client.get_spot_open_orders(
        #     product_symbol="BOME-USDT-SPOT",
        # )
        # print(result)

        result = await client.get_spot_trade_history(
            product_symbol="BOME-USDT-SPOT",
        )
        print(result)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
