"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from AccountHTTP."""

    def batch_set_collateral_coins(self, request: list[dict[str, str]]) -> dict[str, Any]:
        """
        Batch set collateral coins; see
        https://bybit-exchange.github.io/docs/v5/account/batch-set-collateral.
        """
        return self._native_private(
            "batch_set_collateral_coins", self._native_params(request=request)
        )


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    def cancel_batch_orders(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Cancel multiple orders in batch."""
        return self._native_private(
            "cancel_batch_orders",
            self._native_params(request=request, category=category),
        )

    def place_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Place multiple orders in batch."""
        return self._native_private(
            "place_batch_order",
            self._native_params(request=request, category=category),
        )

    def amend_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Amend multiple orders in batch."""
        return self._native_private(
            "amend_batch_order",
            self._native_params(request=request, category=category),
        )
