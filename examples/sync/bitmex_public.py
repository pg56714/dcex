import dcex


def main() -> None:
    client = dcex.bitmex()

    orderbook = client.get_orderbook(product_symbol="XBT-USDT-SWAP")
    print(orderbook)

    ticker = client.get_ticker(symbol="XBT-USDT-SWAP", binSize="1m", count=5)
    print(ticker)


if __name__ == "__main__":
    main()
