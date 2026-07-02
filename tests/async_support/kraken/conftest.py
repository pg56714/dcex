"""Kraken live test rate-limit guard."""

import asyncio
import os

import pytest_asyncio


@pytest_asyncio.fixture(autouse=True)
async def _kraken_private_rate_limit() -> None:
    await asyncio.sleep(float(os.getenv("KRAKEN_PRIVATE_TEST_DELAY_SECONDS", "8")))
