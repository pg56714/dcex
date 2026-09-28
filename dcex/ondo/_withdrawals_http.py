# ruff: noqa: ANN401
"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from AccountHTTP."""

    def get_withdrawals(self) -> Any:
        return self._native_private("get_withdrawals")

    def get_withdrawal(self, withdrawalID: str) -> Any:
        return self._native_private("get_withdrawal", withdrawalID=withdrawalID)

    def get_withdrawal_limits(self) -> Any:
        return self._native_private("get_withdrawal_limits")

    def export_withdrawals_csv(
        self,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:
        return self._native_private(
            "export_withdrawals_csv",
            start_time=start_time,
            end_time=end_time,
        )

    def get_withdrawal_status(
        self,
        withdrawal_id: str | None = None,
        customer_withdrawal_id: str | None = None,
    ) -> Any:
        return self._native_private(
            "get_withdrawal_status",
            withdrawal_id=withdrawal_id,
            customer_withdrawal_id=customer_withdrawal_id,
        )

    def create_withdrawal(
        self,
        *,
        customer_withdrawal_id: str,
        symbol: str,
        network: str,
        amount: str,
        address: str,
        from_account: dict[str, Any] | None = None,
    ) -> Any:
        """
        Submit a withdrawal to the specified address.

        API withdrawals have no second confirmation; they execute on submit.
        Optional from_account identifies the main or margin wallet.
        Source: https://docs.ondoperps.xyz/api-reference/wallet/withdraw
        """
        return self._native_private(
            "create_withdrawal",
            **dict(
                **{
                    "customer_withdrawal_id": customer_withdrawal_id,
                    "symbol": symbol,
                    "network": network,
                    "amount": amount,
                    "address": address,
                    "from": from_account,
                }
            ),
        )

    def sandbox_withdrawal(
        self,
        *,
        customer_withdrawal_id: str,
        symbol: str,
        amount: str,
        from_account: dict[str, Any],
    ) -> Any:
        """
        Debit a specified wallet in the sandbox environment only.

        API withdrawals have no second confirmation; they execute on submit.
        Source: https://docs.ondoperps.xyz/api-reference/sandbox/sandbox-withdrawal
        """
        return self._native_private(
            "sandbox_withdrawal",
            **dict(
                **{
                    "customer_withdrawal_id": customer_withdrawal_id,
                    "symbol": symbol,
                    "amount": amount,
                    "from": from_account,
                }
            ),
        )
