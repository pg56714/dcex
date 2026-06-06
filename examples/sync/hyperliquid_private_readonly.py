"""Read Hyperliquid private account state with optional agent resolution."""

import os

import dcex


def require_env(name: str) -> str:
    """Return a required environment variable."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    """Run the private read-only Hyperliquid example."""
    wallet_address = require_env("HYPERLIQUID_WALLET_ADDRESS")
    client = dcex.hyperliquid()

    role = client.user_role(user=wallet_address)
    if isinstance(role, dict) and role.get("role") == "agent":
        wallet_address = role.get("data", {}).get("user", wallet_address)

    state = client.clearinghouse_state(user=wallet_address)
    print(state)

    spot_state = client.spot_clearinghouse_state(user=wallet_address)
    print(spot_state)

    open_orders = client.open_orders(user=wallet_address)
    print(open_orders)


if __name__ == "__main__":
    main()
