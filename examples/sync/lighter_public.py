import dcex


def main() -> None:
    client = dcex.lighter()
    try:
        details = client.get_order_book_details()
        print(details)

        markets = details.get("order_book_details", []) if isinstance(details, dict) else []
        active = next((market for market in markets if market.get("status") == "active"), None)
        if active is not None:
            order_book = client.get_order_books(market_id=int(active["market_id"]))
            print(order_book)
    finally:
        client.close()


if __name__ == "__main__":
    main()
