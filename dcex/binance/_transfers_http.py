"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AccountHTTP."""

    _native_private: Any

    _params: Any

    _subaccount_query: Any

    def create_universal_transfer(
        self,
        type_: str,
        asset: str,
        amount: str,
        fromSymbol: str | None = None,
        toSymbol: str | None = None,
    ) -> dict:
        """Transfer an asset between Binance account wallets."""
        return self._native_private(
            "create_universal_transfer",
            self._params(
                type=type_,
                asset=asset,
                amount=amount,
                fromSymbol=fromSymbol,
                toSymbol=toSymbol,
            ),
        )

    def get_universal_transfer_history(
        self,
        type_: str,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        size: int | None = None,
        fromSymbol: str | None = None,
        toSymbol: str | None = None,
    ) -> dict:
        """Get Binance universal transfer records."""
        return self._native_private(
            "get_universal_transfer_history",
            self._params(
                type=type_,
                startTime=startTime,
                endTime=endTime,
                current=current,
                size=size,
                fromSymbol=fromSymbol,
                toSymbol=toSymbol,
            ),
        )

    def get_margin_max_transferable(
        self,
        asset: str,
        *,
        isolatedSymbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return the account's current maximum transferable amount."""
        return self._native_private(
            "get_margin_max_transferable",
            self._params(asset=asset, isolatedSymbol=isolatedSymbol, recvWindow=recvWindow),
        )

    def transfer_subaccount_futures(
        self,
        email: str,
        asset: str,
        amount: str,
        type_: int,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Transfer between a sub-account's spot and futures wallets."""
        return self._native_private(
            "transfer_subaccount_futures",
            self._params(
                email=email,
                asset=asset,
                amount=amount,
                type=type_,
                recvWindow=recvWindow,
            ),
        )

    def transfer_subaccount_margin(
        self,
        email: str,
        asset: str,
        amount: str,
        type_: int,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Transfer between a sub-account's spot and margin wallets."""
        return self._native_private(
            "transfer_subaccount_margin",
            self._params(
                email=email,
                asset=asset,
                amount=amount,
                type=type_,
                recvWindow=recvWindow,
            ),
        )

    def get_subaccount_futures_transfer_history(
        self,
        email: str,
        futuresType: int = 1,
        **params: object,
    ) -> dict[str, Any]:
        """Return transfers between sub-account futures wallets."""
        return self._subaccount_query(
            "get_subaccount_futures_transfer_history",
            email=email,
            futuresType=futuresType,
            **params,
        )

    def transfer_between_subaccount_futures(
        self,
        fromEmail: str,
        toEmail: str,
        futuresType: int,
        asset: str,
        amount: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Transfer futures assets between accounts under the same master."""
        return self._subaccount_query(
            "transfer_between_subaccount_futures",
            fromEmail=fromEmail,
            toEmail=toEmail,
            futuresType=futuresType,
            asset=asset,
            amount=amount,
            recvWindow=recvWindow,
        )

    def get_subaccount_spot_transfer_history(self, **params: object) -> dict[str, Any]:
        """Return spot transfers between accounts under the same master."""
        return self._subaccount_query("get_subaccount_spot_transfer_history", **params)

    def get_subaccount_universal_transfer_history(self, **params: object) -> dict[str, Any]:
        """Return universal transfers between accounts under the same master."""
        return self._subaccount_query("get_subaccount_universal_transfer_history", **params)

    def transfer_between_subaccounts(
        self,
        fromAccountType: str,
        toAccountType: str,
        asset: str,
        amount: str,
        *,
        fromEmail: str | None = None,
        toEmail: str | None = None,
        clientTranId: str | None = None,
        symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Universally transfer assets within one Binance master-account tree."""
        return self._subaccount_query(
            "transfer_between_subaccounts",
            **{key: value for key, value in locals().items() if key != "self"},
        )

    def get_subaccount_transfer_history(self, **params: object) -> dict[str, Any]:
        """Return transfer history when authenticated as a sub-account."""
        return self._subaccount_query("get_subaccount_transfer_history", **params)

    def transfer_subaccount_to_master(
        self, asset: str, amount: str, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Transfer assets from a sub-account to its master account."""
        return self._subaccount_query(
            "transfer_subaccount_to_master",
            asset=asset,
            amount=amount,
            recvWindow=recvWindow,
        )

    def transfer_subaccount_to_subaccount(
        self,
        toEmail: str,
        asset: str,
        amount: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Transfer assets to a sibling sub-account under the same master."""
        return self._subaccount_query(
            "transfer_subaccount_to_subaccount",
            toEmail=toEmail,
            asset=asset,
            amount=amount,
            recvWindow=recvWindow,
        )


class TradeHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from TradeHTTP."""

    _native_private: Any

    _params: Any

    def get_pm_margin_transferable_amount(
        self, *, asset: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /papi/v1/margin/maxWithdraw.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-margin-max-withdraw

        """
        return self._native_private(
            "get_pm_margin_transferable_amount", self._params(asset=asset, recvWindow=recv_window)
        )

    def pm_bnb_transfer(
        self, *, amount: str, transfer_side: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        BNB transfer (TRADE).

        POST /papi/v1/bnb-transfer. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#bnb-transfer

        """
        return self._native_private(
            "pm_bnb_transfer",
            self._params(amount=amount, transferSide=transfer_side, recvWindow=recv_window),
        )

    def get_margin_cross_margin_transfer_history(
        self,
        *,
        asset: str | None = None,
        kind_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        isolated_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Cross Margin Transfer History (USER_DATA).

        GET /sapi/v1/margin/transfer. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/transfer#get-cross-margin-transfer-history

        """
        return self._native_private(
            "get_margin_cross_margin_transfer_history",
            self._params(
                asset=asset,
                type=kind_type,
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                isolatedSymbol=isolated_symbol,
                recvWindow=recv_window,
            ),
        )

    def wallet_dust_transfer(
        self,
        *,
        asset: str | list[str],
        account_type: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Dust Transfer (USER_DATA).

        POST /sapi/v1/asset/dust. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#dust-transfer

        """
        return self._native_private(
            "wallet_dust_transfer",
            self._params(asset=asset, accountType=account_type, recvWindow=recv_window),
        )

    def pm_pro_bnb_transfer(
        self, *, amount: str, transfer_side: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        BNB transfer (USER_DATA).

        POST /sapi/v1/portfolio/bnb-transfer. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#bnb-transfer

        """
        return self._native_private(
            "pm_pro_bnb_transfer",
            self._params(amount=amount, transferSide=transfer_side, recvWindow=recv_window),
        )

    def query_managed_sub_account_transfer_log_master_account_investor(
        self,
        *,
        email: str,
        start_time: int,
        end_time: int,
        page: int,
        limit: int,
        transfers: str | None = None,
        transfer_function_account_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/managed-subaccount/queryTransLogForInvestor.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#query-managed-sub-account-transfer-log-master-account-investor
        """
        return self._native_private(
            "query_managed_sub_account_transfer_log_master_account_investor",
            self._params(
                email=email,
                startTime=start_time,
                endTime=end_time,
                page=page,
                limit=limit,
                transfers=transfers,
                transferFunctionAccountType=transfer_function_account_type,
            ),
        )

    def query_managed_sub_account_transfer_log_master_account_trading(
        self,
        *,
        email: str,
        start_time: int,
        end_time: int,
        page: int,
        limit: int,
        transfers: str | None = None,
        transfer_function_account_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/managed-subaccount/queryTransLogForTradeParent.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#query-managed-sub-account-transfer-log-master-account-trading
        """
        return self._native_private(
            "query_managed_sub_account_transfer_log_master_account_trading",
            self._params(
                email=email,
                startTime=start_time,
                endTime=end_time,
                page=page,
                limit=limit,
                transfers=transfers,
                transferFunctionAccountType=transfer_function_account_type,
            ),
        )

    def query_managed_sub_account_transfer_log_sub_account_trading(
        self,
        *,
        start_time: int,
        end_time: int,
        page: int,
        limit: int,
        transfers: str | None = None,
        transfer_function_account_type: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/managed-subaccount/query-trans-log.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#query-managed-sub-account-transfer-log-sub-account-trading
        """
        return self._native_private(
            "query_managed_sub_account_transfer_log_sub_account_trading",
            self._params(
                startTime=start_time,
                endTime=end_time,
                page=page,
                limit=limit,
                transfers=transfers,
                transferFunctionAccountType=transfer_function_account_type,
                recvWindow=recv_window,
            ),
        )

    def get_transferable_earn_asset_balance_for_portfolio_margin(
        self, *, asset: str, transfer_type: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/portfolio/earn-asset-balance.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-transferable-earn-asset-balance-for-portfolio-margin
        """
        return self._native_private(
            "get_transferable_earn_asset_balance_for_portfolio_margin",
            self._params(asset=asset, transferType=transfer_type, recvWindow=recv_window),
        )

    def transfer_ldusdt_rwusd_for_portfolio_margin(
        self, *, asset: str, transfer_type: str, amount: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/portfolio/earn-asset-transfer.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#transfer-ldusdt-rwusd-for-portfolio-margin
        """
        return self._native_private(
            "transfer_ldusdt_rwusd_for_portfolio_margin",
            self._params(
                asset=asset, transferType=transfer_type, amount=amount, recvWindow=recv_window
            ),
        )
