"""BingX account HTTP client."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for BingX account-related API endpoints backed by Rust."""

    def get_account_balance(self, recvWindow: int | None = None) -> dict[str, Any]:
        return self._native_private(
            "get_account_balance",
            self._native_params(recvWindow=recvWindow),
        )

    def get_swap_account_balance(self, recvWindow: int | None = None) -> dict[str, Any]:
        return self._native_private(
            "get_swap_account_balance",
            self._native_params(recvWindow=recvWindow),
        )

    def get_swap_commission_rate(self, recvWindow: int | None = None) -> dict[str, Any]:
        """Get current maker/taker fee rates for perpetuals."""
        return self._native_private(
            "get_swap_commission_rate", self._native_params(recvWindow=recvWindow)
        )

    def get_spot_account_balance(
        self,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_spot_account_balance",
            self._native_params(recvWindow=recvWindow),
        )

    def get_fund_account_balance(
        self,
        asset: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_fund_account_balance",
            self._native_params(asset=asset, recvWindow=recvWindow),
        )

    def get_all_account_balance(
        self,
        accountType: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_all_account_balance",
            self._native_params(accountType=accountType, recvWindow=recvWindow),
        )

    def get_account_uid(
        self,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_account_uid",
            self._native_params(recvWindow=recvWindow),
        )

    def get_api_key_info(
        self,
        uid: int | str,
        apiKey: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_api_key_info",
            self._native_params(uid=uid, apiKey=apiKey, recvWindow=recvWindow),
        )

    def get_transferable_coins(
        self,
        fromAccount: str,
        toAccount: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_transferable_coins",
            self._native_params(
                fromAccount=fromAccount,
                toAccount=toAccount,
                recvWindow=recvWindow,
            ),
        )

    def asset_transfer(
        self,
        fromAccount: str,
        toAccount: str,
        asset: str,
        amount: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "asset_transfer",
            self._native_params(
                fromAccount=fromAccount,
                toAccount=toAccount,
                asset=asset,
                amount=amount,
                recvWindow=recvWindow,
            ),
        )

    def get_asset_transfer_records(
        self,
        fromAccount: str | None = None,
        toAccount: str | None = None,
        transferId: int | str | None = None,
        tranId: int | str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        pageIndex: int | None = None,
        pageSize: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_asset_transfer_records",
            self._native_params(
                fromAccount=fromAccount,
                toAccount=toAccount,
                transferId=transferId,
                tranId=tranId,
                startTime=startTime,
                endTime=endTime,
                pageIndex=pageIndex,
                pageSize=pageSize,
                recvWindow=recvWindow,
            ),
        )

    def get_subaccounts(
        self,
        page: int = 1,
        limit: int = 100,
        subUid: int | str | None = None,
        subAccountString: str | None = None,
        isFeeze: bool | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve BingX sub-accounts owned by the master account."""
        return self._native_private(
            "get_subaccounts",
            self._native_params(
                page=page,
                limit=limit,
                subUid=subUid,
                subAccountString=subAccountString,
                isFeeze=isFeeze,
                recvWindow=recvWindow,
            ),
        )

    def get_subaccount_assets(
        self,
        subUid: int | str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve one BingX sub-account's funding assets."""
        return self._native_private(
            "get_subaccount_assets",
            self._native_params(subUid=subUid, recvWindow=recvWindow),
        )

    def get_subaccount_all_account_balance(
        self,
        pageIndex: int = 1,
        pageSize: int = 10,
        subUid: int | str | None = None,
        accountType: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve paginated BingX sub-account asset overviews."""
        return self._native_private(
            "get_subaccount_all_account_balance",
            self._native_params(
                pageIndex=pageIndex,
                pageSize=pageSize,
                subUid=subUid,
                accountType=accountType,
                recvWindow=recvWindow,
            ),
        )

    def get_subaccount_transfer_history(
        self,
        uid: int | str,
        type_: str | None = None,
        tranId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        pageId: int | None = None,
        pagingSize: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve BingX master/sub-account asset-transfer history."""
        return self._native_private(
            "get_subaccount_transfer_history",
            self._native_params(
                uid=uid,
                type=type_,
                tranId=tranId,
                startTime=startTime,
                endTime=endTime,
                pageId=pageId,
                pagingSize=pagingSize,
                recvWindow=recvWindow,
            ),
        )

    def get_subaccount_transferable_amounts(
        self,
        fromUid: int | str,
        fromAccountType: int,
        toUid: int | str,
        toAccountType: int,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve transferable assets between BingX master/sub-accounts."""
        return self._native_private(
            "get_subaccount_transferable_amounts",
            self._native_params(
                fromUid=fromUid,
                fromAccountType=fromAccountType,
                toUid=toUid,
                toAccountType=toAccountType,
                recvWindow=recvWindow,
            ),
        )

    def transfer_subaccount_assets(
        self,
        assetName: str,
        transferAmount: str,
        fromUid: int | str,
        fromType: int,
        fromAccountType: int,
        toUid: int | str,
        toType: int,
        toAccountType: int,
        remark: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Transfer assets among BingX master and sub-accounts."""
        return self._native_private(
            "transfer_subaccount_assets",
            self._native_params(
                assetName=assetName,
                transferAmount=transferAmount,
                fromUid=fromUid,
                fromType=fromType,
                fromAccountType=fromAccountType,
                toUid=toUid,
                toType=toType,
                toAccountType=toAccountType,
                remark=remark,
                recvWindow=recvWindow,
            ),
        )

    def get_open_positions(
        self,
        product_symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_open_positions",
            self._native_params(product_symbol=product_symbol, recvWindow=recvWindow),
        )

    def get_fund_flow(
        self,
        product_symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_fund_flow",
            self._native_params(
                product_symbol=product_symbol,
                income_type=income_type,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    def get_listen_key(self) -> str:
        if not self.api_key:
            raise ValueError("API key is required")
        self._uses_native_transport()
        return self._native_private("get_listen_key", [])["listenKey"]

    def keep_alive_listen_key(self, listen_key: str) -> dict[str, Any]:
        return self._native_private(
            "keep_alive_listen_key",
            self._native_params(listen_key=listen_key),
        )

    def close_listen_key(self, listen_key: str) -> dict[str, Any]:
        return self._native_private(
            "close_listen_key",
            self._native_params(listen_key=listen_key),
        )
