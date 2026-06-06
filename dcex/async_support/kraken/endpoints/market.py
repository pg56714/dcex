"""Kraken public market-data API endpoints."""

from enum import Enum


class SpotMarket(str, Enum):
    """Enumeration of Kraken spot public market endpoints."""

    SERVER_TIME = "/0/public/Time"
    ASSET_PAIRS = "/0/public/AssetPairs"
    TICKER = "/0/public/Ticker"
    ORDERBOOK = "/0/public/Depth"
    PUBLIC_TRADES = "/0/public/Trades"
    OHLC = "/0/public/OHLC"

    def __str__(self) -> str:
        return self.value


class FuturesMarket(str, Enum):
    """Enumeration of Kraken Futures public market endpoints."""

    INSTRUMENTS = "/derivatives/api/v3/instruments"
    TICKERS = "/derivatives/api/v3/tickers"
    ORDERBOOK = "/derivatives/api/v3/orderbook"
    PUBLIC_TRADES = "/derivatives/api/v3/history"
    CANDLES = "/api/charts/v1/{tick_type}/{symbol}/{resolution}"

    def __str__(self) -> str:
        return self.value
