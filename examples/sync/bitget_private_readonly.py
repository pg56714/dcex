import os

import dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    client = dcex.bitget(
        api_key=require_env("BITGET_API_KEY"),
        api_secret=require_env("BITGET_API_SECRET"),
        passphrase=require_env("BITGET_PASSPHRASE"),
    )

    spot_assets = client.get_uta_account_assets()
    print(spot_assets)

    futures_positions = client.get_uta_positions(category="USDT-FUTURES")
    print(futures_positions)


if __name__ == "__main__":
    main()
