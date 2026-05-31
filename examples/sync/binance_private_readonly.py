import os

import dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    client = dcex.binance(
        api_key=require_env("BINANCE_API_KEY"),
        api_secret=require_env("BINANCE_API_SECRET"),
    )

    balance = client.get_account_balance(market_type="spot")
    print(balance)

    income = client.get_income_history()
    print(income)


if __name__ == "__main__":
    main()
