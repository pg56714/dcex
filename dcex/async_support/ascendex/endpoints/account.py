"""Ascendex cash account API endpoints."""

from enum import Enum


class CashAccount(str, Enum):
    """Ascendex cash account API endpoints."""

    ACCOUNT_INFO = "/api/pro/v1/info"

    @property
    def hash(self) -> str:
        """Get the hash identifier for the endpoint."""
        return self.value.split("/")[-1]

    def __str__(self) -> str:
        return self.value
