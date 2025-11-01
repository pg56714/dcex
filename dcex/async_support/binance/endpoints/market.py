"""Binance market data endpoints for spot and futures trading."""

from enum import Enum


class SpotMarket(str, Enum):
    """Spot trading market data endpoints."""

    EXCHANGE_INFO = "/api/v3/exchangeInfo"
    ORDERBOOK = "/api/v3/depth"
    TRADES = "/api/v3/trades"
    KLINES = "/api/v3/klines"
    PRICE = "/api/v3/ticker/price"

    def __str__(self) -> str:
        return self.value


class FuturesMarket(str, Enum):
    """Futures trading market data endpoints."""

    EXCHANGE_INFO = "/fapi/v1/exchangeInfo"
    BOOK_TICKER = "/fapi/v1/ticker/bookTicker"
    KLINES = "/fapi/v1/klines"
    PREMIUM_INDEX = "/fapi/v1/premiumIndex"
    FUNDING_RATE_HISTORY = "/fapi/v1/fundingRate"

    def __str__(self) -> str:
        return self.value
