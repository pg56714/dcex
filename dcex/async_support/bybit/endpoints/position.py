"""
Bybit position management API endpoints module.

This module contains the Position enum with all position-related
endpoints for the Bybit API.
"""

from enum import Enum


class Position(str, Enum):
    """
    Bybit position management API endpoints.

    This enum contains all the position-related endpoints for the Bybit API,
    including position queries, leverage settings, position mode switching,
    and closed PnL information.
    """

    GET_POSITIONS = "/v5/position/list"
    SET_LEVERAGE = "/v5/position/set-leverage"
    SWITCH_POSITION_MODE = "/v5/position/switch-mode"
    GET_CLOSED_PNL = "/v5/position/closed-pnl"

    def __str__(self) -> str:
        return self.value
