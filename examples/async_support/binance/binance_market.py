import asyncio

import dcex.async_support as dcex


async def main():
    client = await dcex.binance()

    try:
        result = await client.get_spot_exchange_info(product_symbol="BTC-USDT-SPOT")
        print(result)

        result = await client.get_futures_exchange_info()
        print(result)

        result = await client.get_futures_ticker(product_symbol="BTC-USDT-SWAP")
        print(result)

        result = await client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m")
        print(result)

        result = await client.get_futures_premium_index(product_symbol="BTC-USDT-SWAP")
        print(result)

        result = await client.get_futures_funding_rate(product_symbol="BTC-USDT-SWAP")
        print(result)

        result = await client.get_spot_price(product_symbol="BTC-USDT-SWAP")
        print(result)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
