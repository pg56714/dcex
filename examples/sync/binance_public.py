import dcex


def main() -> None:
    client = dcex.binance()

    exchange_info = client.get_futures_exchange_info()
    print(exchange_info)

    klines = client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m")
    print(klines)


if __name__ == "__main__":
    main()
