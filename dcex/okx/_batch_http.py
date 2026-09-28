"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    def place_batch_orders(
        self,
        orders: list[dict],
    ) -> dict[str, Any]:
        """
        Place multiple orders in batch.

        Args:
            orders: List of order dictionaries

        Returns:
            Dict containing batch order placement results
        """

        return self._native_private(
            "place_batch_orders",
            self._native_params(orders=orders),
        )

    def cancel_batch_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Cancel multiple orders in batch.

        Args:
            orders: List of order dictionaries to cancel.

        Returns:
            Dictionary containing batch cancellation result.
        """
        return self._native_private(
            "cancel_batch_orders",
            self._native_params(orders=orders),
        )

    def rfq_cancel_batch_rfqs(
        self, *, rfq_ids: list[str] | None = None, cl_rfq_ids: list[str] | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/rfq/cancel-batch-rfqs. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-multiple-rfqs
        """
        return self._native_private(
            "rfq_cancel_batch_rfqs", self._native_params(rfqIds=rfq_ids, clRfqIds=cl_rfq_ids)
        )

    def cancel_rfq_batch_quotes(
        self,
        *,
        quote_ids: list[Any] | None = None,
        cl_quote_ids: list[Any] | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/rfq/cancel-batch-quotes.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-multiple-quotes
        """
        return self._native_private(
            "cancel_rfq_batch_quotes",
            self._native_params(**{"quoteIds": quote_ids, "clQuoteIds": cl_quote_ids}),
        )
