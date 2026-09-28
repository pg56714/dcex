"""Bybit asset HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager
from ._transfers_http import AssetHTTPTransfersHTTP
from ._withdrawals_http import AssetHTTPWithdrawalsHTTP


class AssetHTTP(AssetHTTPWithdrawalsHTTP, AssetHTTPTransfersHTTP, HTTPManager):
    """HTTP client for Bybit asset operations."""

    def get_coin_info(self, coin: str | None = None) -> dict[str, Any]:
        """Get coin information."""
        return self._native_private("get_coin_info", self._native_params(coin=coin))

    def get_sub_uid(self) -> dict[str, Any]:
        """Get sub-account UID list."""
        return self._native_private("get_sub_uid", [])

    def get_spot_asset_info(self, coin: str | None = None) -> dict[str, Any]:
        """
        Get spot asset information (classic accounts only; deprecated).

        Bybit lists ``GET /v5/asset/transfer/query-asset-info`` under "Abandoned
        Endpoints" and it applies only to classic accounts. For unified accounts use
        ``get_coins_balance`` or ``get_wallet_balance`` instead.
        """
        return self._native_private("get_spot_asset_info", self._native_params(coin=coin))

    def get_coins_balance(
        self,
        accountType: str,
        coin: str | None = None,
        memberId: str | None = None,
        withBonus: bool | None = None,
    ) -> dict[str, Any]:
        """Get coins balance for account."""
        return self._native_private(
            "get_coins_balance",
            self._native_params(
                accountType=accountType,
                coin=coin,
                memberId=memberId,
                withBonus=withBonus,
            ),
        )

    def get_coin_balance(
        self,
        accountType: str,
        coin: str,
        memberId: str | None = None,
        toMemberId: str | None = None,
        toAccountType: str | None = None,
        withBonus: bool | None = None,
        withTransferSafeAmount: bool | None = None,
        withLtvTransferSafeAmount: bool | None = None,
    ) -> dict[str, Any]:
        """Get single coin balance."""
        return self._native_private(
            "get_coin_balance",
            self._native_params(
                accountType=accountType,
                coin=coin,
                memberId=memberId,
                toMemberId=toMemberId,
                toAccountType=toAccountType,
                withBonus=withBonus,
                withTransferSafeAmount=withTransferSafeAmount,
                withLtvTransferSafeAmount=withLtvTransferSafeAmount,
            ),
        )

    def set_deposit_account(self, accountType: str) -> dict[str, Any]:
        """Set deposit account type."""
        return self._native_private(
            "set_deposit_account",
            self._native_params(accountType=accountType),
        )

    def get_deposit_records(
        self,
        id: str | None = None,
        txID: str | None = None,
        coin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get deposit records."""
        return self._native_private(
            "get_deposit_records",
            self._native_params(
                id=id,
                txID=txID,
                coin=coin,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_sub_deposit_records(
        self,
        subMemberId: str,
        id: str | None = None,
        txID: str | None = None,
        coin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get sub-account deposit records."""
        return self._native_private(
            "get_sub_deposit_records",
            self._native_params(
                subMemberId=subMemberId,
                id=id,
                txID=txID,
                coin=coin,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_internal_deposit_records(
        self,
        txID: str | None = None,
        coin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get internal deposit records."""
        return self._native_private(
            "get_internal_deposit_records",
            self._native_params(
                txID=txID,
                coin=coin,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_master_deposit_address(self, coin: str, chainType: str | None = None) -> dict[str, Any]:
        """Get master deposit address for a coin."""
        return self._native_private(
            "get_master_deposit_address",
            self._native_params(coin=coin, chainType=chainType),
        )
