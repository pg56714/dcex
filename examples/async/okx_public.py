import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.okx()
    try:
        instruments = await client.get_public_instruments(instType="SPOT")
        print(instruments)

        orderbook = await client.get_orderbook(product_symbol="BTC-USDT-SPOT")
        print(orderbook)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
