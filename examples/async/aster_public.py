"""Read Aster public market data asynchronously."""

import asyncio

import dcex.async_support as dcex


async def main() -> None:
    """Run the async Aster public market-data example."""
    client = await dcex.aster()
    try:
        exchange_info = await client.get_futures_exchange_info()
        print(exchange_info)

        klines = await client.get_futures_klines(
            product_symbol="BTC-USDT-SWAP",
            interval="1m",
            limit=5,
        )
        print(klines)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
