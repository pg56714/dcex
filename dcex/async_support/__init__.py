"""
Async exchange entry points.

This module exposes coroutine factory functions for each supported exchange,
which return an initialized async client (after awaiting `async_init`).
"""

# Import exchange client classes and create callable functions
from typing import Any, cast

from .binance.client import Client as BinanceClient
from .bingx.client import Client as BingXClient
from .bitmart.client import Client as BitmartClient
from .bitmex.client import Client as BitmexClient
from .bybit.client import Client as BybitClient
from .gateio.client import Client as GateioClient
from .hyperliquid.client import Client as HyperliquidClient
from .kucoin.client import Client as KuCoinClient
from .okx.client import Client as OKXClient
from .zoomex.client import Client as ZoomexClient


async def binance(
    **kwargs: Any,  # noqa: ANN401
) -> BinanceClient:
    """Create and initialize a Binance client instance."""
    return cast(BinanceClient, await BinanceClient(**kwargs).async_init())


async def bingx(
    **kwargs: Any,  # noqa: ANN401
) -> BingXClient:
    """Create and initialize a BingX client instance."""
    return cast(BingXClient, await BingXClient(**kwargs).async_init())


async def bitmart(
    **kwargs: Any,  # noqa: ANN401
) -> BitmartClient:
    """Create and initialize a BitMart client instance."""
    return cast(BitmartClient, await BitmartClient(**kwargs).async_init())


async def bitmex(
    **kwargs: Any,  # noqa: ANN401
) -> BitmexClient:
    """Create and initialize a BitMEX client instance."""
    return cast(BitmexClient, await BitmexClient(**kwargs).async_init())


async def bybit(
    **kwargs: Any,  # noqa: ANN401
) -> BybitClient:
    """Create and initialize a Bybit client instance."""
    return cast(BybitClient, await BybitClient(**kwargs).async_init())


async def gateio(
    **kwargs: Any,  # noqa: ANN401
) -> GateioClient:
    """Create and initialize a Gate.io client instance."""
    return cast(GateioClient, await GateioClient(**kwargs).async_init())


async def hyperliquid(
    **kwargs: Any,  # noqa: ANN401
) -> HyperliquidClient:
    """Create and initialize a Hyperliquid client instance."""
    return cast(HyperliquidClient, await HyperliquidClient(**kwargs).async_init())


async def kucoin(
    **kwargs: Any,  # noqa: ANN401
) -> KuCoinClient:
    """Create and initialize a KuCoin client instance."""
    return cast(KuCoinClient, await KuCoinClient(**kwargs).async_init())


async def okx(
    **kwargs: Any,  # noqa: ANN401
) -> OKXClient:
    """Create and initialize an OKX client instance."""
    return cast(OKXClient, await OKXClient(**kwargs).async_init())


async def zoomex(
    **kwargs: Any,  # noqa: ANN401
) -> ZoomexClient:
    """Create and initialize a Zoomex client instance."""
    return cast(ZoomexClient, await ZoomexClient(**kwargs).async_init())


__all__ = [
    "binance",
    "bingx",
    "bitmart",
    "bitmex",
    "bybit",
    "gateio",
    "hyperliquid",
    "kucoin",
    "okx",
    "zoomex",
]
