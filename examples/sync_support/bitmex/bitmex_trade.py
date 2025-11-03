import os

from dotenv import load_dotenv

import dcex

load_dotenv()

BITMEX_API_KEY = os.getenv("BITMEX_API_KEY")
BITMEX_API_SECRET = os.getenv("BITMEX_API_SECRET")


client = dcex.bitmex(
    api_key=BITMEX_API_KEY,
    api_secret=BITMEX_API_SECRET,
)

# order = client.place_market_buy_order(
#     product_symbol="XRP-USDT-SPOT",
#     orderQty=1000000,  # 1000000 XRP = 2 USDT
# )
# print(order)

# order = client.place_market_sell_order(
#     product_symbol="XRP-USDT-SPOT",
#     orderQty=1000000,
# )
# print(order)

# order = client.place_limit_buy_order(
#     product_symbol="XRP-USDT-SWAP",
#     orderQty=100,
#     price=2,
# )
# print(order)

# order = client.place_limit_sell_order(
#     product_symbol="XRP-USDT-SWAP",
#     orderQty=100,
#     price=3,
# )
# print(order)
# print(client.get_rate_limit_info())

# order = client.place_post_only_buy_order(
#     product_symbol="XRP-USDT-SWAP",
#     orderQty=100,
#     price=2,
# )
# print(order)

# order = client.place_post_only_sell_order(
#     product_symbol="XRP-USDT-SWAP",
#     orderQty=100,
#     price=3,
# )
# print(order)

# order = client.amend_order(
#     orderID="38c2bddf-c6f0-4765-9660-27f8da1d271f",
#     price=2.2,
# )
# print(order)

# order = client.cancel_order(
#     orderID="38c2bddf-c6f0-4765-9660-27f8da1d271f",
# )
# print(order)

# order = client.cancel_all_orders(
#     product_symbol="XRP-USDT-SWAP",
# )
# print(order)

order = client.get_order(
    product_symbol="XRP-USDT-SWAP",
)
print(order)
print(client.get_rate_limit_info())
