"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AccountHTTP."""

    def get_transferable_amount(
        self,
        coins: str | list[str],
    ) -> dict[str, Any]:
        """
        Get transferable amount for specified coins.

        Args:
            coins: A single coin name (e.g. ``"USDT"``) or a list of up to 20 coins.
        """
        if isinstance(coins, str):
            coins = [coins] if coins else []
        if not coins:
            raise ValueError("coins must contain at least one coin.")
        if len(coins) > 20:
            raise ValueError("coins must contain no more than 20 coins.")
        return self._native_private(
            "get_transferable_amount",
            self._native_params(coins=",".join(coins)),
        )


class AssetHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AssetHTTP."""

    def get_internal_transfer_records(
        self,
        transferId: str | None = None,
        coin: str | None = None,
        status: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get internal transfer records."""
        return self._native_private(
            "get_internal_transfer_records",
            self._native_params(
                transferId=transferId,
                coin=coin,
                status=status,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_transferable_coin(
        self,
        fromAccountType: str,
        toAccountType: str,
    ) -> dict[str, Any]:
        """Get transferable coins between account types."""
        return self._native_private(
            "get_transferable_coin",
            self._native_params(fromAccountType=fromAccountType, toAccountType=toAccountType),
        )

    def create_internal_transfer(
        self,
        coin: str,
        amount: str,
        fromAccountType: str,
        toAccountType: str,
        transferId: str | None = None,
    ) -> dict[str, Any]:
        """Create internal transfer between account types."""
        return self._native_private(
            "create_internal_transfer",
            self._native_params(
                coin=coin,
                amount=amount,
                fromAccountType=fromAccountType,
                toAccountType=toAccountType,
                transferId=transferId,
            ),
        )

    def create_universal_transfer(
        self,
        coin: str,
        amount: str,
        fromMemberId: str,
        toMemberId: str,
        fromAccountType: str,
        toAccountType: str,
        transferId: str | None = None,
    ) -> dict[str, Any]:
        """Transfer assets among Bybit master and sub-account UIDs."""
        return self._native_private(
            "create_universal_transfer",
            self._native_params(
                coin=coin,
                amount=amount,
                fromMemberId=fromMemberId,
                toMemberId=toMemberId,
                fromAccountType=fromAccountType,
                toAccountType=toAccountType,
                transferId=transferId,
            ),
        )

    def get_universal_transfer_records(
        self,
        transferId: str | None = None,
        coin: str | None = None,
        status: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        fromMemberId: str | None = None,
        toMemberId: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get universal transfer records."""
        return self._native_private(
            "get_universal_transfer_records",
            self._native_params(
                transferId=transferId,
                coin=coin,
                status=status,
                startTime=startTime,
                endTime=endTime,
                fromMemberId=fromMemberId,
                toMemberId=toMemberId,
                limit=limit,
                cursor=cursor,
            ),
        )
