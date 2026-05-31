import os

import dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    wallet_address = require_env("HYPERLIQUID_WALLET_ADDRESS")
    client = dcex.hyperliquid()

    state = client.clearinghouse_state(user=wallet_address)
    print(state)

    open_orders = client.open_orders(user=wallet_address)
    print(open_orders)


if __name__ == "__main__":
    main()
