"""Lighter async private account HTTP client."""

from typing import Any

from ._http_manager import HTTPManager
from .endpoints.market import Public


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
        return self._private_signer().check_client()

    async def get_account_limits(
        self,
        account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve private Lighter account limits."""
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.ACCOUNT_LIMITS,
            {"account_index": account_index},
            headers={"Authorization": self._auth_token(authorization)},
        )

    async def get_account_active_orders(
        self,
        account_index: int | None = None,
        market_id: int | None = None,
        market_type: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve private Lighter active orders."""
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.ACCOUNT_ACTIVE_ORDERS,
            {
                "account_index": account_index,
                "market_id": market_id,
                "market_type": market_type,
            },
            headers={"Authorization": self._auth_token(authorization)},
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
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.ACCOUNT_INACTIVE_ORDERS,
            {
                "account_index": account_index,
                "market_id": market_id,
                "ask_filter": ask_filter,
                "between_timestamps": between_timestamps,
                "cursor": cursor,
                "limit": limit,
                "market_type": market_type,
            },
            headers={"Authorization": self._auth_token(authorization)},
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
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.DEPOSIT_HISTORY,
            {
                "account_index": account_index,
                "l1_address": l1_address,
                "cursor": cursor,
                "filter": filter,
            },
            headers={"Authorization": self._auth_token(authorization)},
        )

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
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.EXPORT,
            {
                "account_index": account_index,
                "type": type_,
                "market_id": market_id,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "side": side,
                "role": role,
                "trade_type": trade_type,
            },
            headers={"Authorization": self._auth_token(authorization)},
        )

    async def get_fastwithdraw_info(
        self,
        account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter fast-withdraw information."""
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.FASTWITHDRAW_INFO,
            {"account_index": account_index},
            headers={"Authorization": self._auth_token(authorization)},
        )

    async def get_l1_metadata(
        self,
        l1_address: str,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter L1 metadata."""
        return await self._request(
            "GET",
            Public.L1_METADATA,
            {"l1_address": l1_address},
            headers={"Authorization": self._auth_token(authorization)},
        )

    async def get_liquidations(
        self,
        limit: int,
        account_index: int | None = None,
        market_id: int | None = None,
        cursor: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter account liquidations."""
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.LIQUIDATIONS,
            {
                "account_index": account_index,
                "market_id": market_id,
                "cursor": cursor,
                "limit": limit,
            },
            headers={"Authorization": self._auth_token(authorization)},
        )

    async def get_referral_points(
        self,
        account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter referral points."""
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.REFERRAL_POINTS,
            {"account_index": account_index},
            headers={"Authorization": self._auth_token(authorization)},
        )

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
        if authorization is None and auth is None and self.api_private_key is not None:
            authorization = self._auth_token()
        return await self._request(
            "GET",
            Public.REFERRAL_USER_REFERRALS,
            {
                "l1_address": l1_address,
                "cursor": cursor,
                "auth": auth,
                "stats_start_timestamp": stats_start_timestamp,
                "stats_end_timestamp": stats_end_timestamp,
                "limit": limit,
            },
            headers={"Authorization": authorization} if authorization is not None else None,
        )

    async def get_transfer_history(
        self,
        account_index: int | None = None,
        cursor: str | None = None,
        type_: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter transfer history."""
        account_index = self._private_account_index(account_index)
        headers = (
            {"Authorization": self._auth_token(authorization)}
            if authorization is not None or self.api_private_key is not None
            else None
        )
        return await self._request(
            "GET",
            Public.TRANSFER_HISTORY,
            {"account_index": account_index, "cursor": cursor, "type": type_},
            headers=headers,
        )

    async def get_transfer_fee_info(
        self,
        account_index: int | None = None,
        to_account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter transfer fee information."""
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.TRANSFER_FEE_INFO,
            {"account_index": account_index, "to_account_index": to_account_index},
            headers={"Authorization": self._auth_token(authorization)},
        )

    async def get_withdraw_history(
        self,
        account_index: int | None = None,
        cursor: str | None = None,
        filter: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter withdrawal history."""
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.WITHDRAW_HISTORY,
            {"account_index": account_index, "cursor": cursor, "filter": filter},
            headers={"Authorization": self._auth_token(authorization)},
        )

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
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.POSITION_FUNDING,
            {
                "account_index": account_index,
                "market_id": market_id,
                "cursor": cursor,
                "limit": limit,
                "side": side,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
            },
            headers={"Authorization": self._auth_token(authorization)},
        )

    async def get_leases(
        self,
        account_index: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        authorization: str | None = None,
        auth: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter account leases."""
        account_index = self._private_account_index(account_index)
        if authorization is None and auth is None and self.api_private_key is not None:
            authorization = self._auth_token()
        return await self._request(
            "GET",
            Public.LEASES,
            {
                "account_index": account_index,
                "cursor": cursor,
                "limit": limit,
                "auth": auth,
            },
            headers={"Authorization": authorization} if authorization is not None else None,
        )

    async def get_partner_stats(
        self,
        account_index: int | None = None,
        start_timestamp: int | None = None,
        end_timestamp: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter partner statistics."""
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.PARTNER_STATS,
            {
                "account_index": account_index,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
            },
        )

    async def get_maker_only_api_keys(
        self,
        account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter maker-only API key settings."""
        account_index = self._private_account_index(account_index)
        return await self._request(
            "GET",
            Public.GET_MAKER_ONLY_API_KEYS,
            {"account_index": account_index},
            headers={"Authorization": self._auth_token(authorization)},
        )

    async def get_next_nonce(
        self,
        account_index: int | None = None,
        api_key_index: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve the next nonce for a Lighter API key."""
        return await self._request(
            "GET",
            Public.NEXT_NONCE,
            {
                "account_index": self._private_account_index(account_index),
                "api_key_index": self._private_api_key_index(api_key_index),
            },
        )
