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

# result = client.set_leverage(
#     product_symbol="XRP-USDT-SWAP",
#     leverage=3,
# )
# print(result)

# result = client.place_market_buy_order(
#     product_symbol="XRP-USDT-SWAP",
#     quantity="5",
# )
# print(result)

# result = client.place_market_sell_order(
#     product_symbol="XRP-USDT-SWAP",
#     quantity="5",
# )
# print(result)

# result = client.place_limit_buy_order(
#     product_symbol="XRP-USDT-SWAP",
#     quantity="5",
#     price="2.2",
# )
# print(result)

# result = client.place_limit_sell_order(
#     product_symbol="XRP-USDT-SWAP",
#     quantity="5",
#     price="3",
# )
# print(result)

# result = client.place_post_only_limit_buy_order(
#     product_symbol="XRP-USDT-SWAP",
#     quantity="5",
#     price="2.2",
# )
# print(result)

# result = client.place_post_only_limit_sell_order(
#     product_symbol="XRP-USDT-SWAP",
#     quantity="5",
#     price="3",
# )
# print(result)

# result = client.cancel_order(
#     product_symbol="XRP-USDT-SWAP",
#     orderId=127620249437,
# )
# print(result)

# result = client.get_order(
#     product_symbol="XRP-USDT-SWAP",
#     orderId=127620249437,
# )
# print(result)

# result = client.cancel_all_open_orders(
#     product_symbol="XRP-USDT-SWAP",
# )
# print(result)

# result = client.get_future_all_order(
#     product_symbol="XRP-USDT-SWAP",
# )
# print(result)

# result = client.get_open_orders(
#     product_symbol="XRP-USDT-SWAP",
#     orderId="127620978829",
# )
# print(result)

# result = client.get_future_position(
#     product_symbol="XRP-USDT-SWAP",
# )
# print(result)
