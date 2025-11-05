import asyncio
import dcex.async_support as dcex
import os
from dotenv import load_dotenv

load_dotenv()

HYPERLIQUID_WALLET_ADDRESS = os.getenv("HYPERLIQUID_WALLET_ADDRESS")

async def main():
    if HYPERLIQUID_WALLET_ADDRESS is None:
        raise ValueError("HYPERLIQUID_WALLET_ADDRESS is not set in the environment variables")

    # HYPERLIQUID_WALLET_ADDRESS = ""

    client = await dcex.hyperliquid()

    try:
        result = await client.clearinghouse_state(user=HYPERLIQUID_WALLET_ADDRESS)
        print(result)

        result = await client.open_orders(user=HYPERLIQUID_WALLET_ADDRESS)
        print(result)

        result = await client.user_fills(user=HYPERLIQUID_WALLET_ADDRESS)
        print(result)

        result = await client.user_rate_limit(user=HYPERLIQUID_WALLET_ADDRESS)
        print(result)

        # result = await client.order_status(user=HYPERLIQUID_WALLET_ADDRESS, oid=221338024517)
        # print(result)

        result = await client.historical_orders(user=HYPERLIQUID_WALLET_ADDRESS)
        print(result)

        result = await client.subaccounts(user=HYPERLIQUID_WALLET_ADDRESS)
        print(result)

        result = await client.user_role(user=HYPERLIQUID_WALLET_ADDRESS)
        print(result)

        result = await client.portfolio(user=HYPERLIQUID_WALLET_ADDRESS)
        print(result)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
