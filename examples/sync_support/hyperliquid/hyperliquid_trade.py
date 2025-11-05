import asyncio
import os
import dcex.async_support as dcex
from dotenv import load_dotenv

load_dotenv()

HYPERLIQUID_WALLET_ADDRESS = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
HYPERLIQUID_PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")


async def main():
    client = await dcex.hyperliquid(
        wallet_address=HYPERLIQUID_WALLET_ADDRESS,
        private_key=HYPERLIQUID_PRIVATE_KEY,
    )

    try:
        # result = await client.place_order(
        #     product_symbol="BTC-USD-SWAP",
        #     isBuy=True,
        #     price="104320",
        #     size="0.00011",
        #     reduceOnly=False,
        #     isMarket=True,
        #     triggerPx="10000",
        #     tpsl="sl",
        #     grouping="na",
        # )
        # print(result)

        # result = await client.place_future_market_order(
        #     product_symbol="BTC-USD-SWAP",
        #     isBuy=True,
        #     size="0.00011",
        #     triggerPx="10000",
        #     tpsl="sl",
        # )
        # print(result)

        result = await client.place_future_market_buy_order(
            product_symbol="BTC-USD-SWAP", size="0.00011", triggerPx="10000", tpsl="sl"
        )
        print(result)

        # result = await client.place_future_market_sell_order(
        #     product_symbol="BTC-USD-SWAP", size="0.00011", triggerPx="10000", tpsl="sl"
        # )
        # print(result)

        # result = await client.place_future_limit_order(
        #     product_symbol="BTC-USD-SWAP", isBuy=True, price="100000", size="0.00011", tif="Gtc"
        # )
        # print(result)

        # result = await client.place_future_limit_buy_order(
        #     product_symbol="BTC-USD-SWAP", price="104320", size="0.00011", tif="Gtc"
        # )
        # print(result)

        # result = await client.place_future_limit_sell_order(
        #     product_symbol="BTC-USD-SWAP", price="104320", size="0.00011", tif="Gtc"
        # )
        # print(result)

        # result = await client.cancel_order(product_symbol="BTC-USD-SWAP", oid=223529631739)
        # print(result)

        # result = await client.schedule_cancel(time=1748628637000)
        # print(result)

        # result = await client.modify_order(
        #     oid=223537844105,
        #     product_symbol="BTC-USD-SWAP",
        #     isBuy=True,
        #     price="10000",
        #     size="0.00022",
        #     reduceOnly=False,
        #     tif="Gtc",
        # )
        # print(result)

        # result = await client.update_leverage(
        #     product_symbol="BTC-USD-SWAP", isCross=True, leverage=10
        # )
        # print(result)

        # result = await client.update_isolate_margin(
        #     product_symbol="BTC-USD-SWAP", isBuy=True, ntli=2
        # )
        # print(result)

        # result = await client.place_twap_order(
        #     product_symbol="BTC-USD-SWAP",
        #     isBuy=True,
        #     size="0.00022",
        #     reduceOnly=False,
        #     minutes=5,
        #     randomize=False,
        # )
        # print(result)

        # result = await client.cancel_twap_order(product_symbol="BTC-USD-SWAP", twap_id=6249)
        # print(result)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
