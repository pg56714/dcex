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
    GET_OPEN_INTEREST = "/v5/market/open-interest"
    GET_HISTORICAL_VOLATILITY = "/v5/market/historical-volatility"
    GET_INSURANCE_POOL = "/v5/market/insurance"
    GET_RISK_MARKET = "/v5/market/risk-limit"
    GET_DELIVERY_PRICE = "/v5/market/delivery-price"
    GET_LONG_SHORT_RATIO = "/v5/market/account-ratio"
    GET_ORDER_PRICE_LIMIT = "/v5/market/price-limit"
    GET_ADL_ALERT = "/v5/market/adlAlert"

    def __str__(self) -> str:
        return self.value
