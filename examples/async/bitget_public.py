import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.bitget()
    try:
        spot_symbols = await client.get_spot_symbols(product_symbol="BTC-USDT-SPOT")
        print(spot_symbols)

        orderbook = await client.get_futures_orderbook(
            product_symbol="BTC-USDT-SWAP",
            limit=5,
        )
        print(orderbook)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
