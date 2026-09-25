"""Account-related HTTP API client for Hyperliquid exchange backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for account-related operations on Hyperliquid exchange."""

    async def clearinghouse_state(self, user: str, dex: str | None = None) -> dict[str, Any]:
        """Get clearinghouse state for a user."""
        return await self._native_public(
            "clearinghouse_state",
            self._native_params(user=user, dex=dex),
        )

    async def spot_clearinghouse_state(self, user: str) -> dict[str, Any]:
        """Get spot clearinghouse state for a user."""
        return await self._native_public(
            "spot_clearinghouse_state",
            self._native_params(user=user),
        )

    async def open_orders(self, user: str, dex: str | None = None) -> dict[str, Any]:
        """Get open orders for a user."""
        return await self._native_public(
            "open_orders",
            self._native_params(user=user, dex=dex),
        )

    async def user_fills(self, user: str, aggregateByTime: bool = False) -> dict[str, Any]:
        """Get user fills/trades."""
        return await self._native_public(
            "user_fills",
            self._native_params(user=user, aggregateByTime=aggregateByTime),
        )

    async def user_fills_by_time(
        self,
        user: str,
        start_time: int,
        end_time: int | None = None,
        aggregate_by_time: bool | None = None,
    ) -> dict[str, Any]:
        """Retrieve paginated fills from a millisecond timestamp."""
        return await self._native_public(
            "user_fills_by_time",
            self._native_params(
                user=user,
                startTime=start_time,
                endTime=end_time,
                aggregateByTime=aggregate_by_time,
            ),
        )

    async def user_funding(
        self, user: str, start_time: int, end_time: int | None = None
    ) -> dict[str, Any]:
        """Retrieve user funding payments within a time range."""
        return await self._native_public(
            "user_funding",
            self._native_params(user=user, startTime=start_time, endTime=end_time),
        )

    async def user_non_funding_ledger_updates(
        self, user: str, start_time: int, end_time: int | None = None
    ) -> dict[str, Any]:
        """Retrieve non-funding account ledger entries."""
        return await self._native_public(
            "user_non_funding_ledger_updates",
            self._native_params(user=user, startTime=start_time, endTime=end_time),
        )

    async def user_rate_limit(self, user: str) -> dict[str, Any]:
        """Get user rate limit information."""
        return await self._native_public("user_rate_limit", self._native_params(user=user))

    async def order_status(self, user: str, oid: int | str) -> dict[str, Any]:
        """Get status of a specific order."""
        return await self._native_public(
            "order_status",
            self._native_params(user=user, oid=oid),
        )

    async def historical_orders(self, user: str) -> dict[str, Any]:
        """Get historical orders for a user."""
        return await self._native_public("historical_orders", self._native_params(user=user))

    async def subaccounts(self, user: str) -> dict[str, Any]:
        """Get subaccounts for a user."""
        return await self._native_public("subaccounts", self._native_params(user=user))

    async def user_role(self, user: str) -> dict[str, Any]:
        """Get user role information."""
        return await self._native_public("user_role", self._native_params(user=user))

    async def portfolio(self, user: str) -> dict[str, Any]:
        """Get portfolio information for a user."""
        return await self._native_public("portfolio", self._native_params(user=user))
