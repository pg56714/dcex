"""Bitget public market API endpoints."""

from enum import Enum


class SpotMarket(str, Enum):
    """Enumeration of Bitget spot public market endpoints."""

    COINS = "/api/v2/spot/public/coins"
    SYMBOLS = "/api/v2/spot/public/symbols"
    TICKERS = "/api/v2/spot/market/tickers"
    ORDERBOOK = "/api/v2/spot/market/orderbook"
    CANDLES = "/api/v2/spot/market/candles"
    HISTORY_CANDLES = "/api/v2/spot/market/history-candles"
    RECENT_TRADES = "/api/v2/spot/market/fills"
    MARKET_TRADES = "/api/v2/spot/market/fills-history"

    def __str__(self) -> str:
        return self.value


class FuturesMarket(str, Enum):
    """Enumeration of Bitget futures public market endpoints."""

    CONTRACTS = "/api/v2/mix/market/contracts"
    TICKER = "/api/v2/mix/market/ticker"
    TICKERS = "/api/v2/mix/market/tickers"
    ORDERBOOK = "/api/v2/mix/market/merge-depth"
    CANDLES = "/api/v2/mix/market/candles"
    HISTORY_CANDLES = "/api/v2/mix/market/history-candles"
    RECENT_TRADES = "/api/v2/mix/market/fills"
    CURRENT_FUNDING_RATE = "/api/v2/mix/market/current-fund-rate"
    HISTORY_FUNDING_RATE = "/api/v2/mix/market/history-fund-rate"
    OPEN_INTEREST = "/api/v2/mix/market/open-interest"

    def __str__(self) -> str:
        return self.value
