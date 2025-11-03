"""
BitMEX position management API endpoints module.

This module contains the Positions enum with all position-related
endpoints for the BitMEX API.
"""

from enum import Enum


class Positions(str, Enum):
    """
    BitMEX position management API endpoints.

    This enum contains all the position-related endpoints for the BitMEX API,
    including position queries, margin mode switching, leverage settings,
    and margin information retrieval.
    """

    GET_POSITIONS = "/api/v1/position"
    SWITCH_MODE = "/api/v1/position/isolate"
    LEVERAGE = "/api/v1/position/leverage"
    MARGINING_MODE = "/api/v1/user/marginingMode"
    GET_MARGIN = "/api/v1/user/margin"

    def __str__(self) -> str:
        return self.value
