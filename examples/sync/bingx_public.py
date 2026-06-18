import dcex


def main() -> None:
    client = dcex.bingx()

    ticker = client.get_ticker(product_symbol="BTC-USDT-SWAP")
    print(ticker)

    orderbook = client.get_spot_orderbook(product_symbol="BTC-USDT-SPOT", limit=5)
    print(orderbook)


if __name__ == "__main__":
    main()
