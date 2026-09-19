"""Read Ondo Perps public market data."""

import dcex


def main() -> None:
    """Read market metadata and one order book without credentials."""
    client = dcex.ondo(preload_product_table=False)
    try:
        markets = client.get_markets()
        pairs = markets["result"]["perps"]["tradingPairs"]
        market = next(pair["market"] for pair in pairs if not pair.get("disabled"))
        print("market:", market)
        print("depth success:", client.get_depth(market)["success"])
        print("funding success:", client.get_funding_rates(market)["success"])
    finally:
        client.close()


if __name__ == "__main__":
    main()
