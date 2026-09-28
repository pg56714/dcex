"""Fund movement and batch endpoint mixins."""

from typing import Any

from .._keyword_aliases import legacy_keywords
from ._http_manager import HTTPManager


class AccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AccountHTTP."""

    @legacy_keywords(
        {"fromAccount": "from_account", "toAccount": "to_account", "recvWindow": "recv_window"}
    )
    def get_transferable_coins(
        self,
        from_account: str,
        to_account: str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Get transferable coins."""
        return self._native_private(
            "get_transferable_coins",
            self._native_params(
                fromAccount=from_account,
                toAccount=to_account,
                recvWindow=recv_window,
            ),
        )

    @legacy_keywords(
        {"fromAccount": "from_account", "toAccount": "to_account", "recvWindow": "recv_window"}
    )
    def asset_transfer(
        self,
        from_account: str,
        to_account: str,
        asset: str,
        amount: str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Asset transfer."""
        return self._native_private(
            "asset_transfer",
            self._native_params(
                fromAccount=from_account,
                toAccount=to_account,
                asset=asset,
                amount=amount,
                recvWindow=recv_window,
            ),
        )

    @legacy_keywords(
        {
            "fromAccount": "from_account",
            "toAccount": "to_account",
            "transferId": "transfer_id",
            "tranId": "tran_id",
            "startTime": "start_time",
            "endTime": "end_time",
            "pageIndex": "page_index",
            "pageSize": "page_size",
            "recvWindow": "recv_window",
        }
    )
    def get_asset_transfer_records(
        self,
        from_account: str | None = None,
        to_account: str | None = None,
        transfer_id: int | str | None = None,
        tran_id: int | str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Get asset transfer records."""
        return self._native_private(
            "get_asset_transfer_records",
            self._native_params(
                fromAccount=from_account,
                toAccount=to_account,
                transferId=transfer_id,
                tranId=tran_id,
                startTime=start_time,
                endTime=end_time,
                pageIndex=page_index,
                pageSize=page_size,
                recvWindow=recv_window,
            ),
        )

    @legacy_keywords(
        {
            "tranId": "tran_id",
            "startTime": "start_time",
            "endTime": "end_time",
            "pageId": "page_id",
            "pagingSize": "paging_size",
            "recvWindow": "recv_window",
        }
    )
    def get_subaccount_transfer_history(
        self,
        uid: int | str,
        type_: str | None = None,
        tran_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_id: int | None = None,
        paging_size: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve BingX master/sub-account asset-transfer history."""
        return self._native_private(
            "get_subaccount_transfer_history",
            self._native_params(
                uid=uid,
                type=type_,
                tranId=tran_id,
                startTime=start_time,
                endTime=end_time,
                pageId=page_id,
                pagingSize=paging_size,
                recvWindow=recv_window,
            ),
        )

    @legacy_keywords(
        {
            "fromUid": "from_uid",
            "fromAccountType": "from_account_type",
            "toUid": "to_uid",
            "toAccountType": "to_account_type",
            "recvWindow": "recv_window",
        }
    )
    def get_subaccount_transferable_amounts(
        self,
        from_uid: int | str,
        from_account_type: int,
        to_uid: int | str,
        to_account_type: int,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve transferable assets between BingX master/sub-accounts."""
        return self._native_private(
            "get_subaccount_transferable_amounts",
            self._native_params(
                fromUid=from_uid,
                fromAccountType=from_account_type,
                toUid=to_uid,
                toAccountType=to_account_type,
                recvWindow=recv_window,
            ),
        )

    @legacy_keywords(
        {
            "assetName": "asset_name",
            "transferAmount": "transfer_amount",
            "fromUid": "from_uid",
            "fromType": "from_type",
            "fromAccountType": "from_account_type",
            "toUid": "to_uid",
            "toType": "to_type",
            "toAccountType": "to_account_type",
            "recvWindow": "recv_window",
        }
    )
    def transfer_subaccount_assets(
        self,
        asset_name: str,
        transfer_amount: str,
        from_uid: int | str,
        from_type: int,
        from_account_type: int,
        to_uid: int | str,
        to_type: int,
        to_account_type: int,
        remark: str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Transfer assets among BingX master and sub-accounts."""
        return self._native_private(
            "transfer_subaccount_assets",
            self._native_params(
                assetName=asset_name,
                transferAmount=transfer_amount,
                fromUid=from_uid,
                fromType=from_type,
                fromAccountType=from_account_type,
                toUid=to_uid,
                toType=to_type,
                toAccountType=to_account_type,
                remark=remark,
                recvWindow=recv_window,
            ),
        )


class TradeHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from TradeHTTP."""

    def set_sub_account_transfer_authorization(
        self, *, sub_uids: str, transferable: bool, recv_window: int | None = None
    ) -> dict[str, Any]:
        """Set sub account transfer authorization.

        POST /openApi/account/v1/innerTransfer/authorizeSubAccount. Timestamps use milliseconds.
        """
        return self._native_private(
            "set_sub_account_transfer_authorization",
            self._native_params(
                subUids=sub_uids, transferable=transferable, recvWindow=recv_window
            ),
        )

    def get_internal_transfer_records(
        self,
        *,
        coin: str,
        id: str | None = None,
        transfer_client_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Get internal transfer records.

        GET /openApi/wallets/v1/capital/innerTransfer/records. Timestamps use milliseconds."""
        return self._native_private(
            "get_internal_transfer_records",
            self._native_params(
                coin=coin,
                id=id,
                transferClientId=transfer_client_id,
                startTime=start_time,
                endTime=end_time,
                offset=offset,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def get_sub_account_internal_transfer_records(
        self,
        *,
        coin: str,
        transfer_client_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Get sub account internal transfer records.

        GET /openApi/wallets/v1/capital/subAccount/innerTransfer/records. Timestamps use
        milliseconds.
        """
        return self._native_private(
            "get_sub_account_internal_transfer_records",
            self._native_params(
                coin=coin,
                transferClientId=transfer_client_id,
                startTime=start_time,
                endTime=end_time,
                offset=offset,
                limit=limit,
                recvWindow=recv_window,
            ),
        )
