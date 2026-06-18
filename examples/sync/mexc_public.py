import dcex


def main() -> None:
    client = dcex.mexc()

    exchange_info = client.get_spot_exchange_info(product_symbol="BTC-USDT-SPOT")
    print(exchange_info)

    orderbook = client.get_contract_depth(product_symbol="BTC-USDT-SWAP", limit=5)
    print(orderbook)


if __name__ == "__main__":
    main()
