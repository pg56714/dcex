"""
OKX Market API endpoints.

This module contains all the API endpoints related to market data
operations on the OKX exchange, including candlestick data, order books,
and ticker information.
"""

from enum import Enum


class Market(str, Enum):
    """
    Market-related API endpoints for OKX exchange.

    This enum contains all the market data endpoints including:
    - Candlestick/K-line data
    - Order book information
    - Ticker and price data
    """

    GET_KLINE = "/api/v5/market/candles"
    GET_ORDERBOOK = "/api/v5/market/books"
    GET_TICKERS = "/api/v5/market/tickers"
    GET_PUBLIC_TRADES = "/api/v5/market/trades"

    def __str__(self) -> str:
        return self.value
