"""Lighter async private account HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """Async HTTP client for Lighter private account APIs."""

    async def create_auth_token(
        self,
        deadline: int | None = None,
        api_key_index: int | None = None,
    ) -> str:
        """Create a Lighter auth token using the configured API private key."""
        return self._auth_token(deadline=deadline, api_key_index=api_key_index)

    async def check_client(self) -> str | None:
        """Verify the configured API key against the Lighter signer client."""
        return await self._native_check_client()

    async def get_account_limits(
        self,
        account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve private Lighter account limits."""
        return await self._native_private("get_account_limits", self._native_params(**locals()))

    async def get_account_active_orders(
        self,
        account_index: int | None = None,
        market_id: int | None = None,
        market_type: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve private Lighter active orders."""
        return await self._native_private(
            "get_account_active_orders",
            self._native_params(**locals()),
        )

    async def get_account_inactive_orders(
        self,
        limit: int,
        account_index: int | None = None,
        market_id: int | None = None,
        ask_filter: int | None = None,
        between_timestamps: str | None = None,
        cursor: str | None = None,
        market_type: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve private Lighter inactive orders."""
        return await self._native_private(
            "get_account_inactive_orders",
            self._native_params(**locals()),
        )

    async def get_deposit_history(
        self,
        l1_address: str,
        account_index: int | None = None,
        cursor: str | None = None,
        filter: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter deposit history."""
        return await self._native_private("get_deposit_history", self._native_params(**locals()))

    async def get_export(
        self,
        type_: str,
        account_index: int | None = None,
        market_id: int | None = None,
        start_timestamp: int | None = None,
        end_timestamp: int | None = None,
        side: str | None = None,
        role: str | None = None,
        trade_type: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Export Lighter trade or funding records."""
        return await self._native_private("get_export", self._native_params(**locals()))

    async def get_fastwithdraw_info(
        self,
        account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter fast-withdraw information."""
        return await self._native_private("get_fastwithdraw_info", self._native_params(**locals()))

    async def get_l1_metadata(
        self,
        l1_address: str,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter L1 metadata."""
        return await self._native_private("get_l1_metadata", self._native_params(**locals()))

    async def get_liquidations(
        self,
        limit: int,
        account_index: int | None = None,
        market_id: int | None = None,
        cursor: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter account liquidations."""
        return await self._native_private("get_liquidations", self._native_params(**locals()))

    async def get_referral_points(
        self,
        account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter referral points."""
        return await self._native_private("get_referral_points", self._native_params(**locals()))

    async def get_referral_user_referrals(
        self,
        l1_address: str,
        cursor: str | None = None,
        stats_start_timestamp: int | None = None,
        stats_end_timestamp: int | None = None,
        limit: int | None = None,
        authorization: str | None = None,
        auth: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter user referral records."""
        return await self._native_private(
            "get_referral_user_referrals",
            self._native_params(**locals()),
        )

    async def get_transfer_history(
        self,
        account_index: int | None = None,
        cursor: str | None = None,
        type_: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter transfer history."""
        return await self._native_private("get_transfer_history", self._native_params(**locals()))

    async def get_transfer_fee_info(
        self,
        account_index: int | None = None,
        to_account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter transfer fee information."""
        return await self._native_private("get_transfer_fee_info", self._native_params(**locals()))

    async def get_withdraw_history(
        self,
        account_index: int | None = None,
        cursor: str | None = None,
        filter: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter withdrawal history."""
        return await self._native_private("get_withdraw_history", self._native_params(**locals()))

    async def get_position_funding(
        self,
        limit: int,
        account_index: int | None = None,
        market_id: int | None = None,
        cursor: str | None = None,
        side: str | None = None,
        start_timestamp: int | None = None,
        end_timestamp: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter position funding records."""
        return await self._native_private("get_position_funding", self._native_params(**locals()))

    async def get_leases(
        self,
        account_index: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        authorization: str | None = None,
        auth: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter account leases."""
        return await self._native_private("get_leases", self._native_params(**locals()))

    async def get_partner_stats(
        self,
        account_index: int | None = None,
        start_timestamp: int | None = None,
        end_timestamp: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter partner statistics."""
        return await self._native_private("get_partner_stats", self._native_params(**locals()))

    async def get_maker_only_api_keys(
        self,
        account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter maker-only API key settings."""
        return await self._native_private(
            "get_maker_only_api_keys",
            self._native_params(**locals()),
        )

    async def get_next_nonce(
        self,
        account_index: int | None = None,
        api_key_index: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve the next nonce for a Lighter API key."""
        return await self._native_private("get_next_nonce", self._native_params(**locals()))
