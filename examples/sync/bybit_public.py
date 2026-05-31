import dcex


def main() -> None:
    client = dcex.bybit()

    instruments = client.get_instruments_info(product_symbol="BTC-USDT-SWAP")
    print(instruments)

    orderbook = client.get_orderbook(product_symbol="BTC-USDT-SWAP", limit=50)
    print(orderbook)


if __name__ == "__main__":
    main()
