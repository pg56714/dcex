"""Read Ondo Perps public market data asynchronously."""

import asyncio

import dcex.async_support as dcex


async def main() -> None:
    """Read market metadata and one order book without credentials."""
    client = await dcex.ondo(preload_product_table=False)
    try:
        markets = await client.get_markets()
        pairs = markets["result"]["perps"]["tradingPairs"]
        market = next(pair["market"] for pair in pairs if not pair.get("disabled"))
        print("market:", market)
        print("depth success:", (await client.get_depth(market))["success"])
        print("funding success:", (await client.get_funding_rates(market))["success"])
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
