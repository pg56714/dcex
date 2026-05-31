import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.hyperliquid()
    try:
        meta = await client.get_meta()
        print(meta)

        orderbook = await client.get_l2book(product_symbol="BTC-USD-SWAP")
        print(orderbook)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
