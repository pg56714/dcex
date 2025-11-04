import asyncio

from dotenv import load_dotenv

import dcex.async_support as dcex

load_dotenv()


async def main():
    client = await dcex.zoomex()

    res = await client.get_instruments_info()
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
