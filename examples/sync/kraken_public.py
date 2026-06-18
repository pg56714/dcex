import dcex


def main() -> None:
    client = dcex.kraken()

    server_time = client.get_server_time()
    print(server_time)

    orderbook = client.get_spot_orderbook(product_symbol="BTC-USDT-SPOT", count=5)
    print(orderbook)


if __name__ == "__main__":
    main()
