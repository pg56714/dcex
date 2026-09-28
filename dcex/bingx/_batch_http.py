"""Fund movement and batch endpoint mixins."""

from typing import Any

from .._keyword_aliases import legacy_keywords, wire_keywords
from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    _native_call_params: Any

    @legacy_keywords({"recvWindow": "recv_window"})
    def place_spot_batch_order(
        self,
        data: list[dict],
        sync: bool | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Place spot batch order."""
        return self._native_private(
            "place_spot_batch_order",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords(
        {
            "orderIds": "order_ids",
            "clientOrderIDs": "client_order_ids",
            "recvWindow": "recv_window",
        }
    )
    def cancel_spot_batch_orders(
        self,
        product_symbol: str,
        order_ids: list[int | str] | str,
        client_order_ids: list[str] | str | None = None,
        process: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Cancel spot batch orders."""
        return self._native_private(
            "cancel_spot_batch_orders",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderIds": "order_ids",
                        "clientOrderIDs": "client_order_ids",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords({"batchOrders": "batch_orders", "recvWindow": "recv_window"})
    def place_swap_batch_order(
        self,
        batch_orders: list,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Place swap batch order."""
        return self._native_private(
            "place_swap_batch_order",
            self._native_call_params(
                wire_keywords(
                    locals(), {"batchOrders": "batch_orders", "recvWindow": "recv_window"}
                )
            ),
        )

    @legacy_keywords(
        {
            "orderIdList": "order_id_list",
            "clientOrderIdList": "client_order_id_list",
            "recvWindow": "recv_window",
        }
    )
    def cancel_swap_batch_order(
        self,
        product_symbol: str,
        order_id_list: list | None = None,
        client_order_id_list: list | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Cancel swap batch order."""
        return self._native_private(
            "cancel_swap_batch_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderIdList": "order_id_list",
                        "clientOrderIdList": "client_order_id_list",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    def replace_swap_batch_orders(
        self, orders: list[dict[str, Any]], *, recv_window: int | None = None
    ) -> dict[str, Any]:
        """Cancel and replace multiple swap orders; preserve per-order failure results.

        Orders accept the native cancelReplace fields and product_symbol.
        """
        return self._native_private(
            "replace_swap_batch_orders",
            self._native_params(batchOrders=orders, recvWindow=recv_window),
        )
