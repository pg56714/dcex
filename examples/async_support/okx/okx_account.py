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
        # res = await client.get_account_instruments(
        #     instType="SPOT",
        #     product_symbol="BTC-USDT-SPOT",
        # )
        # print(res)

        res = await client.get_account_balance()
        print(res)

        # res = await client.get_positions(
        #     product_symbol="HYPE-USDT-SWAP",
        # )
        # print(res)

        # res = await client.get_positions_history(
        #     product_symbol="BTC-USDT-SPOT",
        # )
        # print(res)

        # res = await client.get_position_risk(instType="SWAP")
        # print(res)

        # res = await client.get_account_bills(
        #     product_symbol="BTC-USDT-SPOT",
        # )
        # print(res)

        # res = await client.get_account_bills_archive(
        #     product_symbol="BTC-USDT-SPOT",
        # )
        # print(res)

        # res = await client.post_account_bills_history_archive(
        #     year="2025",
        #     quarter="Q1",
        # )
        # print(res)

        # res = await client.get_account_bills_history_archive(
        #     year="2025",
        #     quarter="Q1",
        # )
        # print(res)

        # res = await client.get_account_config()
        # print(res)

        # res = await client.set_position_mode(
        #     posMode="net_mode",
        # )
        # print(res)

        # res = await client.get_max_order_size(
        #     product_symbol="BTC-USDT-SPOT",
        #     tdMode="isolated",
        # )
        # print(res)

        # res = await client.get_max_avail_size(
        #     product_symbol="BTC-USDT-SPOT",
        #     tdMode="cash",
        # )
        # print(res)

        # res = await client.get_leverage(
        #     product_symbol="DOGE-USDT-SWAP",
        #     mgnMode="isolated",
        # )
        # print(res)

        # res = await client.get_adjust_leverage(
        #     product_symbol="BTC-USDT-SWAP",
        #     instType="SWAP",
        #     mgnMode="cross",
        #     lever="3",
        # )
        # print(res)

        # res = await client.get_max_loan(
        #     product_symbol="BTC-USDT-SPOT",
        #     mgnMode="cross",
        #     mgnCcy="USDT",
        # )
        # print(res)

        # res = await client.get_fee_rates(
        #     product_symbol="BTC-USDT-SPOT",
        #     instType="SPOT",
        # )
        # print(res)

        # res = await client.get_interest_accrued(
        #     product_symbol="BTC-USDT-SPOT",
        # )
        # print(res)

        # res = await client.get_interest_rate()
        # print(res)

        # res = await client.set_greeks(greeksType="PA")
        # print(res)

        # res = await client.get_max_withdrawal()
        # print(res)

        # res = await client.get_interest_limits()
        # print(res)

        # res = await client.set_leverage(
        #     lever="10",
        #     mgnMode="isolated",
        # )
        # print(res)
    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
