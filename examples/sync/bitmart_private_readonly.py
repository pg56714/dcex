import os

import dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    client = dcex.bitmart(
        api_key=require_env("BITMART_API_KEY"),
        api_secret=require_env("BITMART_API_SECRET"),
        memo=require_env("BITMART_MEMO"),
    )

    balance = client.get_account_balance()
    print(balance)

    wallet = client.get_spot_wallet()
    print(wallet)


if __name__ == "__main__":
    main()
