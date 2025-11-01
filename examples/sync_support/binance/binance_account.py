import os

from dotenv import load_dotenv

import dcex

load_dotenv()


BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")


client = dcex.binance(
    api_key=BINANCE_API_KEY,
    api_secret=BINANCE_API_SECRET,
)

result = client.get_account_balance(market_type="spot")
print(result)

result = client.get_income_history()
print(result)
