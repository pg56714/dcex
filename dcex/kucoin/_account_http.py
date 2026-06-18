"""KuCoin account HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for KuCoin account API operations."""

    def get_account_balance(
        self,
        currency: str | None = None,
        type: str | None = None,  # noqa: A002
    ) -> dict[str, Any]:
        """Retrieve account balance information."""
        return self._native_private(
            "get_account_balance",
            self._native_params(currency=currency, type=type),
        )

    def get_transfer_quotas(
        self,
        currency: str,
        account_type: str,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve transferable balance for one KuCoin account type."""
        return self._native_private(
            "get_transfer_quotas",
            self._native_params(currency=currency, account_type=account_type, tag=tag),
        )

    def flex_transfer(
        self,
        currency: str,
        amount: str,
        fromAccountType: str,
        toAccountType: str,
        clientOid: str | None = None,
        transfer_type: str = "INTERNAL",
        fromUserId: str | None = None,
        toUserId: str | None = None,
    ) -> dict[str, Any]:
        """Transfer funds between KuCoin account types."""
        return self._native_private(
            "flex_transfer",
            self._native_params(
                currency=currency,
                amount=amount,
                fromAccountType=fromAccountType,
                toAccountType=toAccountType,
                clientOid=clientOid,
                transfer_type=transfer_type,
                fromUserId=fromUserId,
                toUserId=toUserId,
            ),
        )

    def get_futures_account(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures account overview."""
        return self._native_private(
            "get_futures_account",
            self._native_params(currency=currency),
        )

    def get_futures_positions(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures positions."""
        return self._native_private(
            "get_futures_positions",
            self._native_params(currency=currency),
        )

    def get_futures_position(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve one KuCoin futures position."""
        return self._native_private(
            "get_futures_position",
            self._native_params(product_symbol=product_symbol),
        )

    def get_futures_position_mode(self) -> dict[str, Any]:
        """Retrieve KuCoin futures position mode."""
        return self._native_private("get_futures_position_mode", [])

    def get_futures_cross_margin_leverage(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve cross-margin leverage for one KuCoin futures contract."""
        return self._native_private(
            "get_futures_cross_margin_leverage",
            self._native_params(product_symbol=product_symbol),
        )

    def modify_futures_cross_margin_leverage(
        self,
        product_symbol: str,
        leverage: int | str,
    ) -> dict[str, Any]:
        """Modify cross-margin leverage for one KuCoin futures contract."""
        return self._native_private(
            "modify_futures_cross_margin_leverage",
            self._native_params(product_symbol=product_symbol, leverage=leverage),
        )
