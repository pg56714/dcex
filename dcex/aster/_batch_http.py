"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    def place_futures_batch_orders(
        self,
        batchOrders: list[dict[str, Any]],
        nonce: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place multiple Aster futures orders."""
        return self._native_private(
            "place_futures_batch_orders",
            self._native_params(batchOrders=batchOrders, nonce=nonce),
        )

    def modify_futures_batch_orders(
        self,
        batchOrders: list[dict[str, Any]],  # noqa: N803
    ) -> dict[str, Any] | list[Any]:
        """Amend up to five futures orders independently."""
        return self._native_private(
            "modify_futures_batch_orders", self._native_params(batchOrders=batchOrders)
        )

    def cancel_futures_batch_orders(
        self,
        product_symbol: str,
        orderIdList: list[int] | None = None,
        origClientOrderIdList: list[str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel multiple Aster futures orders."""
        return self._native_private(
            "cancel_futures_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderIdList=orderIdList,
                origClientOrderIdList=origClientOrderIdList,
            ),
        )

    def guarded_cancel_futures_batch_orders(
        self,
        product_symbol: str,
        nonce: int,
        *,
        orderIdList: list[int] | None = None,
        origClientOrderIdList: list[str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel using the nonce of the original batch placement."""
        return self._native_private(
            "guarded_cancel_futures_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                nonce=nonce,
                orderIdList=orderIdList,
                origClientOrderIdList=origClientOrderIdList,
            ),
        )

    def place_spot_batch_orders_raw(self, **params: object) -> Any:  # noqa: ANN401
        """
        Submit caller-supplied batch order parameters.

        Official spec incomplete; not verified live. Inspect every item in the response;
        an HTTP success does not imply every order succeeded.
        """
        return self._native_private("place_spot_batch_orders_raw", self._native_params(**params))

    def cancel_spot_batch_orders_raw(self, **params: object) -> Any:  # noqa: ANN401
        """
        Cancel a batch using caller-supplied wire parameters.

        Official spec incomplete; not verified live. Inspect every item in the response.
        """
        return self._native_private("cancel_spot_batch_orders_raw", self._native_params(**params))
