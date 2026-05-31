import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.kucoin()
    try:
        instruments = await client.get_spot_instrument_info()
        print(instruments)

        ticker = await client.get_spot_ticker(product_symbol="BTC-USDT-SPOT")
        print(ticker)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
