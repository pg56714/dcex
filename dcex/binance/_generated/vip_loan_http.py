"""Generated binance vip loan HTTP methods."""

from json import dumps
from typing import Any

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedVipLoanHTTP(MarketHTTP, TradeHTTP):
    """Vip loan API methods."""

    def get_vip_loan_interest_rate_history(
        self,
        *,
        coin: str,
        recv_window: int,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get VIP Loan Interest Rate History (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#get-viploan-interest-rate-history
        """
        return self._native_private(
            "get_vip_loan_interest_rate_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "coin": coin,
                    "recvWindow": recv_window,
                    "startTime": start_time,
                    "endTime": end_time,
                    "current": current,
                    "limit": limit,
                }.items()
                if value is not None
            ],
        )

    def query_vip_loan_fixed_rate_market(
        self,
        *,
        loan_coin: str,
        duration: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query VIP Loan Fixed Rate Market (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#query-viploan-fixed-rate-market
        """
        return self._native_private(
            "query_vip_loan_fixed_rate_market",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "loanCoin": loan_coin,
                    "duration": duration,
                    "current": current,
                    "size": size,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def vip_loan_borrow(
        self,
        *,
        loan_account_id: int,
        loan_coin: str,
        loan_amount: str,
        collateral_account_id: str,
        collateral_coin: str,
        is_flexible_rate: bool,
        loan_term: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        VIP Loan Borrow (TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/trade#vip-loan-borrow
        """
        return self._native_private(
            "vip_loan_borrow",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "loanAccountId": loan_account_id,
                    "loanCoin": loan_coin,
                    "loanAmount": loan_amount,
                    "collateralAccountId": collateral_account_id,
                    "collateralCoin": collateral_coin,
                    "isFlexibleRate": is_flexible_rate,
                    "loanTerm": loan_term,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def vip_loan_fixed_rate_borrow(
        self,
        *,
        supply_request: str,
        borrow_coin: str,
        loan_term: int,
        borrow_uid: int,
        collateral_coin: str,
        collateral_account_id: str,
        auto_repay: bool | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        VIP Loan Fixed Rate Borrow (TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/trade#vip-loan-fixed-rate-borrow
        """
        return self._native_private(
            "vip_loan_fixed_rate_borrow",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "supplyRequest": supply_request,
                    "borrowCoin": borrow_coin,
                    "loanTerm": loan_term,
                    "borrowUid": borrow_uid,
                    "collateralCoin": collateral_coin,
                    "collateralAccountId": collateral_account_id,
                    "autoRepay": auto_repay,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def vip_loan_renew(
        self, *, order_id: int, loan_term: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        VIP Loan Renew (TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/trade#vip-loan-renew
        """
        return self._native_private(
            "vip_loan_renew",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "loanTerm": loan_term,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def vip_loan_repay(self, *, order_id: int, amount: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        VIP Loan Repay (TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/trade#vip-loan-repay
        """
        return self._native_private(
            "vip_loan_repay",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "amount": amount,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def check_vip_loan_collateral_account(
        self,
        *,
        order_id: int | None = None,
        collateral_account_id: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Check VIP Loan Collateral Account (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/user-information#check-viploan-collateral-account
        """
        return self._native_private(
            "check_vip_loan_collateral_account",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "collateralAccountId": collateral_account_id,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def get_vip_loan_accrued_interest(
        self,
        *,
        order_id: int | None = None,
        loan_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get VIP Loan Accrued Interest (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/user-information#get-viploan-accrued-interest
        """
        return self._native_private(
            "get_vip_loan_accrued_interest",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "loanCoin": loan_coin,
                    "startTime": start_time,
                    "endTime": end_time,
                    "current": current,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def get_vip_loan_ongoing_orders(
        self,
        *,
        order_id: int | None = None,
        collateral_account_id: int | None = None,
        loan_coin: str | None = None,
        collateral_coin: str | None = None,
        current: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get VIP Loan Ongoing Orders (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/user-information#get-viploan-ongoing-orders
        """
        return self._native_private(
            "get_vip_loan_ongoing_orders",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "collateralAccountId": collateral_account_id,
                    "loanCoin": loan_coin,
                    "collateralCoin": collateral_coin,
                    "current": current,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def get_vip_loan_repayment_history(
        self,
        *,
        order_id: int | None = None,
        loan_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get VIP Loan Repayment History (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/user-information#get-viploan-repayment-history
        """
        return self._native_private(
            "get_vip_loan_repayment_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "loanCoin": loan_coin,
                    "startTime": start_time,
                    "endTime": end_time,
                    "current": current,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )
