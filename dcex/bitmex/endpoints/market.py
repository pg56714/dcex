"""
BitMEX Market Data API endpoints.

This module contains the API endpoint definitions for market data operations
on the BitMEX exchange, including instrument information, orderbook, trades,
tickers, klines, and funding data.
"""

from enum import Enum


class Market(str, Enum):
    """
    BitMEX Market Data API endpoints.

    This enum contains all the API endpoint paths for market data operations
    such as retrieving instrument information, orderbook data, trade history,
    ticker information, candlestick data, and funding rates.
    """

    INSTRUMENT_INFO = "/api/v1/instrument/active"
    ORDERBOOK = "/api/v1/orderBook/L2"
    TRADE = "/api/v1/trade"
    TICKER = "/api/v1/quote/bucketed"
    KLINE = "/api/v1/trade/bucketed"
    FUNDING = "/api/v1/funding"

    def __str__(self) -> str:
        return self.value
