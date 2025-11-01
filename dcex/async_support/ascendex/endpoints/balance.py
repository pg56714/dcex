"""Ascendex balance API endpoints."""

from enum import Enum


class Balance(str, Enum):
    """Ascendex balance API endpoints."""

    CASH_ACCOUNT_BALANCE = "/{ACCOUNT_GROUP}/api/pro/v1/cash/balance"

    @property
    def hash(self) -> str:
        """Get the hash identifier for the endpoint."""
        return self.value.split("/")[-1]

    def __str__(self) -> str:
        return self.value
