import dcex


def main() -> None:
    client = dcex.bitmart()

    pairs = client.get_trading_pairs()
    print(pairs)

    depth = client.get_depth(product_symbol="BTC-USDT-SWAP")
    print(depth)


if __name__ == "__main__":
    main()
