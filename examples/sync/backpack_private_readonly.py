"""Read Backpack private account data."""

import os

import dcex


def require_env(name: str) -> str:
    """Return a required environment variable."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    """Run the Backpack private read-only example."""
    client = dcex.backpack(
        api_key=require_env("BACKPACK_API_KEY"),
        api_secret=require_env("BACKPACK_API_SECRET"),
        preload_product_table=False,
    )

    account = client.get_account()
    print(account)

    balances = client.get_balances()
    print(balances)

    client.close()


if __name__ == "__main__":
    main()
