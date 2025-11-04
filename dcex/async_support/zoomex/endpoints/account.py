"""Zoomex account API endpoints."""

from enum import Enum


class Account(str, Enum):
    """Account-related API endpoints for Zoomex."""

    GET_WALLET_BALANCE = "/cloud/trade/v3/account/wallet-balance"

    def __str__(self) -> str:
        return self.value
