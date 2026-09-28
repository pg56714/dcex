"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from AccountHTTP."""

    def get_fastwithdraw_info(
        self,
        account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter fast-withdraw information."""
        return self._native_private("get_fastwithdraw_info", self._native_params(**locals()))

    def get_withdraw_history(
        self,
        account_index: int | None = None,
        cursor: str | None = None,
        filter: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter withdrawal history."""
        return self._native_private("get_withdraw_history", self._native_params(**locals()))


class MarketHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from MarketHTTP."""

    def get_withdrawal_delay(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter withdrawal delay information."""
        return self._native_public("get_withdrawal_delay", self._native_params(**locals()))


class TradeHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from TradeHTTP."""

    def transfer_l2_account(
        self,
        *,
        to_account_index: int,
        asset_index: int,
        from_route_type: int,
        to_route_type: int,
        amount: int,
        usdc_fee: int = 0,
        memo_hex: str | None = None,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Transfer between L2 account indices using raw integer amount and fee units.

        The recipient may be another user. Transfers have no second confirmation;
        they execute on submit. Account-family membership is not verified locally.
        The exchange enforces eligibility.
        """
        return self._native_private("transfer_l2_account", self._native_params(**locals()))

    def sign_transfer_l2_account(
        self,
        *,
        to_account_index: int,
        asset_index: int,
        from_route_type: int,
        to_route_type: int,
        amount: int,
        usdc_fee: int = 0,
        memo_hex: str | None = None,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """
        Transfer between L2 account indices using raw integer amount and fee units.

        The recipient may be another user. Transfers have no second confirmation;
        they execute on submit. Account-family membership is not verified locally.
        The exchange enforces eligibility.
        """
        return self._native_sign("sign_transfer_l2_account", self._native_params(**locals()))

    def submit_fast_withdrawal(
        self,
        *,
        tx_info: str,
        to_address: str,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/fastwithdraw.

        API withdrawals have no second confirmation; they execute on submit.
        tx_info must be an already signed L2 transfer to the fast-withdraw service.

        https://apidocs.lighter.xyz/reference/fastwithdraw
        """
        return self._native_private("submit_fast_withdrawal", self._native_params(**locals()))

    def withdraw_l2(
        self,
        *,
        asset_index: int,
        route_type: int,
        amount: int,
        nonce: int | None = None,
        api_key_index: int | None = None,
        skip_nonce: int = 0,
    ) -> dict[str, Any] | list[Any]:
        """
        Submit L2 withdrawal transaction 13; amount uses raw integer asset units.

        API withdrawals have no second confirmation; they execute on submit.

        https://github.com/elliottech/lighter-go/blob/main/types/txtypes/withdraw.go
        """
        return self._native_private("withdraw_l2", self._native_params(**locals()))

    def sign_withdraw_l2(
        self,
        *,
        asset_index: int,
        route_type: int,
        amount: int,
        nonce: int | None = None,
        api_key_index: int | None = None,
        skip_nonce: int = 0,
    ) -> tuple[Any, Any, Any, Any]:
        """
        Sign L2 withdrawal transaction 13; amount uses raw integer asset units.

        https://github.com/elliottech/lighter-go/blob/main/types/txtypes/withdraw.go
        """
        return self._native_sign("sign_withdraw_l2", self._native_params(**locals()))

    transfer_same_master_account = transfer_l2_account
    sign_transfer_same_master_account = sign_transfer_l2_account
