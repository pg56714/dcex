"""OKX live test rate-limit guard."""

import os
import time

import pytest


@pytest.fixture(autouse=True)
def _okx_private_rate_limit() -> None:
    time.sleep(float(os.getenv("OKX_PRIVATE_TEST_DELAY_SECONDS", "2")))
