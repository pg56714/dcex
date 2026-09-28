"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from AccountHTTP."""

    def get_max_withdrawal_quantity(
        self,
        symbol: str,
        autoBorrow: bool | None = None,
        autoLendRedeem: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack max withdrawal quantity."""
        return self._native_private(
            "get_max_withdrawal_quantity",
            self._native_params(**locals()),
        )

    def get_withdrawals(
        self,
        id: int | None = None,
        clientId: str | None = None,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack withdrawal history."""
        return self._native_private(
            "get_withdrawals",
            self._native_params(**locals()),
        )


class TradeHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from TradeHTTP."""

    def create_withdrawal(
        self,
        *,
        address: str,
        blockchain: str,
        quantity: str,
        symbol: str,
        client_id: str | None = None,
        two_factor_token: str | None = None,
        auto_borrow: bool | None = None,
        auto_lend_redeem: bool | None = None,
        recipient_information: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Submit a withdrawal with the documented withdraw signing instruction.

        API withdrawals have no second confirmation; they execute on submit.
        two_factor_token is required unless the exchange exempts the destination.
        recipient_information is sent in the body but excluded from the signature.
        Source: https://docs.backpack.exchange/#tag/Capital/operation/request_withdrawal
        """
        return self._native_private(
            "create_withdrawal",
            self._native_params(
                **{
                    "address": address,
                    "blockchain": blockchain,
                    "quantity": quantity,
                    "symbol": symbol,
                    "clientId": client_id,
                    "twoFactorToken": two_factor_token,
                    "autoBorrow": auto_borrow,
                    "autoLendRedeem": auto_lend_redeem,
                    "recipientInformation": recipient_information,
                }
            ),
        )
