import os

import dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    client = dcex.okx(
        api_key=require_env("OKX_API_KEY"),
        api_secret=require_env("OKX_API_SECRET"),
        passphrase=require_env("OKX_PASSPHRASE"),
    )

    balance = client.get_account_balance()
    print(balance)

    orders = client.get_order_list(product_symbol="BTC-USDT-SPOT")
    print(orders)


if __name__ == "__main__":
    main()
