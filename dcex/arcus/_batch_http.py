"""Fund movement and batch endpoint mixins."""

import json
from typing import Any

from ..base.http_manager import BaseHTTPManager


class ClientBatchHTTP(BaseHTTPManager):
    """Batch methods moved from Client."""

    private_request: Any

    _call: Any
    public_request: Any
    private_request: Any
    address: str | None
    account_index: int | None

    def batch_place_orders(
        self, orders: list[dict[str, Any]], *, grouping: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Place orders, optionally grouped as partialTpsl, positionTpsl, or entryTpsl.

        TPSL legs use tpsl_type, stop_price, and reduce_only=True.
        positionTpsl legs require quantity="0"; entryTpsl starts with the entry.
        """
        return self.private_request(
            "batch_place_orders",
            orders=json.dumps(orders, separators=(",", ":")),
            grouping=grouping,
        )

    def batch_cancel_orders(self, cancels: list[dict[str, Any]]) -> Any:  # noqa: ANN401
        """Cancel up to 100 individually signed orders in one request."""
        return self.private_request(
            "batch_cancel_orders", cancels=json.dumps(cancels, separators=(",", ":"))
        )

    def batch_modify_orders(self, modifies: list[dict[str, Any]]) -> Any:  # noqa: ANN401
        """Modify up to 100 individually signed orders in one request."""
        return self.private_request(
            "batch_modify_orders", modifies=json.dumps(modifies, separators=(",", ":"))
        )
