"""
Every Binance wrapper parameter must be a field the official endpoint documents.

The native client rejects undocumented fields before sending (see
``scripts/build_binance_official_fields.py``). Calling each public wrapper with every
optional argument filled proves the Python surface never trips that check.
"""

from __future__ import annotations

import inspect
from decimal import Decimal
from typing import Any

import pytest

from dcex import _native
from dcex.binance.client import Client
from tests.unit.native_http_helpers import _http_server


def _placeholder(parameter: inspect.Parameter) -> Any:  # noqa: ANN401
    annotation = str(parameter.annotation)
    if "bool" in annotation:
        return True
    if "int" in annotation:
        return 1
    if "Decimal" in annotation or "float" in annotation:
        return Decimal(1)
    if "list" in annotation or "Sequence" in annotation:
        return ["1"]
    if "dict" in annotation or "Mapping" in annotation:
        return {"symbol": "BTCUSDT"}
    if parameter.name in {"product_symbol", "symbol"}:
        return "BTCUSDT"
    return "1"


def _methods() -> list[str]:
    return sorted(
        name
        for name, member in inspect.getmembers(Client, inspect.isfunction)
        if not name.startswith("_") and name not in {"close"}
    )


@pytest.fixture(scope="module")
def client() -> Any:  # noqa: ANN401
    """One client against a local server answering every request at once."""
    with _http_server({"code": 0, "serverTime": 1}) as (base_url, _received):
        client = Client(api_key="key", api_secret="secret", preload_product_table=False)
        client._native_client = _native.BinanceHttpClient(
            api_key="key",
            api_secret="secret",
            timeout=5,
            spot_base_url=base_url,
            futures_base_url=base_url,
            options_base_url=base_url,
            coin_futures_base_url=base_url,
            portfolio_margin_base_url=base_url,
            alpha_base_url=base_url,
        )
        yield client
        client.close()


@pytest.mark.parametrize("name", _methods())
def test_every_wrapper_argument_is_an_official_field(client: Any, name: str) -> None:  # noqa: ANN401
    """Each sync wrapper, with every argument filled, passes the official field check."""
    method = getattr(client, name)
    parameters = [
        parameter
        for parameter in inspect.signature(method).parameters.values()
        if parameter.kind not in {parameter.VAR_KEYWORD, parameter.VAR_POSITIONAL}
    ]
    kwargs = {parameter.name: _placeholder(parameter) for parameter in parameters}
    try:
        method(**kwargs)
    except Exception as error:  # noqa: BLE001 - only the field check matters here
        assert "unsupported Binance parameter" not in str(error), f"{name}: {error}"


def _async_methods() -> list[str]:
    from dcex.async_support.binance.client import Client as AsyncClient

    return sorted(
        name
        for name, member in inspect.getmembers(AsyncClient, inspect.iscoroutinefunction)
        if not name.startswith("_") and name not in {"close", "async_init"}
    )


@pytest.mark.asyncio
async def test_every_async_wrapper_argument_is_an_official_field() -> None:
    """Each async wrapper, with every argument filled, passes the official field check."""
    from dcex.async_support.binance.client import Client as AsyncClient

    with _http_server({"code": 0, "serverTime": 1}) as (base_url, _received):
        client = AsyncClient(api_key="key", api_secret="secret", preload_product_table=False)
        await client.async_init()
        client._native_client = _native.BinanceHttpClient(
            api_key="key",
            api_secret="secret",
            timeout=5,
            spot_base_url=base_url,
            futures_base_url=base_url,
            options_base_url=base_url,
            coin_futures_base_url=base_url,
            portfolio_margin_base_url=base_url,
            alpha_base_url=base_url,
        )
        rejected = []
        for name in _async_methods():
            method = getattr(client, name)
            parameters = [
                parameter
                for parameter in inspect.signature(method).parameters.values()
                if parameter.kind not in {parameter.VAR_KEYWORD, parameter.VAR_POSITIONAL}
            ]
            kwargs = {parameter.name: _placeholder(parameter) for parameter in parameters}
            try:
                await method(**kwargs)
            except Exception as error:  # noqa: BLE001 - only the field check matters here
                if "unsupported Binance parameter" in str(error):
                    rejected.append(f"{name}: {error}")
        closed = client.close()
        if inspect.isawaitable(closed):
            await closed
    assert not rejected, rejected
