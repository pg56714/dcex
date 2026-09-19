"""Read Ondo Perps account data without modifying account state."""

import os

import dcex


def main() -> None:
    """Require Ondo API-key credentials before reading."""
    key_id = os.getenv("ONDO_API_KEY_ID") or None
    secret = os.getenv("ONDO_API_SECRET") or None
    if not (key_id and secret):
        raise RuntimeError("Set ONDO_API_KEY_ID and ONDO_API_SECRET.")
    client = dcex.ondo(
        api_key_id=key_id,
        api_secret=secret,
        preload_product_table=False,
    )
    try:
        print(client.get_account())
        print(client.get_balance())
        print(client.get_positions())
    finally:
        client.close()


if __name__ == "__main__":
    main()
