import dcex


def main() -> None:
    client = dcex.hyperliquid()

    meta = client.get_meta()
    print(meta)

    orderbook = client.get_l2book(product_symbol="BTC-USD-SWAP")
    print(orderbook)


if __name__ == "__main__":
    main()
