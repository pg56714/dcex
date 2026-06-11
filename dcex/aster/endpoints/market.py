"""Aster V3 public market API endpoints."""

from enum import Enum


class SpotMarket(str, Enum):
    """Aster spot public REST endpoints."""

    PING = "/api/v3/ping"
    SERVER_TIME = "/api/v3/time"
    EXCHANGE_INFO = "/api/v3/exchangeInfo"
    DEPTH = "/api/v3/depth"
    TRADES = "/api/v3/trades"
    HISTORICAL_TRADES = "/api/v3/historicalTrades"
    AGG_TRADES = "/api/v3/aggTrades"
    KLINES = "/api/v3/klines"
    TICKER_24HR = "/api/v3/ticker/24hr"
    TICKER_PRICE = "/api/v3/ticker/price"
    BOOK_TICKER = "/api/v3/ticker/bookTicker"
    COMMISSION_RATE = "/api/v3/commissionRate"
    WITHDRAW_FEE = "/api/v3/aster/withdraw/estimateFee"

    def __str__(self) -> str:
        return self.value


class FuturesMarket(str, Enum):
    """Aster futures public REST endpoints."""

    PING = "/fapi/v3/ping"
    SERVER_TIME = "/fapi/v3/time"
    EXCHANGE_INFO = "/fapi/v3/exchangeInfo"
    DEPTH = "/fapi/v3/depth"
    TRADES = "/fapi/v3/trades"
    HISTORICAL_TRADES = "/fapi/v3/historicalTrades"
    AGG_TRADES = "/fapi/v3/aggTrades"
    KLINES = "/fapi/v3/klines"
    INDEX_PRICE_KLINES = "/fapi/v3/indexPriceKlines"
    MARK_PRICE_KLINES = "/fapi/v3/markPriceKlines"
    PREMIUM_INDEX = "/fapi/v3/premiumIndex"
    FUNDING_RATE = "/fapi/v3/fundingRate"
    FUNDING_INFO = "/fapi/v3/fundingInfo"
    TICKER_24HR = "/fapi/v3/ticker/24hr"
    TICKER_PRICE = "/fapi/v3/ticker/price"
    BOOK_TICKER = "/fapi/v3/ticker/bookTicker"
    INDEX_REFERENCES = "/fapi/v3/indexreferences"

    def __str__(self) -> str:
        return self.value
