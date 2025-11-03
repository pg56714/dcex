import asyncio
import os

from dotenv import load_dotenv

import dcex.async_support as dcex

load_dotenv()

async def main():
    try:
        client = await dcex.kucoin()
        instrument_info = await client.get_spot_instrument_info()
        print(instrument_info)

        ticker = await client.get_spot_ticker(product_symbol="BTC-USDT-SPOT")
        print(ticker)

        all_tickers = await client.get_spot_all_tickers()
        print(all_tickers)

        orderbook = await client.get_spot_orderbook(product_symbol="BTC-USDT-SPOT")
        print(orderbook)

        public_trades = await client.get_spot_public_trades(product_symbol="BTC-USDT-SPOT")
        print(public_trades)

        kline = await client.get_spot_kline(product_symbol="BTC-USDT-SPOT", timeframe="1m")
        print(kline)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
