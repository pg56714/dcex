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

    def __str__(self) -> str:
        return self.value
