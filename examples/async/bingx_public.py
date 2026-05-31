import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.bingx()
    try:
        instruments = await client.get_swap_instrument_info(product_symbol="BTC-USDT-SWAP")
        print(instruments)

        orderbook = await client.get_orderbook("BTC-USDT-SWAP", limit=10)
        print(orderbook)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
