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
