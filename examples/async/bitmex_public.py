import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.bitmex()
    try:
        orderbook = await client.get_orderbook(product_symbol="XBT-USDT-SWAP")
        print(orderbook)

        ticker = await client.get_ticker(symbol="XBT-USDT-SWAP", binSize="1m", count=5)
        print(ticker)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
