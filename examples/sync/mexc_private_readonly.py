import os

import dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    client = dcex.mexc(
        api_key=require_env("MEXC_API_KEY"),
        api_secret=require_env("MEXC_API_SECRET"),
    )

    spot_account = client.get_spot_account()
    print(spot_account)

    contract_assets = client.get_contract_assets()
    print(contract_assets)


if __name__ == "__main__":
    main()
