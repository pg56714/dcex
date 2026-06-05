"""KuCoin Spot Market API endpoints."""

from enum import Enum


class SpotMarket(str, Enum):
    """
    Enumeration of KuCoin Spot Market API endpoints.

    This class defines the available endpoints for spot market data operations
    on the KuCoin exchange, including instrument information, tickers,
    orderbook data, trade history, and candlestick data.
    """

    INSTRUMENT_INFO = "/api/v2/symbols"
    TICKER = "/api/v1/market/orderbook/level1"
    ALL_TICKERS = "/api/v1/market/allTickers"
    ORDERBOOK = "/api/v3/market/orderbook/level2"
    PUBLIC_TRADES = "/api/v1/market/histories"
    KLINE = "/api/v1/market/candles"

    def __str__(self) -> str:
        return self.value


class FuturesMarket(str, Enum):
    """Enumeration of KuCoin Futures Market API endpoints."""

    CONTRACTS = "/api/v1/contracts/active"
    CONTRACT = "/api/v1/contracts/{symbol}"
    TICKER = "/api/v1/ticker"
    ORDERBOOK = "/api/v1/level2/snapshot"
    PART_ORDERBOOK = "/api/v1/level2/depth{size}"
    PUBLIC_TRADES = "/api/v1/trade/history"
    KLINE = "/api/v1/kline/query"
    OPEN_INTEREST = "/api/ua/v1/market/open-interest"

    def __str__(self) -> str:
        return self.value
