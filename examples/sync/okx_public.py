import dcex


def main() -> None:
    client = dcex.okx()

    instruments = client.get_public_instruments(instType="SPOT")
    print(instruments)

    orderbook = client.get_orderbook(product_symbol="BTC-USDT-SPOT")
    print(orderbook)


if __name__ == "__main__":
    main()
