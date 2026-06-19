"""Account-related HTTP API client for Hyperliquid exchange backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for account-related operations on Hyperliquid exchange."""

    def clearinghouse_state(self, user: str, dex: str | None = None) -> dict[str, Any]:
        """Get clearinghouse state for a user."""
        return self._native_public(
            "clearinghouse_state",
            self._native_params(user=user, dex=dex),
        )

    def spot_clearinghouse_state(self, user: str) -> dict[str, Any]:
        """Get spot clearinghouse state for a user."""
        return self._native_public(
            "spot_clearinghouse_state",
            self._native_params(user=user),
        )

    def open_orders(self, user: str, dex: str | None = None) -> dict[str, Any]:
        """Get open orders for a user."""
        return self._native_public(
            "open_orders",
            self._native_params(user=user, dex=dex),
        )

    def user_fills(self, user: str, aggregateByTime: bool = False) -> dict[str, Any]:
        """Get user fills/trades."""
        return self._native_public(
            "user_fills",
            self._native_params(user=user, aggregateByTime=aggregateByTime),
        )

    def user_rate_limit(self, user: str) -> dict[str, Any]:
        """Get user rate limit information."""
        return self._native_public("user_rate_limit", self._native_params(user=user))

    def order_status(self, user: str, oid: int | str) -> dict[str, Any]:
        """Get status of a specific order."""
        return self._native_public(
            "order_status",
            self._native_params(user=user, oid=oid),
        )

    def historical_orders(self, user: str) -> dict[str, Any]:
        """Get historical orders for a user."""
        return self._native_public("historical_orders", self._native_params(user=user))

    def subaccounts(self, user: str) -> dict[str, Any]:
        """Get subaccounts for a user."""
        return self._native_public("subaccounts", self._native_params(user=user))

    def user_role(self, user: str) -> dict[str, Any]:
        """Get user role information."""
        return self._native_public("user_role", self._native_params(user=user))

    def portfolio(self, user: str) -> dict[str, Any]:
        """Get portfolio information for a user."""
        return self._native_public("portfolio", self._native_params(user=user))
