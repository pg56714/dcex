"""
Bybit Market API endpoints.

This module contains all the API endpoints related to market data
operations on the Bybit exchange, including instrument information,
price data, orderbook, and trading history.
"""

from enum import Enum


class Market(str, Enum):
    """
    Bybit market data API endpoints.

    This enum contains all the market data related endpoints for the Bybit API,
    including instruments information, klines, orderbook, tickers,
    funding rate history, public trade history, and risk market data.
    """

    GET_INSTRUMENTS_INFO = "/v5/market/instruments-info"
    GET_KLINE = "/v5/market/kline"
    GET_ORDERBOOK = "/v5/market/orderbook"
    GET_TICKERS = "/v5/market/tickers"
    GET_FUNDING_RATE_HISTORY = "/v5/market/funding/history"
    GET_PUBLIC_TRADE_HISTORY = "/v5/market/recent-trade"
    GET_RISK_MARKET = "/v5/market/risk-limit"

    def __str__(self) -> str:
        return self.value
