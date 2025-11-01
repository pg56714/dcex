"""Binance market data API endpoints for spot and futures trading."""

from enum import Enum


class SpotMarket(str, Enum):
    """Enumeration of Binance spot trading market data API endpoints."""

    EXCHANGE_INFO = "/api/v3/exchangeInfo"
    ORDERBOOK = "/api/v3/depth"
    TRADES = "/api/v3/trades"
    KLINES = "/api/v3/klines"

    def __str__(self) -> str:
        return self.value


class FuturesMarket(str, Enum):
    """Enumeration of Binance futures trading market data API endpoints."""

    EXCHANGE_INFO = "/fapi/v1/exchangeInfo"
    BOOK_TICKER = "/fapi/v1/ticker/bookTicker"
    KLINES = "/fapi/v1/klines"
    PREMIUM_INDEX = "/fapi/v1/premiumIndex"
    FUNDING_RATE_HISTORY = "/fapi/v1/fundingRate"

    def __str__(self) -> str:
        return self.value
