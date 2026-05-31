import dcex


def main() -> None:
    client = dcex.gateio()

    contracts = client.get_all_futures_contracts(ccy="usdt")
    print(contracts)

    orderbook = client.get_spot_order_book(product_symbol="BTC-USDT-SPOT")
    print(orderbook)


if __name__ == "__main__":
    main()
