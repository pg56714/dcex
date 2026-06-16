"""Async Bybit asset HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AssetHTTP(HTTPManager):
    """Async HTTP client for Bybit asset operations."""

    async def get_coin_info(self, coin: str | None = None) -> dict[str, Any]:
        """Get coin information."""
        return await self._native_private("get_coin_info", self._native_params(coin=coin))

    async def get_sub_uid(self) -> dict[str, Any]:
        """Get sub-account UID list."""
        return await self._native_private("get_sub_uid", [])

    async def get_spot_asset_info(self, coin: str | None = None) -> dict[str, Any]:
        """Get spot asset information."""
        return await self._native_private("get_spot_asset_info", self._native_params(coin=coin))

    async def get_coins_balance(
        self,
        accountType: str,
        coin: str | None = None,
        memberId: str | None = None,
    ) -> dict[str, Any]:
        """Get coins balance for account."""
        return await self._native_private(
            "get_coins_balance",
            self._native_params(accountType=accountType, coin=coin, memberId=memberId),
        )

    async def get_coin_balance(
        self,
        accountType: str,
        coin: str,
        memberId: str | None = None,
        toAccountType: str | None = None,
    ) -> dict[str, Any]:
        """Get single coin balance."""
        return await self._native_private(
            "get_coin_balance",
            self._native_params(
                accountType=accountType,
                coin=coin,
                memberId=memberId,
                toAccountType=toAccountType,
            ),
        )

    async def get_withdrawable_amount(self, coin: str) -> dict[str, Any]:
        """Get withdrawable amount for a coin."""
        return await self._native_private(
            "get_withdrawable_amount",
            self._native_params(coin=coin),
        )

    async def get_internal_transfer_records(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get internal transfer records."""
        return await self._native_private(
            "get_internal_transfer_records",
            self._native_params(coin=coin, startTime=startTime, limit=limit),
        )

    async def get_transferable_coin(
        self,
        fromAccountType: str,
        toAccountType: str,
    ) -> dict[str, Any]:
        """Get transferable coins between account types."""
        return await self._native_private(
            "get_transferable_coin",
            self._native_params(fromAccountType=fromAccountType, toAccountType=toAccountType),
        )

    async def create_internal_transfer(
        self,
        coin: str,
        amount: str,
        fromAccountType: str,
        toAccountType: str,
    ) -> dict[str, Any]:
        """Create internal transfer between account types."""
        return await self._native_private(
            "create_internal_transfer",
            self._native_params(
                coin=coin,
                amount=amount,
                fromAccountType=fromAccountType,
                toAccountType=toAccountType,
            ),
        )

    async def get_universal_transfer_records(
        self,
        coin: str | None = None,
        status: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get universal transfer records."""
        return await self._native_private(
            "get_universal_transfer_records",
            self._native_params(coin=coin, status=status, startTime=startTime, limit=limit),
        )

    async def set_deposit_account(self, accountType: str) -> dict[str, Any]:
        """Set deposit account type."""
        return await self._native_private(
            "set_deposit_account",
            self._native_params(accountType=accountType),
        )

    async def get_deposit_records(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get deposit records."""
        return await self._native_private(
            "get_deposit_records",
            self._native_params(coin=coin, startTime=startTime, limit=limit),
        )

    async def get_sub_deposit_records(
        self,
        subMemberId: str,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get sub-account deposit records."""
        return await self._native_private(
            "get_sub_deposit_records",
            self._native_params(
                subMemberId=subMemberId,
                coin=coin,
                startTime=startTime,
                limit=limit,
            ),
        )

    async def get_internal_deposit_records(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get internal deposit records."""
        return await self._native_private(
            "get_internal_deposit_records",
            self._native_params(coin=coin, startTime=startTime, limit=limit),
        )

    async def get_master_deposit_address(self, coin: str) -> dict[str, Any]:
        """Get master deposit address for a coin."""
        return await self._native_private(
            "get_master_deposit_address",
            self._native_params(coin=coin),
        )
