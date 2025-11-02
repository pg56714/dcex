"""
Bybit Position API endpoints.

This module contains all the API endpoints related to position management
operations on the Bybit exchange, including position queries, leverage
settings, and PnL history.
"""

from enum import Enum


class Position(str, Enum):
    """
    Position-related API endpoints for Bybit exchange.

    This enum contains all the position management endpoints including:
    - Position list queries
    - Leverage settings
    - Position mode switching
    - Closed PnL history
    """

    GET_POSITIONS = "/v5/position/list"
    SET_LEVERAGE = "/v5/position/set-leverage"
    SWITCH_POSITION_MODE = "/v5/position/switch-mode"
    GET_CLOSED_PNL = "/v5/position/closed-pnl"

    def __str__(self) -> str:
        return self.value
