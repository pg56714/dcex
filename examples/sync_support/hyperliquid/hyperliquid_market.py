import asyncio
import dcex.async_support as dcex


async def main():
    client = await dcex.hyperliquid()

    try:
        # spot: BTC-USDC-SPOT
        # swap: BTC-USD-SWAP
        result = await client.get_meta()
        print(result)

        result = await client.get_spot_meta()
        print(result)

        result = await client.get_meta_and_asset_ctxs()
        print(result)

        result = await client.get_spot_meta_and_asset_ctxs()
        print(result)

        result = await client.get_l2book(product_symbol="FLASK-USDC-SPOT")
        print(result)

        result = await client.get_candle_snapshot(
            product_symbol="BTC-USD-SWAP",
            interval="1m",
            startTime=1696128000000,
        )
        print(result)

        result = await client.get_funding_rate_history(
            product_symbol="BTC-USD-SWAP", startTime=1696128000000
        )
        print(result)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
