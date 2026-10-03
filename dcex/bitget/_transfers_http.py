"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AccountHTTP."""


class TradeHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from TradeHTTP."""

    def get_uta_max_transferable(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v3/account/max-transferable``."""
        return self._native_private("get_uta_max_transferable", self._native_params(coin=coin))

    def get_uta_transferable_coins(self, from_type: str, to_type: str) -> dict[str, Any]:
        """Call ``GET /api/v3/account/transferable-coins``."""
        return self._native_private(
            "get_uta_transferable_coins", self._native_params(fromType=from_type, toType=to_type)
        )

    def get_uta_position_transfer_history(
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
        return self._native_private(
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

    def transfer_uta_account(
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
        return self._native_private(
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

    def transfer_uta_sub_to_master(
        self, from_type: str, to_type: str, amount: str, coin: str, *, client_oid: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/sub-master-transfer``."""
        return self._native_private(
            "transfer_uta_sub_to_master",
            self._native_params(
                fromType=from_type, toType=to_type, amount=amount, coin=coin, clientOid=client_oid
            ),
        )

    def transfer_uta_sub_account(
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
        return self._native_private(
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

    def get_uta_sub_account_transfer_records(
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
        return self._native_private(
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
