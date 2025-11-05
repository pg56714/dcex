"""Market-related API endpoints for Hyperliquid exchange."""

from enum import Enum


class Market(str, Enum):
    """
    Market-related API endpoints for Hyperliquid exchange.

    This enum defines all market-related API endpoints including market metadata,
    order book, candlestick data, funding history, and other market functions.
    """

    META = "meta"
    SPOTMETA = "spotMeta"
    METAANDASSETCTXS = "metaAndAssetCtxs"
    SPOTMETAANDASSETCTXS = "spotMetaAndAssetCtxs"
    L2BOOK = "l2Book"
    CANDLESNAPSHOT = "candleSnapshot"
    FUNDINGHISTORY = "fundingHistory"

    def __str__(self) -> str:
        return self.value
