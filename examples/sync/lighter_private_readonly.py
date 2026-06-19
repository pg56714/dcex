"""Read Lighter private account state."""

import os

import dcex


def require_env(name: str) -> str:
    """Return a required environment variable."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    """Run the private read-only Lighter example."""
    account_index = int(require_env("LIGHTER_ACCOUNT_INDEX"))
    api_key_index = int(require_env("LIGHTER_API_KEY_INDEX"))
    api_private_key = require_env("LIGHTER_API_PRIVATE_KEY")

    client = dcex.lighter(
        account_index=account_index,
        api_key_index=api_key_index,
        api_private_key=api_private_key,
    )
    try:
        account = client.get_account(by="index", value=str(account_index))
        print(account)

        limits = client.get_account_limits()
        print(limits)

        active_orders = client.get_account_active_orders()
        print(active_orders)
    finally:
        client.close()


if __name__ == "__main__":
    main()
