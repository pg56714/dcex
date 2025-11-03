"""
BitMEX market data API endpoints module.

This module contains the Market enum with all market data related
endpoints for the BitMEX API.
"""

from enum import Enum


class Market(str, Enum):
    """
    BitMEX market data API endpoints.

    This enum contains all the market data related endpoints
    for the BitMEX API, including instrument information,
    orderbook, trades, tickers, klines, and funding rates.
    """

    INSTRUMENT_INFO = "/api/v1/instrument/active"
    ORDERBOOK = "/api/v1/orderBook/L2"
    TRADE = "/api/v1/trade"
    TICKER = "/api/v1/quote/bucketed"
    KLINE = "/api/v1/trade/bucketed"
    FUNDING = "/api/v1/funding"

    def __str__(self) -> str:
        return self.value
