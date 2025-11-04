"""Zoomex market API endpoints."""

from enum import Enum


class Market(str, Enum):
    """Market-related API endpoints for Zoomex."""

    GET_INSTRUMENTS_INFO = "/cloud/trade/v3/market/instruments-info"

    def __str__(self) -> str:
        return self.value
