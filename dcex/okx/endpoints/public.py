"""
OKX Public API endpoints.

This module contains all the API endpoints related to public market data
operations on the OKX exchange, including instrument information and
funding rate data.
"""

from enum import Enum


class Public(str, Enum):
    """
    Public market-related API endpoints for OKX exchange.

    This enum contains all the public market data endpoints including:
    - Instrument information and specifications
    - Funding rate data and history
    - Public market statistics
    """

    GET_INSTRUMENT_INFO = "/api/v5/public/instruments"
    GET_FUNDING_RATE = "/api/v5/public/funding-rate"
    GET_FUNDING_RATE_HISTORY = "/api/v5/public/funding-rate-history"
    GET_OPEN_INTEREST = "/api/v5/public/open-interest"
    GET_POSITION_TIERS = "/api/v5/public/position-tiers"
    GET_TRADING_DATA_SUPPORT_COIN = "/api/v5/rubik/stat/trading-data/support-coin"
    GET_TAKER_VOLUME = "/api/v5/rubik/stat/taker-volume"
    GET_CONTRACT_TAKER_VOLUME = "/api/v5/rubik/stat/taker-volume-contract"
    GET_LONG_SHORT_RATIO = "/api/v5/rubik/stat/contracts/long-short-account-ratio"
    GET_CONTRACT_LONG_SHORT_RATIO = "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract"
    GET_TOP_TRADER_LONG_SHORT_ACCOUNT_RATIO = (
        "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader"
    )
    GET_TOP_TRADER_LONG_SHORT_POSITION_RATIO = (
        "/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader"
    )
    GET_CONTRACTS_OPEN_INTEREST_VOLUME = "/api/v5/rubik/stat/contracts/open-interest-volume"
    GET_CONTRACT_OPEN_INTEREST_HISTORY = "/api/v5/rubik/stat/contracts/open-interest-history"

    def __str__(self) -> str:
        return self.value
