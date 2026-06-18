import dcex


def main() -> None:
    client = dcex.kucoin()

    instruments = client.get_spot_instrument_info()
    print(instruments)

    ticker = client.get_spot_ticker(product_symbol="BTC-USDT-SPOT")
    print(ticker)


if __name__ == "__main__":
    main()
