"""
dcex - dex & cex trading library.

A comprehensive library for cryptocurrency exchange interactions with both sync and async support.
Automatically handles Jupyter Notebook compatibility with nest_asyncio.
"""

from typing import Any

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
from .utils.jupyter_helper import auto_apply_nest_asyncio

auto_apply_nest_asyncio(verbose=False)


# Create callable functions for each exchange (synchronous clients)
def aster(**kwargs: Any) -> AsterClient:  # noqa: ANN401
    """Create an Aster client instance."""
    return AsterClient(**kwargs)


def backpack(**kwargs: Any) -> BackpackClient:  # noqa: ANN401
    """Create a Backpack client instance."""
    return BackpackClient(**kwargs)


def binance(**kwargs: Any) -> BinanceClient:  # noqa: ANN401
    """Create a Binance client instance."""
    return BinanceClient(**kwargs)


def bingx(**kwargs: Any) -> BingXClient:  # noqa: ANN401
    """Create a BingX client instance."""
    return BingXClient(**kwargs)


def bitget(**kwargs: Any) -> BitgetClient:  # noqa: ANN401
    """Create a Bitget client instance."""
    return BitgetClient(**kwargs)


def bybit(**kwargs: Any) -> BybitClient:  # noqa: ANN401
    """Create a Bybit client instance."""
    return BybitClient(**kwargs)


def extended(**kwargs: Any) -> ExtendedClient:  # noqa: ANN401
    """Create an Extended client instance."""
    return ExtendedClient(**kwargs)


def hyperliquid(**kwargs: Any) -> HyperliquidClient:  # noqa: ANN401
    """Create a Hyperliquid client instance."""
    return HyperliquidClient(**kwargs)


def kucoin(**kwargs: Any) -> KuCoinClient:  # noqa: ANN401
    """Create a KuCoin client instance."""
    return KuCoinClient(**kwargs)


def kraken(**kwargs: Any) -> KrakenClient:  # noqa: ANN401
    """Create a Kraken client instance."""
    return KrakenClient(**kwargs)


def lighter(**kwargs: Any) -> LighterClient:  # noqa: ANN401
    """Create a Lighter client instance."""
    return LighterClient(**kwargs)


def mexc(**kwargs: Any) -> MEXCClient:  # noqa: ANN401
    """Create a MEXC client instance."""
    return MEXCClient(**kwargs)


def okx(**kwargs: Any) -> OKXClient:  # noqa: ANN401
    """Create an OKX client instance."""
    return OKXClient(**kwargs)


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
