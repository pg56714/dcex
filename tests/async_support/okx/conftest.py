"""OKX live test rate-limit guard."""

import asyncio
import os

import pytest_asyncio


@pytest_asyncio.fixture(autouse=True)
async def _okx_private_rate_limit() -> None:
    await asyncio.sleep(float(os.getenv("OKX_PRIVATE_TEST_DELAY_SECONDS", "2")))
