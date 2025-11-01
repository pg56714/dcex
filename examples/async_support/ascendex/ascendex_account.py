import asyncio
import os

from dotenv import load_dotenv

import dcex.async_support as dcex

load_dotenv()


ASCENDEX_API_KEY = os.getenv("ASCENDEX_API_KEY")
ASCENDEX_API_SECRET = os.getenv("ASCENDEX_API_SECRET")


async def main():
    client = await dcex.ascendex(
        api_key=ASCENDEX_API_KEY,
        api_secret=ASCENDEX_API_SECRET,
    )

    try:
        account_info = await client.get_account_info()
        print(account_info)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
