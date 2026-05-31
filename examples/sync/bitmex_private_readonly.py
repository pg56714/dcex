import os

import dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    client = dcex.bitmex(
        api_key=require_env("BITMEX_API_KEY"),
        api_secret=require_env("BITMEX_API_SECRET"),
    )

    wallet = client.get_wallet_summary()
    print(wallet)

    positions = client.get_positions()
    print(positions)


if __name__ == "__main__":
    main()
