"""Read Aster public market data."""

import dcex


def main() -> None:
    """Run the Aster public market-data example."""
    client = dcex.aster()

    exchange_info = client.get_futures_exchange_info()
    print(exchange_info)

    klines = client.get_futures_klines(product_symbol="BTC-USDT-SWAP", interval="1m", limit=5)
    print(klines)


if __name__ == "__main__":
    main()
