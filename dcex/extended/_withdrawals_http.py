"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from AccountHTTP."""

    def create_withdrawal_signed(self, *, body: dict[str, Any]) -> dict[str, Any] | list[Any]:
        """
        Submit a caller-signed withdrawal settlement.

        API withdrawals have no second confirmation; they execute on submit.
        The caller supplies the official Stark settlement signature and scaled amount.
        EVM withdrawals require quoteId; STRK withdrawals use a Starknet wallet.
        Source: https://api.docs.extended.exchange/#withdrawals
        """
        return self._native_private(
            "create_withdrawal_signed", self._native_params(**{"body": body})
        )
