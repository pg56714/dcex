import os

from dotenv import load_dotenv

import dcex

load_dotenv()

BITMART_API_KEY = os.getenv("BITMART_API_KEY")
BITMART_API_SECRET = os.getenv("BITMART_API_SECRET")
MEMO = os.getenv("BITMART_MEMO")

client = dcex.bitmart(
    api_key=BITMART_API_KEY,
    api_secret=BITMART_API_SECRET,
    memo=MEMO,
)


res = client.get_account_balance()
print("1. get_account_balance:", res)

res = client.get_account_currencies()
print("2. get_account_currencies:", res)

res = client.get_spot_wallet()
print("3. get_spot_wallet:", res)

res = client.get_deposit_address(currency="BTC")
print("4. get_deposit_address:", res)

# res = client.get_withdraw_charge(currency="BTC")
# print("5. get_withdraw_charge:", res)

res = client.get_deposit_withdraw_history(currency="USDT")
print("6. get_deposit_withdraw_history:", res)

# res = client.get_deposit_withdraw_history_detail(id="26695771")
# print("7. get_deposit_withdraw_history_detail:", res)

res = client.get_contract_assets()
print("8. get_contract_assets:", res)
