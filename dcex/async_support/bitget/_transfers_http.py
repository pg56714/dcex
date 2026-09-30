"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AccountHTTP."""

    async def transfer(
        self,
        coin: str,
        amount: str,
        from_type: str,
        to_type: str,
        symbol: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Transfer assets between Bitget account types."""
        return await self._native_private(
            "transfer",
            self._native_params(
                coin=coin,
                amount=amount,
                fromType=from_type,
                toType=to_type,
                symbol=symbol,
                clientOid=client_oid,
            ),
        )

    async def get_transfer_records(
        self,
        coin: str,
        from_type: str | None = None,
        start_time: int | str | None = None,
        end_time: int | str | None = None,
        client_oid: str | None = None,
        page_num: int | str | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget account transfer records."""
        return await self._native_private(
            "get_transfer_records",
            self._native_params(
                coin=coin,
                fromType=from_type,
                startTime=start_time,
                endTime=end_time,
                clientOid=client_oid,
                pageNum=page_num,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_transferable_coins(
        self,
        from_type: str,
        to_type: str,
    ) -> dict[str, Any]:
        """Retrieve coins transferable between Bitget account types."""
        return await self._native_private(
            "get_transferable_coins",
            self._native_params(fromType=from_type, toType=to_type),
        )


class TradeHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from TradeHTTP."""

    async def get_futures_union_transfer_limits(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/transfer-limits``."""
        return await self._native_private(
            "get_futures_union_transfer_limits", self._native_params(coin=coin)
        )

    async def get_spot_sub_account_transfer_records(
        self,
        *,
        coin: str | None = None,
        role: str | None = None,
        sub_uid: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        client_oid: str | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/account/sub-main-trans-record``."""
        return await self._native_private(
            "get_spot_sub_account_transfer_records",
            self._native_params(
                coin=coin,
                role=role,
                subUid=sub_uid,
                startTime=start_time,
                endTime=end_time,
                clientOid=client_oid,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def transfer_spot_sub_account(
        self,
        from_type: str,
        to_type: str,
        amount: str,
        coin: str,
        from_user_id: str,
        to_user_id: str,
        *,
        product_symbol: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/wallet/subaccount-transfer``."""
        return await self._native_private(
            "transfer_spot_sub_account",
            self._native_params(
                fromType=from_type,
                toType=to_type,
                amount=amount,
                coin=coin,
                fromUserId=from_user_id,
                toUserId=to_user_id,
                product_symbol=product_symbol,
                clientOid=client_oid,
            ),
        )

    async def get_cross_margin_max_transferable(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/account/max-transfer-out-amount``."""
        return await self._native_private(
            "get_cross_margin_max_transferable", self._native_params(coin=coin)
        )

    async def get_isolated_margin_max_transferable(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/account/max-transfer-out-amount``."""
        return await self._native_private(
            "get_isolated_margin_max_transferable",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_uta_max_transferable(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v3/account/max-transferable``."""
        return await self._native_private(
            "get_uta_max_transferable", self._native_params(coin=coin)
        )

    async def get_uta_transferable_coins(self, from_type: str, to_type: str) -> dict[str, Any]:
        """Call ``GET /api/v3/account/transferable-coins``."""
        return await self._native_private(
            "get_uta_transferable_coins", self._native_params(fromType=from_type, toType=to_type)
        )

    async def get_uta_position_transfer_history(
        self,
        category: str,
        *,
        product_symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/move-position-history``."""
        return await self._native_private(
            "get_uta_position_transfer_history",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                startTime=start_time,
                endTime=end_time,
                cursor=cursor,
                limit=limit,
            ),
        )

    async def transfer_uta_account(
        self,
        from_type: str,
        to_type: str,
        amount: str,
        coin: str,
        *,
        product_symbol: str | None = None,
        allow_borrow: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/transfer``."""
        return await self._native_private(
            "transfer_uta_account",
            self._native_params(
                fromType=from_type,
                toType=to_type,
                amount=amount,
                coin=coin,
                product_symbol=product_symbol,
                allowBorrow=allow_borrow,
                clientOid=client_oid,
            ),
        )

    async def transfer_uta_sub_to_master(
        self, from_type: str, to_type: str, amount: str, coin: str, *, client_oid: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/sub-master-transfer``."""
        return await self._native_private(
            "transfer_uta_sub_to_master",
            self._native_params(
                fromType=from_type, toType=to_type, amount=amount, coin=coin, clientOid=client_oid
            ),
        )

    async def transfer_uta_sub_account(
        self,
        from_type: str,
        to_type: str,
        amount: str,
        coin: str,
        from_user_id: str,
        to_user_id: str,
        client_oid: str,
        *,
        allow_borrow: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/sub-transfer``."""
        return await self._native_private(
            "transfer_uta_sub_account",
            self._native_params(
                fromType=from_type,
                toType=to_type,
                amount=amount,
                coin=coin,
                fromUserId=from_user_id,
                toUserId=to_user_id,
                clientOid=client_oid,
                allowBorrow=allow_borrow,
            ),
        )

    async def get_uta_sub_account_transfer_records(
        self,
        *,
        sub_uid: str | None = None,
        role: str | None = None,
        coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        client_oid: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/sub-transfer-record``."""
        return await self._native_private(
            "get_uta_sub_account_transfer_records",
            self._native_params(
                subUid=sub_uid,
                role=role,
                coin=coin,
                startTime=start_time,
                endTime=end_time,
                clientOid=client_oid,
                limit=limit,
                cursor=cursor,
            ),
        )
