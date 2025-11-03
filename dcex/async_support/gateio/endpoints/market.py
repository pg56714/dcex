"""
Gate.io market data API endpoints module.

This module contains the market data endpoint enums for different
trading types (Future, Delivery, Spot) in the Gate.io API.
"""

from enum import Enum


class FutureMarket(str, Enum):
    """
    Gate.io futures market data API endpoints.

    This enum contains all futures market data endpoints for the Gate.io API,
    including contracts, order books, klines, tickers, and funding rates.
    """

    GET_ALL_CONTRACTS = "/futures/{settle}/contracts"
    GET_A_SINGLE_CONTRACT = "/futures/{settle}/contracts/{contract}"
    ORDER_BOOK = "/futures/{settle}/order_book"
    GET_KLINE = "/futures/{settle}/candlesticks"
    LIST_TICKERS = "/futures/{settle}/tickers"
    FUNDING_RATE_HISTORY = "/futures/{settle}/funding_rate"

    def __str__(self) -> str:
        return self.value


class DeliveryMarket(str, Enum):
    """
    Gate.io delivery market data API endpoints.

    This enum contains all delivery market data endpoints for the Gate.io API,
    including contracts, order books, klines, and tickers.
    """

    GET_ALL_CONTRACTS = "/delivery/{settle}/contracts"
    ORDER_BOOK = "/delivery/{settle}/order_book"
    GET_KLINE = "/delivery/{settle}/candlesticks"
    LIST_TICKERS = "/delivery/{settle}/tickers"

    def __str__(self) -> str:
        return self.value


class SpotMarket(str, Enum):
    """
    Gate.io spot market data API endpoints.

    This enum contains all spot market data endpoints for the Gate.io API,
    including currency pairs, order books, klines, and tickers.
    """

    GET_ALL_CURRENCY_PAIRS = "/spot/currency_pairs"
    ORDER_BOOK = "/spot/order_book"
    GET_KLINE = "/spot/candlesticks"
    LIST_TICKERS = "/spot/tickers"

    def __str__(self) -> str:
        return self.value
