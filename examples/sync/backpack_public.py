"""Read Backpack public market data."""

import dcex


def main() -> None:
    """Run the Backpack public market-data example."""
    client = dcex.backpack(preload_product_table=False)

    markets = client.get_markets()
    print(markets)

    time_response = client.get_time()
    print(time_response)

    client.close()


if __name__ == "__main__":
    main()
