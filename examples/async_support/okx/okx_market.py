import asyncio

import dcex.async_support as dcex


async def main():
    client = await dcex.okx()

    try:
        res = await client.get_candles_ticks(product_symbol="BTC-USDT-SPOT")
        print(res)

        res = await client.get_orderbook(product_symbol="BTC-USDT-SPOT")
        print(res)

        res = await client.get_tickers(instType="SPOT")
        print(res)

        res = await client.get_public_trades(product_symbol="BTC-USDT-SPOT")
        print(res)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
