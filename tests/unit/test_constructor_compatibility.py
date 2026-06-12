"""Tests for retained public constructor parameters."""
# ruff: noqa: D103

import inspect
from typing import Any

import pytest

from dcex.async_support.bingx.client import Client as AsyncBingXClient
from dcex.async_support.bitmart.client import Client as AsyncBitmartClient
from dcex.async_support.bybit.client import Client as AsyncBybitClient
from dcex.async_support.hyperliquid.client import Client as AsyncHyperliquidClient
from dcex.async_support.okx.client import Client as AsyncOKXClient
from dcex.bingx.client import Client as BingXClient
from dcex.bitmart.client import Client as BitmartClient
from dcex.bybit.client import Client as BybitClient
from dcex.hyperliquid.client import Client as HyperliquidClient
from dcex.okx.client import Client as OKXClient


@pytest.mark.parametrize(
    ("client_type", "parameter_names"),
    [
        (BingXClient, {"max_retries", "retry_delay"}),
        (AsyncBingXClient, {"max_retries", "retry_delay"}),
        (BitmartClient, {"max_retries", "retry_delay"}),
        (AsyncBitmartClient, {"max_retries", "retry_delay"}),
        (BybitClient, {"max_retries", "retry_delay"}),
        (AsyncBybitClient, {"max_retries", "retry_delay"}),
        (HyperliquidClient, {"recv_window", "max_retries", "retry_delay"}),
        (AsyncHyperliquidClient, {"recv_window", "max_retries", "retry_delay"}),
        (OKXClient, {"max_retries", "retry_delay"}),
        (AsyncOKXClient, {"max_retries", "retry_delay"}),
    ],
)
def test_client_constructor_retains_configuration_parameters(
    client_type: type[Any],
    parameter_names: set[str],
) -> None:
    values = {name: 6000 if name == "recv_window" else 7 for name in parameter_names}
    client = client_type(preload_product_table=False, **values)

    try:
        for name, value in values.items():
            assert getattr(client, name) == value
    finally:
        close = getattr(client, "close", None)
        if close is not None and not inspect.iscoroutinefunction(close):
            close()
        else:
            session = getattr(client, "session", None)
            if session is not None and not inspect.iscoroutinefunction(session.close):
                session.close()
