"""Binance market data endpoints for spot and futures trading."""

from enum import Enum


class SpotMarket(str, Enum):
    """Spot trading market data endpoints."""

    SERVER_TIME = "/api/v3/time"
    EXCHANGE_INFO = "/api/v3/exchangeInfo"
    ORDERBOOK = "/api/v3/depth"
    TRADES = "/api/v3/trades"
    KLINES = "/api/v3/klines"
    PRICE = "/api/v3/ticker/price"

    def __str__(self) -> str:
        return self.value


class FuturesMarket(str, Enum):
    """Futures trading market data endpoints."""

    SERVER_TIME = "/fapi/v1/time"
    EXCHANGE_INFO = "/fapi/v1/exchangeInfo"
    BOOK_TICKER = "/fapi/v1/ticker/bookTicker"
    KLINES = "/fapi/v1/klines"
    PREMIUM_INDEX = "/fapi/v1/premiumIndex"
    FUNDING_RATE_HISTORY = "/fapi/v1/fundingRate"
    OPEN_INTEREST = "/fapi/v1/openInterest"
    OPEN_INTEREST_HISTORY = "/futures/data/openInterestHist"
    GLOBAL_LONG_SHORT_ACCOUNT_RATIO = "/futures/data/globalLongShortAccountRatio"
    TOP_LONG_SHORT_ACCOUNT_RATIO = "/futures/data/topLongShortAccountRatio"
    TOP_LONG_SHORT_POSITION_RATIO = "/futures/data/topLongShortPositionRatio"
    TAKER_LONG_SHORT_RATIO = "/futures/data/takerlongshortRatio"
    BASIS = "/futures/data/basis"

    def __str__(self) -> str:
        return self.value
