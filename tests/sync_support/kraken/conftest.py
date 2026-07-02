"""Kraken live test rate-limit guard."""

import os
import time

import pytest


@pytest.fixture(autouse=True)
def _kraken_private_rate_limit() -> None:
    time.sleep(float(os.getenv("KRAKEN_PRIVATE_TEST_DELAY_SECONDS", "8")))
