import asyncio

import dcex.async_support as dcex


async def main() -> None:
    client = await dcex.gateio()
    try:
        contracts = await client.get_all_futures_contracts(ccy="usdt")
        print(contracts)

        orderbook = await client.get_spot_order_book(product_symbol="BTC-USDT-SPOT")
        print(orderbook)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
