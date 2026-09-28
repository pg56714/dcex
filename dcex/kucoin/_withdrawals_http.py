"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from TradeHTTP."""

    def get_futures_max_withdraw_margin(
        self, product_symbol: str, *, position_side: str | None = None
    ) -> dict[str, Any]:
        """GET /api/v1/margin/maxWithdrawMargin; classic trading account."""
        return self._native_private(
            "get_futures_max_withdraw_margin",
            self._native_params(product_symbol=product_symbol, positionSide=position_side),
        )

    def get_withdrawal_history_by_id(self, *, withdrawal_id: str) -> dict[str, Any]:
        """
        GET /api/v1/withdrawals/{withdrawalId}.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/rest/account-info/withdrawals/get-withdrawal-by-id
        """
        return self._native_private(
            "get_withdrawal_history_by_id", self._native_params(withdrawalId=withdrawal_id)
        )

    def get_withdrawal_history(
        self,
        *,
        currency: str,
        status: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v1/withdrawals.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/rest/account-info/withdrawals/get-withdrawal-history
        """
        return self._native_private(
            "get_withdrawal_history",
            self._native_params(
                currency=currency,
                status=status,
                startAt=start_at,
                endAt=end_at,
                currentPage=current_page,
                pageSize=page_size,
            ),
        )

    def get_withdrawal_quotas(self, *, currency: str, chain: str | None = None) -> dict[str, Any]:
        """
        GET /api/v1/withdrawals/quotas.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/rest/account-info/withdrawals/get-withdrawal-quotas
        """
        return self._native_private(
            "get_withdrawal_quotas", self._native_params(currency=currency, chain=chain)
        )

    def get_uta_withdrawal_history(
        self,
        *,
        currency: str | None = None,
        id: str | None = None,
        status: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/ua/v2/asset/withdrawal/history.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/v2/rest/ua/withdrawal-history
        """
        return self._native_private(
            "get_uta_withdrawal_history",
            self._native_params(
                currency=currency,
                id=id,
                status=status,
                startAt=start_at,
                endAt=end_at,
                currentPage=current_page,
                pageSize=page_size,
            ),
        )

    def get_uta_withdrawal_quotas(
        self,
        *,
        currency: str,
        withdraw_type: str,
        chain: str | None = None,
        is_inner: bool | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/ua/v2/withdrawals/quotas.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/v2/rest/ua/withdrawal-quota
        """
        return self._native_private(
            "get_uta_withdrawal_quotas",
            self._native_params(
                chain=chain, currency=currency, isInner=is_inner, withdrawType=withdraw_type
            ),
        )

    def create_withdrawal(
        self,
        *,
        currency: str,
        amount: str,
        to_address: str,
        withdraw_type: str,
        chain: str | None = None,
        memo: str | None = None,
        remark: str | None = None,
        is_inner: bool | None = None,
        fee_deduct_type: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Submit an address, UID, email or phone withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        Caller supplies chain and memo/tag required by the destination.
        Source: https://www.kucoin.com/docs-new/rest/account-info/withdrawals/withdraw-v3
        """
        return self._native_private(
            "create_withdrawal",
            self._native_params(
                currency=currency,
                amount=amount,
                toAddress=to_address,
                withdrawType=withdraw_type,
                chain=chain,
                memo=memo,
                remark=remark,
                isInner=is_inner,
                feeDeductType=fee_deduct_type,
            ),
        )

    def create_uta_withdrawal(
        self,
        *,
        currency: str,
        amount: str,
        to_address: str,
        withdraw_type: str,
        chain: str | None = None,
        memo: str | None = None,
        remark: str | None = None,
        is_inner: bool | None = None,
        fee_deduct_type: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Submit an address, UID, email or phone withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        Caller supplies chain and memo/tag required by the destination.
        Source: https://www.kucoin.com/docs-new/v2/rest/ua/withdrawal
        """
        return self._native_private(
            "create_uta_withdrawal",
            self._native_params(
                currency=currency,
                amount=amount,
                toAddress=to_address,
                withdrawType=withdraw_type,
                chain=chain,
                memo=memo,
                remark=remark,
                isInner=is_inner,
                feeDeductType=fee_deduct_type,
            ),
        )

    def cancel_withdrawal(self, withdrawal_id: str) -> dict[str, Any] | list[Any]:
        """
        Cancel a withdrawal while the exchange still permits cancellation.

        Source: https://www.kucoin.com/docs-new/rest/account-info/withdrawals/cancel-withdrawal
        """
        return self._native_private(
            "cancel_withdrawal", self._native_params(withdrawalId=withdrawal_id)
        )

    def cancel_uta_withdrawal(self, withdraw_id: str) -> dict[str, Any] | list[Any]:
        """
        Cancel a withdrawal while the exchange still permits cancellation.

        Source: https://www.kucoin.com/docs-new/v2/rest/ua/cancel-withdrawal
        """
        return self._native_private(
            "cancel_uta_withdrawal", self._native_params(withdrawId=withdraw_id)
        )
