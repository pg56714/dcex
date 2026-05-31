import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.bybit()
    try:
        instruments = await client.get_instruments_info(product_symbol="BTC-USDT-SWAP")
        print(instruments)

        orderbook = await client.get_orderbook(product_symbol="BTC-USDT-SWAP", limit=50)
        print(orderbook)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
