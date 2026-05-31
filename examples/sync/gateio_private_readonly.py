import os

import dcex


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example.")
    return value


def main() -> None:
    client = dcex.gateio(
        api_key=require_env("GATEIO_API_KEY"),
        api_secret=require_env("GATEIO_API_SECRET"),
    )

    futures_account = client.get_futures_account()
    print(futures_account)

    spot_account = client.get_spot_account(ccy="btc")
    print(spot_account)


if __name__ == "__main__":
    main()
