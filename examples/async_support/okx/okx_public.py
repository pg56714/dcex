import asyncio

import dcex.async_support as dcex


async def main():
    client = await dcex.okx()

    try:
        res = await client.get_public_instruments(instType="SPOT")
        print(res)

        res = await client.get_funding_rate(product_symbol="BTC-USDT-SWAP")
        print(res)

        res = await client.get_funding_rate_history(product_symbol="BTC-USDT-SWAP")
        print(res)

        res = await client.get_position_tiers(
            instType="SWAP",
            tdMode="isolated",
            instFamily="BTC-USDT",
            product_symbol="BTC-USDT-SWAP",
        )
        print(res)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
