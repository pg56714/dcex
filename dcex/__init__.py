"""
dcex - dex & cex trading library.

A comprehensive library for cryptocurrency exchange interactions with both sync and async support.
Automatically handles Jupyter Notebook compatibility with nest_asyncio.
"""

from typing import Any

from .binance.client import Client as BinanceClient
from .bitmart.client import Client as BitmartClient
from .bitmex.client import Client as BitmexClient
from .bybit.client import Client as BybitClient
from .gateio.client import Client as GateioClient
from .okx.client import Client as OKXClient
from .utils.jupyter_helper import auto_apply_nest_asyncio

auto_apply_nest_asyncio(verbose=False)


# Create callable functions for each exchange (synchronous clients)
def binance(**kwargs: Any) -> BinanceClient:  # noqa: ANN401
    """Create a Binance client instance."""
    return BinanceClient(**kwargs)


def bitmart(**kwargs: Any) -> BitmartClient:  # noqa: ANN401
    """Create a BitMart client instance."""
    return BitmartClient(**kwargs)


def bitmex(**kwargs: Any) -> BitmexClient:  # noqa: ANN401
    """Create a BitMEX client instance."""
    return BitmexClient(**kwargs)


def bybit(**kwargs: Any) -> BybitClient:  # noqa: ANN401
    """Create a Bybit client instance."""
    return BybitClient(**kwargs)


def gateio(**kwargs: Any) -> GateioClient:  # noqa: ANN401
    """Create a Gate.io client instance."""
    return GateioClient(**kwargs)


def okx(**kwargs: Any) -> OKXClient:  # noqa: ANN401
    """Create an OKX client instance."""
    return OKXClient(**kwargs)


__all__ = [
    "binance",
    "bitmart",
    "bitmex",
    "bybit",
    "gateio",
    "okx",
]
