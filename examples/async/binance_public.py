import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.binance()
    try:
        exchange_info = await client.get_futures_exchange_info()
        print(exchange_info)

        klines = await client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m")
        print(klines)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
