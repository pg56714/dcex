import dcex


def main() -> None:
    client = dcex.bitget()

    spot_symbols = client.get_uta_instruments("SPOT", product_symbol="BTC-USDT-SPOT")
    print(spot_symbols)

    orderbook = client.get_uta_orderbook("USDT-FUTURES", product_symbol="BTC-USDT-SWAP", limit=5)
    print(orderbook)


if __name__ == "__main__":
    main()
