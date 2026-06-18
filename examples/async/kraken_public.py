import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.kraken()
    try:
        server_time = await client.get_server_time()
        print(server_time)

        orderbook = await client.get_spot_orderbook(
            product_symbol="BTC-USDT-SPOT",
            count=5,
        )
        print(orderbook)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
