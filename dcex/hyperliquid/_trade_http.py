"""Trading-related HTTP API client for Hyperliquid exchange backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for trading operations on Hyperliquid exchange."""

    def place_order(
        self,
        product_symbol: str,
        isBuy: bool,
        price: str,
        size: str,
        reduceOnly: bool,
        tif: str | None = None,
        isMarket: bool | None = None,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        cloid: str | None = None,
        grouping: str = "na",
        builder_address: str | None = None,
        fee_ten_bp: int | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Place an order on the exchange."""
        if (builder_address is None) != (fee_ten_bp is None):
            raise ValueError("builder_address and fee_ten_bp must be provided together")
        return self._native_private("place_order", self._native_params(**locals()))

    def place_future_market_order(
        self,
        product_symbol: str,
        isBuy: bool,
        size: str,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Place a future market order."""
        return self._native_private(
            "place_future_market_order",
            self._native_params(**locals()),
        )

    def place_future_market_buy_order(
        self,
        product_symbol: str,
        size: str,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Place a future market buy order."""
        return self._native_private(
            "place_future_market_buy_order",
            self._native_params(**locals()),
        )

    def place_future_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Place a future market sell order."""
        return self._native_private(
            "place_future_market_sell_order",
            self._native_params(**locals()),
        )

    def place_future_limit_order(
        self,
        product_symbol: str,
        isBuy: bool,
        price: str,
        size: str,
        tif: str,
    ) -> dict[str, Any]:
        """Place a future limit order."""
        return self._native_private(
            "place_future_limit_order",
            self._native_params(**locals()),
        )

    def place_future_limit_buy_order(
        self,
        product_symbol: str,
        price: str,
        size: str,
        tif: str,
    ) -> dict[str, Any]:
        """Place a future limit buy order."""
        return self._native_private(
            "place_future_limit_buy_order",
            self._native_params(**locals()),
        )

    def place_future_limit_sell_order(
        self,
        product_symbol: str,
        price: str,
        size: str,
        tif: str,
    ) -> dict[str, Any]:
        """Place a future limit sell order."""
        return self._native_private(
            "place_future_limit_sell_order",
            self._native_params(**locals()),
        )

    def cancel_order(
        self,
        product_symbol: str,
        oid: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel an order by order ID."""
        return self._native_private("cancel_order", self._native_params(**locals()))

    def cancel_order_by_cloid(
        self,
        product_symbol: str,
        cloid: str,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel an order by client order ID."""
        return self._native_private(
            "cancel_order_by_cloid",
            self._native_params(**locals()),
        )

    def schedule_cancel(
        self,
        time: int | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Schedule order cancellation."""
        return self._native_private("schedule_cancel", self._native_params(**locals()))

    def modify_order(
        self,
        oid: int | str,
        product_symbol: str,
        isBuy: bool,
        price: str,
        size: str,
        reduceOnly: bool,
        tif: str | None = None,
        isMarket: bool | None = None,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        cloid: str | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Modify an existing order."""
        return self._native_private("modify_order", self._native_params(**locals()))

    def modify_batch_orders(
        self,
        modifies: list,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Modify multiple orders in batch."""
        return self._native_private(
            "modify_batch_orders",
            self._native_params(**locals()),
        )

    def update_leverage(
        self,
        product_symbol: str,
        isCross: bool,
        leverage: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Update leverage for a product."""
        return self._native_private("update_leverage", self._native_params(**locals()))

    def update_isolate_margin(
        self,
        product_symbol: str,
        isBuy: bool,
        ntli: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Update isolated margin for a product."""
        return self._native_private(
            "update_isolate_margin",
            self._native_params(**locals()),
        )

    def place_twap_order(
        self,
        product_symbol: str,
        isBuy: bool,
        size: str,
        reduceOnly: bool,
        minutes: int,
        randomize: bool,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Place a TWAP order."""
        return self._native_private("place_twap_order", self._native_params(**locals()))

    def cancel_twap_order(
        self,
        product_symbol: str,
        twap_id: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel a TWAP order."""
        return self._native_private("cancel_twap_order", self._native_params(**locals()))
