"""BingX account HTTP client."""

from typing import Any

from dcex._keyword_aliases import legacy_keywords

from ._http_manager import HTTPManager
from ._transfers_http import AccountHTTPTransfersHTTP


class AccountHTTP(AccountHTTPTransfersHTTP, HTTPManager):
    """HTTP client for BingX account-related API endpoints backed by Rust."""

    @legacy_keywords({"recvWindow": "recv_window"})
    def get_account_balance(self, recv_window: int | None = None) -> dict[str, Any]:
        """Get account balance."""
        return self._native_private(
            "get_account_balance",
            self._native_params(recvWindow=recv_window),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    def get_swap_account_balance(self, recv_window: int | None = None) -> dict[str, Any]:
        """Get swap account balance."""
        return self._native_private(
            "get_swap_account_balance",
            self._native_params(recvWindow=recv_window),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    def get_swap_commission_rate(self, recv_window: int | None = None) -> dict[str, Any]:
        """Get current maker/taker fee rates for perpetuals."""
        return self._native_private(
            "get_swap_commission_rate", self._native_params(recvWindow=recv_window)
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    def get_spot_account_balance(
        self,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Get spot account balance."""
        return self._native_private(
            "get_spot_account_balance",
            self._native_params(recvWindow=recv_window),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    def get_fund_account_balance(
        self,
        asset: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Get fund account balance."""
        return self._native_private(
            "get_fund_account_balance",
            self._native_params(asset=asset, recvWindow=recv_window),
        )

    @legacy_keywords({"accountType": "account_type", "recvWindow": "recv_window"})
    def get_all_account_balance(
        self,
        account_type: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Get all account balance."""
        return self._native_private(
            "get_all_account_balance",
            self._native_params(accountType=account_type, recvWindow=recv_window),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    def get_account_uid(
        self,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Get account uid."""
        return self._native_private(
            "get_account_uid",
            self._native_params(recvWindow=recv_window),
        )

    @legacy_keywords({"apiKey": "api_key", "recvWindow": "recv_window"})
    def get_api_key_info(
        self,
        uid: int | str,
        api_key: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Get API key info."""
        return self._native_private(
            "get_api_key_info",
            self._native_params(uid=uid, apiKey=api_key, recvWindow=recv_window),
        )

    @legacy_keywords(
        {
            "subUid": "sub_uid",
            "subAccountString": "sub_account_string",
            "isFeeze": "is_feeze",
            "recvWindow": "recv_window",
        }
    )
    def get_subaccounts(
        self,
        page: int = 1,
        limit: int = 100,
        sub_uid: int | str | None = None,
        sub_account_string: str | None = None,
        is_feeze: bool | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve BingX sub-accounts owned by the master account."""
        return self._native_private(
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
    def get_subaccount_assets(
        self,
        sub_uid: int | str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve one BingX sub-account's funding assets."""
        return self._native_private(
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
    def get_subaccount_all_account_balance(
        self,
        page_index: int = 1,
        page_size: int = 10,
        sub_uid: int | str | None = None,
        account_type: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve paginated BingX sub-account asset overviews."""
        return self._native_private(
            "get_subaccount_all_account_balance",
            self._native_params(
                pageIndex=page_index,
                pageSize=page_size,
                subUid=sub_uid,
                accountType=account_type,
                recvWindow=recv_window,
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    def get_open_positions(
        self,
        product_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Get open positions."""
        return self._native_private(
            "get_open_positions",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    def get_fund_flow(
        self,
        product_symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Get fund flow."""
        return self._native_private(
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

    def get_listen_key(self) -> str:
        """Get listen key."""
        if not self.api_key:
            raise ValueError("API key is required")
        self._uses_native_transport()
        return self._native_private("get_listen_key", [])["listenKey"]

    def keep_alive_listen_key(self, listen_key: str) -> dict[str, Any]:
        """Keep alive listen key."""
        return self._native_private(
            "keep_alive_listen_key",
            self._native_params(listen_key=listen_key),
        )

    def close_listen_key(self, listen_key: str) -> dict[str, Any]:
        """Close listen key."""
        return self._native_private(
            "close_listen_key",
            self._native_params(listen_key=listen_key),
        )
