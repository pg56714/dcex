"""Offline coverage for aster network and nonce."""
# ruff: noqa: ANN001, ANN201, D103

import pytest


@pytest.mark.parametrize(
    "base_urls,expected",
    [
        ({}, "https://papi.asterdex.com"),
        (
            {
                "spot_base_url": "https://sapi.asterdex-testnet.com",
                "futures_base_url": "https://fapi.asterdex-testnet.com",
            },
            "https://papi.asterdex-testnet.com",
        ),
    ],
)
def test_aster_prediction_follows_network(base_urls, expected):
    from dcex.aster.client import Client

    client = Client(preload_product_table=False, **base_urls)
    try:
        assert client.prediction_base_url == expected
    finally:
        client.close()


@pytest.mark.parametrize("key", ["spot_base_url", "futures_base_url"])
def test_aster_rejects_mixed_network_defaults(key):
    from dcex.aster.client import Client

    with pytest.raises(ValueError, match="network"):
        Client(preload_product_table=False, **{key: "https://fapi.asterdex-testnet.com"})


def test_aster_nonce_reservations_are_unique_and_current():
    import time
    from concurrent.futures import ThreadPoolExecutor

    from dcex.aster.client import Client

    client = Client(preload_product_table=False)
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            values = list(pool.map(lambda _: client.reserve_nonce(), range(100)))
        assert len(set(values)) == 100
        assert all(abs(time.time_ns() // 1000 - value) < 60_000_000 for value in values)
    finally:
        client.close()
