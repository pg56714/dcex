"""BingX account HTTP client."""

from typing import Any

from dcex._keyword_aliases import legacy_keywords

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """Async HTTP client for BingX account-related API endpoints backed by Rust."""

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_account_balance(self, recv_window: int | None = None) -> dict[str, Any]:
        return await self._native_private(
            "get_account_balance",
            self._native_params(recvWindow=recv_window),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_swap_account_balance(self, recv_window: int | None = None) -> dict[str, Any]:
        return await self._native_private(
            "get_swap_account_balance",
            self._native_params(recvWindow=recv_window),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_swap_commission_rate(self, recv_window: int | None = None) -> dict[str, Any]:
        """Get current maker/taker fee rates for perpetuals."""
        return await self._native_private(
            "get_swap_commission_rate", self._native_params(recvWindow=recv_window)
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_spot_account_balance(
        self,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_spot_account_balance",
            self._native_params(recvWindow=recv_window),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_fund_account_balance(
        self,
        asset: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_fund_account_balance",
            self._native_params(asset=asset, recvWindow=recv_window),
        )

    @legacy_keywords({"accountType": "account_type", "recvWindow": "recv_window"})
    async def get_all_account_balance(
        self,
        account_type: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_all_account_balance",
            self._native_params(accountType=account_type, recvWindow=recv_window),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_account_uid(
        self,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_account_uid",
            self._native_params(recvWindow=recv_window),
        )

    @legacy_keywords({"apiKey": "api_key", "recvWindow": "recv_window"})
    async def get_api_key_info(
        self,
        uid: int | str,
        api_key: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_api_key_info",
            self._native_params(uid=uid, apiKey=api_key, recvWindow=recv_window),
        )

    @legacy_keywords(
        {"fromAccount": "from_account", "toAccount": "to_account", "recvWindow": "recv_window"}
    )
    async def get_transferable_coins(
        self,
        from_account: str,
        to_account: str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
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
    async def asset_transfer(
        self,
        from_account: str,
        to_account: str,
        asset: str,
        amount: str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
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
    async def get_asset_transfer_records(
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
        return await self._native_private(
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
            "subUid": "sub_uid",
            "subAccountString": "sub_account_string",
            "isFeeze": "is_feeze",
            "recvWindow": "recv_window",
        }
    )
    async def get_subaccounts(
        self,
        page: int = 1,
        limit: int = 100,
        sub_uid: int | str | None = None,
        sub_account_string: str | None = None,
        is_feeze: bool | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve BingX sub-accounts owned by the master account."""
        return await self._native_private(
            "get_subaccounts",
            self._native_params(
                page=page,
                limit=limit,
                subUid=sub_uid,
                subAccountString=sub_account_string,
                isFeeze=is_feeze,
                recvWindow=recv_window,
            ),
        )

    @legacy_keywords({"subUid": "sub_uid", "recvWindow": "recv_window"})
    async def get_subaccount_assets(
        self,
        sub_uid: int | str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve one BingX sub-account's funding assets."""
        return await self._native_private(
            "get_subaccount_assets",
            self._native_params(subUid=sub_uid, recvWindow=recv_window),
        )

    @legacy_keywords(
        {
            "pageIndex": "page_index",
            "pageSize": "page_size",
            "subUid": "sub_uid",
            "accountType": "account_type",
            "recvWindow": "recv_window",
        }
    )
    async def get_subaccount_all_account_balance(
        self,
        page_index: int = 1,
        page_size: int = 10,
        sub_uid: int | str | None = None,
        account_type: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve paginated BingX sub-account asset overviews."""
        return await self._native_private(
            "get_subaccount_all_account_balance",
            self._native_params(
                pageIndex=page_index,
                pageSize=page_size,
                subUid=sub_uid,
                accountType=account_type,
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
    async def get_subaccount_transfer_history(
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
        return await self._native_private(
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
    async def get_subaccount_transferable_amounts(
        self,
        from_uid: int | str,
        from_account_type: int,
        to_uid: int | str,
        to_account_type: int,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve transferable assets between BingX master/sub-accounts."""
        return await self._native_private(
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
    async def transfer_subaccount_assets(
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
        return await self._native_private(
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

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_open_positions(
        self,
        product_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_open_positions",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_fund_flow(
        self,
        product_symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_fund_flow",
            self._native_params(
                product_symbol=product_symbol,
                income_type=income_type,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_listen_key(self) -> str:
        if not self.api_key:
            raise ValueError("API key is required")
        self._uses_native_transport()
        return (await self._native_private("get_listen_key", []))["listenKey"]

    async def keep_alive_listen_key(self, listen_key: str) -> dict[str, Any]:
        return await self._native_private(
            "keep_alive_listen_key",
            self._native_params(listen_key=listen_key),
        )

    async def close_listen_key(self, listen_key: str) -> dict[str, Any]:
        return await self._native_private(
            "close_listen_key",
            self._native_params(listen_key=listen_key),
        )
