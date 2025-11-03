import os

from dotenv import load_dotenv

import dcex

load_dotenv()


client = dcex.gateio(
    api_key=os.getenv("GATEIO_API_KEY"),
    api_secret=os.getenv("GATEIO_API_SECRET"),
)

result = client.get_futures_account()
print(result)

result = client.get_futures_account_book()
print(result)

result = client.get_delivery_account()
print(result)

result = client.get_delivery_account_book()
print(result)

result = client.get_spot_account(ccy="btc")
print(result)

result = client.get_spot_account_book()
print(result)
