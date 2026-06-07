"""MEXC public market API endpoints."""

from enum import Enum


class SpotMarket(str, Enum):
    """MEXC Spot V3 public market endpoints."""

    PING = "/api/v3/ping"
    SERVER_TIME = "/api/v3/time"
    DEFAULT_SYMBOLS = "/api/v3/defaultSymbols"
    EXCHANGE_INFO = "/api/v3/exchangeInfo"
    ORDERBOOK = "/api/v3/depth"
    RECENT_TRADES = "/api/v3/trades"
    AGG_TRADES = "/api/v3/aggTrades"
    KLINES = "/api/v3/klines"
    AVG_PRICE = "/api/v3/avgPrice"
    TICKER_24HR = "/api/v3/ticker/24hr"
    TICKER_PRICE = "/api/v3/ticker/price"
    BOOK_TICKER = "/api/v3/ticker/bookTicker"

    def __str__(self) -> str:
        return self.value


class ContractMarket(str, Enum):
    """MEXC Contract V1 public market endpoints."""

    PING = "/api/v1/contract/ping"
    DETAIL = "/api/v1/contract/detail"
    TICKER = "/api/v1/contract/ticker"
    DEPTH = "/api/v1/contract/depth/{symbol}"
    DEPTH_COMMITS = "/api/v1/contract/depth_commits/{symbol}/{limit}"
    INDEX_PRICE = "/api/v1/contract/index_price/{symbol}"
    FAIR_PRICE = "/api/v1/contract/fair_price/{symbol}"
    FUNDING_RATE = "/api/v1/contract/funding_rate/{symbol}"
    KLINE = "/api/v1/contract/kline/{symbol}"
    INDEX_PRICE_KLINE = "/api/v1/contract/kline/index_price/{symbol}"
    FAIR_PRICE_KLINE = "/api/v1/contract/kline/fair_price/{symbol}"
    DEALS = "/api/v1/contract/deals/{symbol}"
    RISK_REVERSE = "/api/v1/contract/risk_reverse"
    RISK_REVERSE_HISTORY = "/api/v1/contract/risk_reverse/history"
    FUNDING_RATE_HISTORY = "/api/v1/contract/funding_rate/history"

    def __str__(self) -> str:
        return self.value
