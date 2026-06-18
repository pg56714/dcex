import os

import dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    client = dcex.bingx(
        api_key=require_env("BINGX_API_KEY"),
        api_secret=require_env("BINGX_API_SECRET"),
    )

    balance = client.get_account_balance()
    print(balance)

    positions = client.get_open_positions(product_symbol="BTC-USDT-SWAP")
    print(positions)


if __name__ == "__main__":
    main()
