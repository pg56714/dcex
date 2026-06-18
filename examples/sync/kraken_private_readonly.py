import os

import dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    client = dcex.kraken(
        api_key=require_env("KRAKEN_API_KEY"),
        api_secret=require_env("KRAKEN_API_SECRET"),
    )

    balance = client.get_spot_account_balance()
    print(balance)

    open_orders = client.get_spot_open_orders()
    print(open_orders)


if __name__ == "__main__":
    main()
