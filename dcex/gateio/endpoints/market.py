"""
Gate.io Market API endpoints.

This module contains all the API endpoints related to market data
operations on the Gate.io exchange, including spot, futures, and delivery
market information.
"""

from enum import Enum


class FutureMarket(str, Enum):
    """
    Futures market-related API endpoints for Gate.io exchange.

    This enum contains all the futures market data endpoints including:
    - Contract information
    - Order book data
    - K-line/candlestick data
    - Ticker information
    - Funding rate history
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
    Delivery market-related API endpoints for Gate.io exchange.

    This enum contains all the delivery market data endpoints including:
    - Contract information
    - Order book data
    - K-line/candlestick data
    - Ticker information
    """

    GET_ALL_CONTRACTS = "/delivery/{settle}/contracts"
    ORDER_BOOK = "/delivery/{settle}/order_book"
    GET_KLINE = "/delivery/{settle}/candlesticks"
    LIST_TICKERS = "/delivery/{settle}/tickers"

    def __str__(self) -> str:
        return self.value


class SpotMarket(str, Enum):
    """
    Spot market-related API endpoints for Gate.io exchange.

    This enum contains all the spot market data endpoints including:
    - Currency pair information
    - Order book data
    - K-line/candlestick data
    - Ticker information
    """

    GET_ALL_CURRENCY_PAIRS = "/spot/currency_pairs"
    ORDER_BOOK = "/spot/order_book"
    GET_KLINE = "/spot/candlesticks"
    LIST_TICKERS = "/spot/tickers"

    def __str__(self) -> str:
        return self.value
