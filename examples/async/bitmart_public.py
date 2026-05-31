import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.bitmart()
    try:
        pairs = await client.get_trading_pairs()
        print(pairs)

        depth = await client.get_depth(product_symbol="BTC-USDT-SWAP")
        print(depth)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
