"""Read Backpack public market data asynchronously."""

import asyncio

import dcex.async_support as dcex


async def main() -> None:
    """Run the async Backpack public market-data example."""
    client = await dcex.backpack(preload_product_table=False)
    try:
        markets = await client.get_markets()
        print(markets)

        time_response = await client.get_time()
        print(time_response)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
