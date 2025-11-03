"""
BitMEX trading history API endpoints module.

This module contains the Trading enum with all trading history related
endpoints for the BitMEX API.
"""

from enum import Enum


class Trading(str, Enum):
    """
    BitMEX trading history API endpoints.

    This enum contains all the trading history related endpoints for the BitMEX API,
    including execution history, trade history, and trading volume information.
    """

    GET_EXECUTION_HISTORY = "/api/v1/user/executionHistory"
    GET_EXECUTIONS = "/api/v1/execution"
    GET_TRADE_HISTORY = "/api/v1/execution/tradeHistory"
    GET_TRADING_VOLUME = "/api/v1/user/tradingVolume"

    def __str__(self) -> str:
        return self.value
