import dcex

client = dcex.binance()

# result = client.get_spot_exchange_info(product_symbol="BTC-USDT-SPOT")
# print(result)

result = client.get_futures_exchange_info()
print(result)

# result = client.get_futures_ticker(product_symbol="BTC-USDT-SWAP")
# print(result)

# result = client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m")
# print(result)

# result = client.get_futures_premium_index(product_symbol="BTC-USDT-SWAP")
# print(result)

# result = client.get_futures_funding_rate(product_symbol="BTC-USDT-SWAP")
# print(result)
