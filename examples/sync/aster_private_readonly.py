"""Read Aster private account data."""

import os

import dcex


def require_env(name: str) -> str:
    """Read a required environment variable."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    """Run the Aster private read-only example."""
    client = dcex.aster(
        user_address=require_env("ASTER_USER_ADDRESS"),
        signer_address=require_env("ASTER_SIGNER_ADDRESS"),
        private_key=require_env("ASTER_PRIVATE_KEY"),
    )

    spot_account = client.get_spot_account()
    print(spot_account)

    futures_balance = client.get_futures_balance()
    print(futures_balance)


if __name__ == "__main__":
    main()
