"""
BitMEX Trading History API endpoints.

This module contains the API endpoint definitions for trading history operations
on the BitMEX exchange, including execution history, trade history, and
trading volume information.
"""

from enum import Enum


class Trading(str, Enum):
    """
    BitMEX Trading History API endpoints.

    This enum contains all the API endpoint paths for trading history operations
    such as retrieving execution history, trade history, and trading volume
    information for analysis and reporting purposes.
    """

    GET_EXECUTION_HISTORY = "/api/v1/user/executionHistory"
    GET_EXECUTIONS = "/api/v1/execution"
    GET_TRADE_HISTORY = "/api/v1/execution/tradeHistory"
    GET_TRADING_VOLUME = "/api/v1/user/tradingVolume"

    def __str__(self) -> str:
        return self.value
