import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.mexc()
    try:
        exchange_info = await client.get_spot_exchange_info(product_symbol="BTC-USDT-SPOT")
        print(exchange_info)

        orderbook = await client.get_contract_depth(product_symbol="BTC-USDT-SWAP", limit=5)
        print(orderbook)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
