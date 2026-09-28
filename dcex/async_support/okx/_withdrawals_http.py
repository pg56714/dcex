"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from AccountHTTP."""

    async def get_max_withdrawal(
        self,
        ccy: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get maximum withdrawal amount.

        Args:
            ccy: List of currencies to query

        Returns:
            Dict containing maximum withdrawal information
        """
        return await self._native_private(
            "get_max_withdrawal",
            self._native_params(ccy=ccy),
        )


class AssetHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from AssetHTTP."""

    async def get_deposit_withdraw_status(
        self,
        wdId: str | None = None,
        txId: str | None = None,
        ccy: str | None = None,
        to: str | None = None,
        chain: str | None = None,
    ) -> dict[str, Any]:
        """
        Get deposit and withdrawal status.

        Args:
            wdId: Withdrawal ID to query (optional).
            txId: Transaction ID to query (optional).
            ccy: Currency code to query (optional).
            to: Destination address to query (optional).
            chain: Blockchain network to query (optional).

        Returns:
            Dict containing deposit and withdrawal status information from OKX API.
        """
        if (wdId is None) == (txId is None):
            raise ValueError("Exactly one of wdId or txId is required.")
        if txId is not None:
            missing = [
                name
                for name, value in (("ccy", ccy), ("to", to), ("chain", chain))
                if value is None
            ]
            if missing:
                raise ValueError(
                    f"{', '.join(missing)} required when querying deposit status by txId."
                )
        return await self._native_private(
            "get_deposit_withdraw_status",
            self._native_params(wdId=wdId, txId=txId, ccy=ccy, to=to, chain=chain),
        )


class TradeHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from TradeHTTP."""

    async def trading_bot_grid_withdraw_income(self, *, algo_id: str) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/withdraw-income. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-spot-grid-withdraw-income
        """
        return await self._native_private(
            "trading_bot_grid_withdraw_income", self._native_params(algoId=algo_id)
        )

    async def get_asset_withdrawal_history(
        self,
        *,
        ccy: str | None = None,
        wd_id: str | None = None,
        client_id: str | None = None,
        tx_id: str | None = None,
        type_: str | None = None,
        state: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/asset/withdrawal-history. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-history
        """
        return await self._native_private(
            "get_asset_withdrawal_history",
            self._native_params(
                ccy=ccy,
                wdId=wd_id,
                clientId=client_id,
                txId=tx_id,
                type=type_,
                state=state,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    async def get_fiat_withdrawal_payment_methods(self, *, ccy: str) -> dict[str, Any]:
        """
        GET /api/v5/fiat/withdrawal-payment-methods. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-payment-methods
        """
        return await self._native_private(
            "get_fiat_withdrawal_payment_methods", self._native_params(ccy=ccy)
        )

    async def get_fiat_withdrawal_order_history(
        self,
        *,
        ccy: str | None = None,
        payment_method: str | None = None,
        state: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/fiat/withdrawal-order-history. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-order-history
        """
        return await self._native_private(
            "get_fiat_withdrawal_order_history",
            self._native_params(
                ccy=ccy,
                paymentMethod=payment_method,
                state=state,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    async def get_fiat_withdrawal(self, *, ord_id: str) -> dict[str, Any]:
        """
        GET /api/v5/fiat/withdrawal. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-order-detail
        """
        return await self._native_private("get_fiat_withdrawal", self._native_params(ordId=ord_id))

    async def get_account_subaccount_max_withdrawal(
        self, *, sub_acct: str, ccy: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/account/subaccount/max-withdrawal. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#sub-account-rest-api-get-sub-account-maximum-withdrawals
        """
        return await self._native_private(
            "get_account_subaccount_max_withdrawal", self._native_params(subAcct=sub_acct, ccy=ccy)
        )

    async def create_withdrawal(
        self,
        *,
        ccy: str,
        amt: str,
        dest: str,
        to_addr: str,
        to_addr_type: str | None = None,
        chain: str | None = None,
        area_code: str | None = None,
        rcvr_info: dict[str, Any] | None = None,
        client_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/asset/withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-withdrawal
        """
        return await self._native_private(
            "create_withdrawal",
            self._native_params(
                **{
                    "ccy": ccy,
                    "amt": amt,
                    "dest": dest,
                    "toAddr": to_addr,
                    "toAddrType": to_addr_type,
                    "chain": chain,
                    "areaCode": area_code,
                    "rcvrInfo": rcvr_info,
                    "clientId": client_id,
                }
            ),
        )

    async def cancel_withdrawal(
        self,
        *,
        wd_id: str,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/asset/cancel-withdrawal.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-cancel-withdrawal
        """
        return await self._native_private(
            "cancel_withdrawal",
            self._native_params(**{"wdId": wd_id}),
        )

    async def create_fiat_withdrawal(
        self,
        *,
        payment_acct_id: str,
        ccy: str,
        amt: str,
        payment_method: str,
        client_id: str,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/fiat/create-withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-create-withdrawal-order
        """
        return await self._native_private(
            "create_fiat_withdrawal",
            self._native_params(
                **{
                    "paymentAcctId": payment_acct_id,
                    "ccy": ccy,
                    "amt": amt,
                    "paymentMethod": payment_method,
                    "clientId": client_id,
                }
            ),
        )

    async def cancel_fiat_withdrawal(
        self,
        *,
        ord_id: str,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/fiat/cancel-withdrawal.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-cancel-withdrawal-order
        """
        return await self._native_private(
            "cancel_fiat_withdrawal",
            self._native_params(**{"ordId": ord_id}),
        )
