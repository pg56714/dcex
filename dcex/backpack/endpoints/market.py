"""Backpack public market API endpoints."""

from enum import Enum


class Public(str, Enum):
    """Backpack public REST endpoints."""

    ASSETS = "/api/v1/assets"
    COLLATERAL = "/api/v1/collateral"
    BORROW_LEND_MARKETS = "/api/v1/borrowLend/markets"
    BORROW_LEND_MARKET_HISTORY = "/api/v1/borrowLend/markets/history"
    BORROW_LEND_APY = "/api/v1/borrowLend/apy"
    MARKETS = "/api/v1/markets"
    MARKET = "/api/v1/market"
    DEPTH = "/api/v1/depth"
    MARKET_SESSIONS = "/api/v1/market-sessions"
    SECURITIES = "/api/v1/securities"
    MARK_PRICES = "/api/v1/markPrices"
    OPEN_INTEREST = "/api/v1/openInterest"
    FUNDING_RATES = "/api/v1/fundingRates"
    KLINES = "/api/v1/klines"
    TICKER = "/api/v1/ticker"
    TICKERS = "/api/v1/tickers"
    STATUS = "/api/v1/status"
    PING = "/api/v1/ping"
    TIME = "/api/v1/time"
    WALLETS = "/api/v1/wallets"
    TRADES = "/api/v1/trades"
    HISTORICAL_TRADES = "/api/v1/trades/history"

    def __str__(self) -> str:
        return self.value
