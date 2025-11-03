"""
BitMEX Position Management API endpoints.

This module contains the API endpoint definitions for position management operations
on the BitMEX exchange, including getting positions, switching modes, setting
leverage, and managing margin.
"""

from enum import Enum


class Positions(str, Enum):
    """
    BitMEX Position Management API endpoints.

    This enum contains all the API endpoint paths for position management operations
    such as retrieving current positions, switching position modes, setting leverage,
    managing margin modes, and retrieving margin information.
    """

    GET_POSITIONS = "/api/v1/position"
    SWITCH_MODE = "/api/v1/position/isolate"
    LEVERAGE = "/api/v1/position/leverage"
    MARGINING_MODE = "/api/v1/user/marginingMode"
    GET_MARGIN = "/api/v1/user/margin"

    def __str__(self) -> str:
        return self.value
