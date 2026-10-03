"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    def place_uta_batch_orders(self, order_list: list[dict[str, Any]]) -> dict[str, Any]:
        """Place Bitget UTA orders in batch."""
        return self._native_private(
            "place_uta_batch_orders",
            self._native_params(orderList=order_list),
        )

    def cancel_uta_batch_orders(self, order_list: list[dict[str, Any]]) -> dict[str, Any]:
        """Cancel Bitget UTA orders in batch."""
        return self._native_private(
            "cancel_uta_batch_orders",
            self._native_params(orderList=order_list),
        )

    def modify_uta_batch_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Call ``POST /api/v3/trade/batch-modify-order``. At most 20 orders in one category; ACK
        does not confirm matching-engine completion.
        """
        return self._native_private("modify_uta_batch_orders", self._native_params(orders=orders))

    def batch_create_classic_sub_accounts(self, accounts: list[dict[str, Any]]) -> dict[str, Any]:
        """Create 1..5 virtual sub-accounts and API keys using an array body."""
        return self._native_private(
            "batch_create_classic_sub_accounts", self._native_params(accounts=accounts)
        )
