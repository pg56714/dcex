"""
Async exchange entry points.

This module exposes coroutine factory functions for each supported exchange,
which return an initialized async client (after awaiting `async_init`).
"""

# Import exchange client classes and create callable functions
from typing import Any, cast

from .aster.client import Client as AsterClient
from .backpack.client import Client as BackpackClient
from .binance.client import Client as BinanceClient
from .bingx.client import Client as BingXClient
from .bitget.client import Client as BitgetClient
from .bybit.client import Client as BybitClient
from .extended.client import Client as ExtendedClient
from .hyperliquid.client import Client as HyperliquidClient
from .kraken.client import Client as KrakenClient
from .kucoin.client import Client as KuCoinClient
from .lighter.client import Client as LighterClient
from .mexc.client import Client as MEXCClient
from .okx.client import Client as OKXClient


async def aster(
    **kwargs: Any,  # noqa: ANN401
) -> AsterClient:
    """Create and initialize an Aster client instance."""
    return cast(AsterClient, await AsterClient(**kwargs).async_init())


async def backpack(
    **kwargs: Any,  # noqa: ANN401
) -> BackpackClient:
    """Create and initialize a Backpack client instance."""
    return cast(BackpackClient, await BackpackClient(**kwargs).async_init())


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


async def bitget(
    **kwargs: Any,  # noqa: ANN401
) -> BitgetClient:
    """Create and initialize a Bitget client instance."""
    return cast(BitgetClient, await BitgetClient(**kwargs).async_init())


async def bybit(
    **kwargs: Any,  # noqa: ANN401
) -> BybitClient:
    """Create and initialize a Bybit client instance."""
    return cast(BybitClient, await BybitClient(**kwargs).async_init())


async def extended(
    **kwargs: Any,  # noqa: ANN401
) -> ExtendedClient:
    """Create and initialize an Extended client instance."""
    return cast(ExtendedClient, await ExtendedClient(**kwargs).async_init())


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


async def kraken(
    **kwargs: Any,  # noqa: ANN401
) -> KrakenClient:
    """Create and initialize a Kraken client instance."""
    return cast(KrakenClient, await KrakenClient(**kwargs).async_init())


async def lighter(
    **kwargs: Any,  # noqa: ANN401
) -> LighterClient:
    """Create and initialize a Lighter client instance."""
    return cast(LighterClient, await LighterClient(**kwargs).async_init())


async def mexc(
    **kwargs: Any,  # noqa: ANN401
) -> MEXCClient:
    """Create and initialize a MEXC client instance."""
    return cast(MEXCClient, await MEXCClient(**kwargs).async_init())


async def okx(
    **kwargs: Any,  # noqa: ANN401
) -> OKXClient:
    """Create and initialize an OKX client instance."""
    return cast(OKXClient, await OKXClient(**kwargs).async_init())


__all__ = [
    "aster",
    "backpack",
    "binance",
    "bingx",
    "bitget",
    "bybit",
    "extended",
    "hyperliquid",
    "kucoin",
    "kraken",
    "lighter",
    "mexc",
    "okx",
]
