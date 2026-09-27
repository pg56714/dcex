"""BingX trade HTTP client."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for BingX trade-related API endpoints backed by Rust."""

    def _native_call_params(self, values: dict[str, Any]) -> list[tuple[str, str]]:
        values.pop("self", None)
        return self._native_params(**values)

    def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        type_: str,
        timeInForce: str | None = None,
        quantity: float | str | None = None,
        quoteOrderQty: float | str | None = None,
        price: float | str | None = None,
        stopPrice: float | str | None = None,
        newClientOrderId: str | None = None,
        clientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("place_spot_order", self._native_call_params(locals()))

    def place_spot_market_buy_order(
        self,
        product_symbol: str,
        quoteOrderQty: float | str,
        clientOrderId: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_market_buy_order",
            self._native_call_params(locals()),
        )

    def place_spot_market_sell_order(
        self,
        product_symbol: str,
        quantity: float | str,
        clientOrderId: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_market_sell_order",
            self._native_call_params(locals()),
        )

    def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float | str,
        price: float | str,
        timeInForce: str | None = None,
        clientOrderId: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("place_spot_limit_order", self._native_call_params(locals()))

    def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        quantity: float | str,
        price: float | str,
        timeInForce: str | None = None,
        clientOrderId: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_limit_buy_order",
            self._native_call_params(locals()),
        )

    def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        quantity: float | str,
        price: float | str,
        timeInForce: str | None = None,
        clientOrderId: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_limit_sell_order",
            self._native_call_params(locals()),
        )

    def place_spot_post_only_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float | str,
        price: float | str,
        clientOrderId: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_post_only_order",
            self._native_call_params(locals()),
        )

    def place_spot_post_only_buy_order(
        self,
        product_symbol: str,
        quantity: float | str,
        price: float | str,
        clientOrderId: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_post_only_buy_order",
            self._native_call_params(locals()),
        )

    def place_spot_post_only_sell_order(
        self,
        product_symbol: str,
        quantity: float | str,
        price: float | str,
        clientOrderId: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_post_only_sell_order",
            self._native_call_params(locals()),
        )

    def place_spot_batch_order(
        self,
        data: list[dict],
        sync: bool | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("place_spot_batch_order", self._native_call_params(locals()))

    def replace_spot_order(
        self,
        product_symbol: str,
        cancelReplaceMode: str,  # noqa: N803
        side: str,
        type_: str,
        cancelOrderId: int | str | None = None,  # noqa: N803
        cancelClientOrderID: str | None = None,  # noqa: N803
        cancelRestrictions: str | None = None,  # noqa: N803
        quantity: float | str | None = None,
        quoteOrderQty: float | str | None = None,  # noqa: N803
        price: float | str | None = None,
        stopPrice: float | str | None = None,  # noqa: N803
        timeInForce: str | None = None,  # noqa: N803
        newClientOrderId: str | None = None,  # noqa: N803
        recvWindow: int | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Atomically request spot order cancellation and replacement."""
        return self._native_private("replace_spot_order", self._native_call_params(locals()))

    def cancel_spot_order(
        self,
        product_symbol: str,
        orderId: int | str | None = None,
        clientOrderID: str | None = None,
        clientOrderId: str | None = None,
        cancelRestrictions: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("cancel_spot_order", self._native_call_params(locals()))

    def cancel_spot_batch_orders(
        self,
        product_symbol: str,
        orderIds: list[int | str] | str,
        clientOrderIDs: list[str] | str | None = None,
        process: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "cancel_spot_batch_orders",
            self._native_call_params(locals()),
        )

    def cancel_spot_open_orders(
        self,
        product_symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("cancel_spot_open_orders", self._native_call_params(locals()))

    def set_spot_cancel_all_after(
        self,
        type_: str,
        timeOut: int | None = None,  # noqa: N803
        recvWindow: int | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Activate or close the spot order dead man's switch."""
        return self._native_private("set_spot_cancel_all_after", self._native_call_params(locals()))

    def get_spot_order(
        self,
        product_symbol: str,
        orderId: int | str | None = None,
        clientOrderID: str | None = None,
        clientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("get_spot_order", self._native_call_params(locals()))

    def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("get_spot_open_orders", self._native_call_params(locals()))

    def get_spot_order_history(
        self,
        product_symbol: str | None = None,
        orderId: int | str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        pageIndex: int = 1,
        pageSize: int = 100,
        status: str | None = None,
        type_: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("get_spot_order_history", self._native_call_params(locals()))

    def get_spot_my_trades(
        self,
        product_symbol: str,
        orderId: int | str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        fromId: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("get_spot_my_trades", self._native_call_params(locals()))

    def get_spot_commission_rate(
        self,
        product_symbol: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_spot_commission_rate",
            self._native_call_params(locals()),
        )

    def place_swap_order(
        self,
        product_symbol: str,
        type_: str,
        side: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
        price: float | None = None,
        quantity: float | None = None,
        quoteOrderQty: float | None = None,
        stopPrice: float | None = None,
        priceRate: float | None = None,
        stopLoss: str | None = None,
        takeProfit: str | None = None,
        workingType: str | None = None,
        clientOrderId: str | None = None,
        recvWindow: int | None = None,
        timeInForce: str | None = None,
        closePosition: str | None = None,
        activationPrice: float | None = None,
        stopGuaranteed: str | None = None,
        positionId: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("place_swap_order", self._native_call_params(locals()))

    def test_swap_order(
        self,
        product_symbol: str,
        type_: str,
        side: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
        price: float | None = None,
        quantity: float | None = None,
        quoteOrderQty: float | None = None,
        stopPrice: float | None = None,
        priceRate: float | None = None,
        stopLoss: str | None = None,
        takeProfit: str | None = None,
        workingType: str | None = None,
        clientOrderId: str | None = None,
        recvWindow: int | None = None,
        timeInForce: str | None = None,
        closePosition: str | None = None,
        activationPrice: float | None = None,
        stopGuaranteed: str | None = None,
        positionId: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("test_swap_order", self._native_call_params(locals()))

    def place_swap_market_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float,
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
        positionSide: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("place_swap_market_order", self._native_call_params(locals()))

    def place_swap_market_buy_order(
        self,
        product_symbol: str,
        quantity: float,
        positionSide: str = "LONG",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_swap_market_buy_order",
            self._native_call_params(locals()),
        )

    def place_swap_market_sell_order(
        self,
        product_symbol: str,
        quantity: float,
        positionSide: str = "SHORT",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_swap_market_sell_order",
            self._native_call_params(locals()),
        )

    def place_swap_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float,
        price: float,
        clientOrderId: str | None = None,
        timeInForce: str = "GTC",
        reduceOnly: str | None = None,
        positionSide: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("place_swap_limit_order", self._native_call_params(locals()))

    def place_swap_limit_buy_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        positionSide: str = "LONG",
        timeInForce: str = "GTC",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_swap_limit_buy_order",
            self._native_call_params(locals()),
        )

    def place_swap_limit_sell_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        positionSide: str = "SHORT",
        timeInForce: str = "GTC",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_swap_limit_sell_order",
            self._native_call_params(locals()),
        )

    def place_swap_post_only_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float,
        price: float,
        clientOrderId: str | None = None,
        timeInForce: str = "PostOnly",
        reduceOnly: str | None = None,
        positionSide: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_swap_post_only_order",
            self._native_call_params(locals()),
        )

    def place_swap_post_only_buy_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        positionSide: str = "LONG",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_swap_post_only_buy_order",
            self._native_call_params(locals()),
        )

    def place_swap_post_only_sell_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        positionSide: str = "SHORT",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_swap_post_only_sell_order",
            self._native_call_params(locals()),
        )

    def place_swap_batch_order(
        self,
        batchOrders: list,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("place_swap_batch_order", self._native_call_params(locals()))

    def cancel_swap_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        clientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("cancel_swap_order", self._native_call_params(locals()))

    def cancel_swap_batch_order(
        self,
        product_symbol: str,
        orderIdList: list | None = None,
        clientOrderIdList: list | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("cancel_swap_batch_order", self._native_call_params(locals()))

    def cancel_swap_all_orders(
        self,
        product_symbol: str | None = None,
        type_: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("cancel_swap_all_orders", self._native_call_params(locals()))

    def replace_swap_order(
        self,
        product_symbol: str,
        cancelReplaceMode: str,
        type_: str,
        side: str,
        positionSide: str,
        orderId: str | None = None,
        cancelClientOrderId: str | None = None,
        cancelOrderId: str | None = None,
        cancelRestrictions: str | None = None,
        reduceOnly: str | None = None,
        price: float | None = None,
        quantity: float | None = None,
        quoteOrderQty: float | None = None,
        stopPrice: float | None = None,
        priceRate: float | None = None,
        workingType: str | None = None,
        stopLoss: str | None = None,
        takeProfit: str | None = None,
        clientOrderId: str | None = None,
        closePosition: str | None = None,
        activationPrice: float | None = None,
        stopGuaranteed: str | None = None,
        timeInForce: str | None = None,
        positionId: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("replace_swap_order", self._native_call_params(locals()))

    def close_swap_position(
        self,
        positionId: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("close_swap_position", self._native_call_params(locals()))

    def close_swap_all_positions(
        self,
        product_symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("close_swap_all_positions", self._native_call_params(locals()))

    def get_order_detail(
        self,
        product_symbol: str,
        orderId: int | None = None,
        clientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("get_order_detail", self._native_call_params(locals()))

    def get_open_orders(
        self,
        product_symbol: str | None = None,
        type_: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("get_open_orders", self._native_call_params(locals()))

    def get_order_history(
        self,
        product_symbol: str | None = None,
        currency: str | None = None,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("get_order_history", self._native_call_params(locals()))

    def change_margin_type(
        self,
        product_symbol: str,
        marginType: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("change_margin_type", self._native_call_params(locals()))

    def get_margin_type(
        self,
        product_symbol: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("get_margin_type", self._native_call_params(locals()))

    def set_leverage(
        self,
        product_symbol: str,
        side: str,
        leverage: int,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("set_leverage", self._native_call_params(locals()))

    def get_leverage(
        self,
        product_symbol: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("get_leverage", self._native_call_params(locals()))

    def set_position_mode(
        self,
        dualSidePosition: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private("set_position_mode", self._native_call_params(locals()))

    def get_position_mode(self, recvWindow: int | None = None) -> dict[str, Any]:
        return self._native_private("get_position_mode", self._native_call_params(locals()))

    def set_swap_cancel_all_after(
        self, type_: str, timeOut: int, *, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v2/trade/cancelAllAfter``."""
        return self._native_private("set_swap_cancel_all_after", self._native_call_params(locals()))

    def get_swap_open_order(
        self,
        product_symbol: str,
        *,
        orderId: int | None = None,
        clientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v2/trade/openOrder``."""
        return self._native_private("get_swap_open_order", self._native_call_params(locals()))

    def get_swap_force_orders(
        self,
        *,
        product_symbol: str | None = None,
        currency: str | None = None,
        autoCloseType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v2/trade/forceOrders``."""
        return self._native_private("get_swap_force_orders", self._native_call_params(locals()))

    def get_swap_trade_fills(
        self,
        tradingUnit: str,
        startTs: int,
        endTs: int,
        *,
        orderId: int | None = None,
        currency: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v2/trade/allFillOrders``."""
        return self._native_private("get_swap_trade_fills", self._native_call_params(locals()))

    def adjust_swap_position_margin(
        self,
        product_symbol: str,
        amount: str,
        type_: int,
        *,
        positionSide: str | None = None,
        positionId: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v2/trade/positionMargin``."""
        return self._native_private(
            "adjust_swap_position_margin", self._native_call_params(locals())
        )

    def amend_swap_order(
        self,
        product_symbol: str,
        quantity: str,
        *,
        orderId: str | None = None,
        clientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v1/trade/amend``."""
        return self._native_private("amend_swap_order", self._native_call_params(locals()))

    def place_swap_twap_order(
        self,
        product_symbol: str,
        side: str,
        positionSide: str,
        priceType: str,
        priceVariance: str,
        triggerPrice: str,
        interval: int,
        amountPerOrder: str,
        totalAmount: str,
        *,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v1/twap/order``."""
        return self._native_private("place_swap_twap_order", self._native_call_params(locals()))

    def cancel_swap_twap_order(
        self, mainOrderId: str, *, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v1/twap/cancelOrder``."""
        return self._native_private("cancel_swap_twap_order", self._native_call_params(locals()))

    def get_swap_open_twap_orders(
        self, *, product_symbol: str | None = None, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/twap/openOrders``."""
        return self._native_private("get_swap_open_twap_orders", self._native_call_params(locals()))

    def get_swap_twap_order_history(
        self,
        pageIndex: int,
        pageSize: int,
        startTime: int,
        endTime: int,
        *,
        product_symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/twap/historyOrders``."""
        return self._native_private(
            "get_swap_twap_order_history", self._native_call_params(locals())
        )

    def get_swap_twap_order(
        self, mainOrderId: str, *, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/twap/orderDetail``."""
        return self._native_private("get_swap_twap_order", self._native_call_params(locals()))

    def get_swap_asset_mode(self, *, recvWindow: int | None = None) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/trade/assetMode``."""
        return self._native_private("get_swap_asset_mode", self._native_call_params(locals()))

    def set_swap_asset_mode(
        self, assetMode: str, *, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v1/trade/assetMode``."""
        return self._native_private("set_swap_asset_mode", self._native_call_params(locals()))

    def get_swap_multi_asset_rules(self, *, recvWindow: int | None = None) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/trade/multiAssetsRules``."""
        return self._native_private(
            "get_swap_multi_asset_rules", self._native_call_params(locals())
        )

    def get_swap_margin_assets(self, *, recvWindow: int | None = None) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/user/marginAssets``."""
        return self._native_private("get_swap_margin_assets", self._native_call_params(locals()))

    def get_swap_full_orders(
        self,
        limit: int,
        *,
        product_symbol: str | None = None,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/trade/fullOrder``."""
        return self._native_private("get_swap_full_orders", self._native_call_params(locals()))

    def get_swap_fill_history(
        self,
        product_symbol: str,
        startTs: int,
        endTs: int,
        *,
        currency: str | None = None,
        orderId: int | None = None,
        lastFillId: int | None = None,
        pageIndex: int | None = None,
        pageSize: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v2/trade/fillHistory``."""
        return self._native_private("get_swap_fill_history", self._native_call_params(locals()))

    def get_swap_position_history(
        self,
        product_symbol: str,
        startTs: int,
        endTs: int,
        *,
        currency: str | None = None,
        positionId: int | None = None,
        pageIndex: int | None = None,
        pageSize: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/trade/positionHistory``."""
        return self._native_private("get_swap_position_history", self._native_call_params(locals()))

    def get_swap_margin_history(
        self,
        product_symbol: str,
        positionId: str,
        startTime: int,
        endTime: int,
        pageIndex: int,
        pageSize: int,
        *,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/positionMargin/history``."""
        return self._native_private("get_swap_margin_history", self._native_call_params(locals()))

    def get_swap_maintenance_margin_ratios(
        self, product_symbol: str, *, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/maintMarginRatio``."""
        return self._native_private(
            "get_swap_maintenance_margin_ratios", self._native_call_params(locals())
        )

    def set_swap_auto_add_margin(
        self,
        product_symbol: str,
        positionId: int,
        functionSwitch: str,
        *,
        amount: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v1/trade/autoAddMargin``."""
        return self._native_private("set_swap_auto_add_margin", self._native_call_params(locals()))

    def place_coin_swap_order(
        self,
        *,
        product_symbol: str,
        side: str,
        type_: str,
        position_side: str | None = None,
        quantity: str | None = None,
        price: str | None = None,
        stop_price: str | None = None,
        time_in_force: str | None = None,
        client_order_id: str | None = None,
        working_type: str | None = None,
        take_profit: dict[str, Any] | None = None,
        stop_loss: dict[str, Any] | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        POST /openApi/cswap/v1/trade/order.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "place_coin_swap_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type_=type_,
                positionSide=position_side,
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                timeInForce=time_in_force,
                clientOrderId=client_order_id,
                workingType=working_type,
                takeProfit=take_profit,
                stopLoss=stop_loss,
                recvWindow=recv_window,
            ),
        )

    def cancel_coin_swap_order(
        self,
        *,
        product_symbol: str,
        order_id: int | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        DELETE /openApi/cswap/v1/trade/cancelOrder.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "cancel_coin_swap_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=order_id,
                clientOrderId=client_order_id,
                recvWindow=recv_window,
            ),
        )

    def cancel_coin_swap_all_orders(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        POST /openApi/cswap/v1/trade/allOpenOrders.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "cancel_coin_swap_all_orders",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def close_coin_swap_all_positions(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        POST /openApi/cswap/v1/trade/closeAllPositions.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "close_coin_swap_all_positions",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_coin_swap_open_orders(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/trade/openOrders.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "get_coin_swap_open_orders",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_coin_swap_order(
        self,
        *,
        product_symbol: str,
        order_id: int | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/trade/orderDetail.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "get_coin_swap_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=order_id,
                clientOrderId=client_order_id,
                recvWindow=recv_window,
            ),
        )

    def get_coin_swap_order_history(
        self,
        *,
        limit: int,
        product_symbol: str | None = None,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/trade/orderHistory.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "get_coin_swap_order_history",
            self._native_params(
                limit=limit,
                product_symbol=product_symbol,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    def get_coin_swap_fills(
        self,
        *,
        order_id: str,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/trade/allFillOrders.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "get_coin_swap_fills",
            self._native_params(
                orderId=order_id, pageIndex=page_index, pageSize=page_size, recvWindow=recv_window
            ),
        )

    def get_coin_swap_force_orders(
        self,
        *,
        product_symbol: str | None = None,
        auto_close_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/trade/forceOrders.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "get_coin_swap_force_orders",
            self._native_params(
                product_symbol=product_symbol,
                autoCloseType=auto_close_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def get_coin_swap_leverage(
        self, *, product_symbol: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/trade/leverage.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "get_coin_swap_leverage",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def set_coin_swap_leverage(
        self, *, product_symbol: str, side: str, leverage: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        POST /openApi/cswap/v1/trade/leverage.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "set_coin_swap_leverage",
            self._native_params(
                product_symbol=product_symbol, side=side, leverage=leverage, recvWindow=recv_window
            ),
        )

    def get_coin_swap_margin_type(
        self, *, product_symbol: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/trade/marginType.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "get_coin_swap_margin_type",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def set_coin_swap_margin_type(
        self, *, product_symbol: str, margin_type: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        POST /openApi/cswap/v1/trade/marginType.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "set_coin_swap_margin_type",
            self._native_params(
                product_symbol=product_symbol, marginType=margin_type, recvWindow=recv_window
            ),
        )

    def adjust_coin_swap_position_margin(
        self,
        *,
        product_symbol: str,
        position_side: str,
        amount: str,
        type_: int,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        POST /openApi/cswap/v1/trade/positionMargin.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "adjust_coin_swap_position_margin",
            self._native_params(
                product_symbol=product_symbol,
                positionSide=position_side,
                amount=amount,
                type_=type_,
                recvWindow=recv_window,
            ),
        )

    def get_coin_swap_commission_rate(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/user/commissionRate.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "get_coin_swap_commission_rate", self._native_params(recvWindow=recv_window)
        )

    def get_coin_swap_balance(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/user/balance.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "get_coin_swap_balance",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_coin_swap_positions(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/user/positions.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return self._native_private(
            "get_coin_swap_positions",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def place_spot_oco(
        self,
        *,
        product_symbol: str,
        side: str,
        quantity: str,
        limit_price: str,
        trigger_price: str,
        order_price: str,
        list_client_order_id: str | None = None,
        above_client_order_id: str | None = None,
        below_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        POST /openApi/spot/v1/oco/order.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/spot-trade/api-reference.md

        """
        return self._native_private(
            "place_spot_oco",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                quantity=quantity,
                limitPrice=limit_price,
                triggerPrice=trigger_price,
                orderPrice=order_price,
                listClientOrderId=list_client_order_id,
                aboveClientOrderId=above_client_order_id,
                belowClientOrderId=below_client_order_id,
                recvWindow=recv_window,
            ),
        )

    def cancel_spot_oco(
        self,
        *,
        order_id: str | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        POST /openApi/spot/v1/oco/cancel.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/spot-trade/api-reference.md

        """
        return self._native_private(
            "cancel_spot_oco",
            self._native_params(
                orderId=order_id, clientOrderId=client_order_id, recvWindow=recv_window
            ),
        )

    def get_spot_oco(
        self,
        *,
        order_list_id: str | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /openApi/spot/v1/oco/orderList.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/spot-trade/api-reference.md

        """
        return self._native_private(
            "get_spot_oco",
            self._native_params(
                orderListId=order_list_id, clientOrderId=client_order_id, recvWindow=recv_window
            ),
        )

    def get_spot_open_oco(
        self, *, page_index: int, page_size: int, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/spot/v1/oco/openOrderList.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/spot-trade/api-reference.md

        """
        return self._native_private(
            "get_spot_open_oco",
            self._native_params(pageIndex=page_index, pageSize=page_size, recvWindow=recv_window),
        )

    def get_spot_oco_history(
        self,
        *,
        page_index: int,
        page_size: int,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /openApi/spot/v1/oco/historyOrderList.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/spot-trade/api-reference.md

        """
        return self._native_private(
            "get_spot_oco_history",
            self._native_params(
                pageIndex=page_index,
                pageSize=page_size,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    def get_deposit_history(
        self,
        *,
        coin: str | None = None,
        status: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        tx_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /openApi/api/v3/capital/deposit/hisrec.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/spot-wallet/api-reference.md

        """
        return self._native_private(
            "get_deposit_history",
            self._native_params(
                coin=coin,
                status=status,
                startTime=start_time,
                endTime=end_time,
                offset=offset,
                limit=limit,
                txId=tx_id,
                recvWindow=recv_window,
            ),
        )

    def replace_swap_batch_orders(
        self, orders: list[dict[str, Any]], *, recv_window: int | None = None
    ) -> dict[str, Any]:
        """
        Cancel and replace multiple swap orders; preserve per-order failure results.

        Orders accept the native cancelReplace fields and product_symbol.
        """
        return self._native_private(
            "replace_swap_batch_orders",
            self._native_params(batchOrders=orders, recvWindow=recv_window),
        )

    def get_coin_network_config(
        self,
        *,
        coin: str | None = None,
        display_name: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """GET /openApi/wallets/v1/capital/config/getall. Timestamps use milliseconds."""
        return self._native_private(
            "get_coin_network_config",
            self._native_params(coin=coin, displayName=display_name, recvWindow=recv_window),
        )

    def get_deposit_addresses(
        self,
        *,
        coin: str,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """GET /openApi/wallets/v1/capital/deposit/address. Timestamps use milliseconds."""
        return self._native_private(
            "get_deposit_addresses",
            self._native_params(coin=coin, offset=offset, limit=limit, recvWindow=recv_window),
        )

    def get_deposit_risk_records(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """GET /openApi/wallets/v1/capital/deposit/riskRecords. Timestamps use milliseconds."""
        return self._native_private(
            "get_deposit_risk_records", self._native_params(recvWindow=recv_window)
        )

    def reverse_swap_position(
        self,
        *,
        type_: str,
        product_symbol: str,
        trigger_price: str | None = None,
        working_type: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """POST /openApi/swap/v1/trade/reverse. Timestamps use milliseconds."""
        return self._native_private(
            "reverse_swap_position",
            self._native_params(
                type_=type_,
                product_symbol=product_symbol,
                triggerPrice=trigger_price,
                workingType=working_type,
                recvWindow=recv_window,
            ),
        )

    def adjust_simulated_trading_balance(
        self,
        *,
        adjust_type: str | None = None,
        amount: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """POST /openApi/swap/v2/trade/getVst. Timestamps use milliseconds."""
        return self._native_private(
            "adjust_simulated_trading_balance",
            self._native_params(adjustType=adjust_type, amount=amount, recvWindow=recv_window),
        )

    def get_standard_futures_positions(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """GET /openApi/contract/v1/allPosition. Timestamps use milliseconds."""
        return self._native_private(
            "get_standard_futures_positions", self._native_params(recvWindow=recv_window)
        )

    def get_standard_futures_orders(
        self,
        *,
        product_symbol: str,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """GET /openApi/contract/v1/allOrders. Timestamps use milliseconds."""
        return self._native_private(
            "get_standard_futures_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def get_standard_futures_balance(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """GET /openApi/contract/v1/balance. Timestamps use milliseconds."""
        return self._native_private(
            "get_standard_futures_balance", self._native_params(recvWindow=recv_window)
        )

    def get_api_permissions(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """GET /openApi/v1/account/apiPermissions. Timestamps use milliseconds."""
        return self._native_private(
            "get_api_permissions", self._native_params(recvWindow=recv_window)
        )

    def create_sub_account(
        self, *, sub_account_string: str, note: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """POST /openApi/subAccount/v1/create. Timestamps use milliseconds."""
        return self._native_private(
            "create_sub_account",
            self._native_params(
                subAccountString=sub_account_string, note=note, recvWindow=recv_window
            ),
        )

    def set_sub_account_frozen(
        self, *, sub_uid: int, freeze: bool, recv_window: int | None = None
    ) -> dict[str, Any]:
        """POST /openApi/subAccount/v1/updateStatus. Timestamps use milliseconds."""
        return self._native_private(
            "set_sub_account_frozen",
            self._native_params(subUid=sub_uid, freeze=freeze, recvWindow=recv_window),
        )

    def create_sub_account_api_key(
        self,
        *,
        sub_uid: int,
        note: str,
        permissions: list[int],
        ip_addresses: list[str] | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """POST /openApi/subAccount/v1/apiKey/create. Timestamps use milliseconds."""
        return self._native_private(
            "create_sub_account_api_key",
            self._native_params(
                subUid=sub_uid,
                note=note,
                permissions=permissions,
                ipAddresses=ip_addresses,
                recvWindow=recv_window,
            ),
        )

    def modify_sub_account_api_key(
        self,
        *,
        sub_uid: int,
        api_key: str,
        note: str,
        permissions: list[int],
        ip_addresses: list[str] | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """POST /openApi/subAccount/v1/apiKey/edit. Timestamps use milliseconds."""
        return self._native_private(
            "modify_sub_account_api_key",
            self._native_params(
                subUid=sub_uid,
                apiKey=api_key,
                note=note,
                permissions=permissions,
                ipAddresses=ip_addresses,
                recvWindow=recv_window,
            ),
        )

    def delete_sub_account_api_key(
        self, *, sub_uid: int, api_key: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """POST /openApi/subAccount/v1/apiKey/del. Timestamps use milliseconds."""
        return self._native_private(
            "delete_sub_account_api_key",
            self._native_params(subUid=sub_uid, apiKey=api_key, recvWindow=recv_window),
        )

    def set_sub_account_transfer_authorization(
        self, *, sub_uids: str, transferable: bool, recv_window: int | None = None
    ) -> dict[str, Any]:
        """
        POST /openApi/account/v1/innerTransfer/authorizeSubAccount. Timestamps use milliseconds.
        """
        return self._native_private(
            "set_sub_account_transfer_authorization",
            self._native_params(
                subUids=sub_uids, transferable=transferable, recvWindow=recv_window
            ),
        )

    def get_sub_account_deposit_addresses(
        self,
        *,
        coin: str,
        sub_uid: int,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /openApi/wallets/v1/capital/subAccount/deposit/address. Timestamps use milliseconds.
        """
        return self._native_private(
            "get_sub_account_deposit_addresses",
            self._native_params(
                coin=coin, subUid=sub_uid, offset=offset, limit=limit, recvWindow=recv_window
            ),
        )

    def get_sub_account_deposit_history(
        self,
        *,
        coin: str | None = None,
        sub_uid: int | None = None,
        tx_id: str | None = None,
        status: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """GET /openApi/wallets/v1/capital/deposit/subHisrec. Timestamps use milliseconds."""
        return self._native_private(
            "get_sub_account_deposit_history",
            self._native_params(
                coin=coin,
                subUid=sub_uid,
                txId=tx_id,
                status=status,
                startTime=start_time,
                endTime=end_time,
                offset=offset,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def get_api_restrictions(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """GET /openApi/v1/account/apiRestrictions. Timestamps use milliseconds."""
        return self._native_private(
            "get_api_restrictions", self._native_params(recvWindow=recv_window)
        )

    def create_sub_account_deposit_address(
        self,
        *,
        coin: str,
        sub_uid: int,
        network: str,
        wallet_type: int,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """
        POST /openApi/wallets/v1/capital/deposit/createSubAddress. Timestamps use milliseconds.
        """
        return self._native_private(
            "create_sub_account_deposit_address",
            self._native_params(
                coin=coin,
                subUid=sub_uid,
                network=network,
                walletType=wallet_type,
                recvWindow=recv_window,
            ),
        )

    def export_swap_income(
        self,
        *,
        product_symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> bytes:
        """Download the income report as Excel bytes; timestamps use milliseconds."""
        if self._native_client is None:
            raise RuntimeError("BingX native client is required.")
        return self._native_client.export_swap_income(
            self._native_params(
                product_symbol=product_symbol,
                incomeType=income_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            )
        )

    def get_withdrawal_history(
        self,
        *,
        id: str | None = None,
        coin: str | None = None,
        withdraw_order_id: str | None = None,
        status: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        tx_id: str | None = None,
        recv_window: int | None = None,
    ) -> list[dict[str, Any]]:
        """GET /openApi/api/v3/capital/withdraw/history. Timestamps use milliseconds."""
        return self._native_private(
            "get_withdrawal_history",
            self._native_params(
                id=id,
                coin=coin,
                withdrawOrderId=withdraw_order_id,
                status=status,
                startTime=start_time,
                endTime=end_time,
                offset=offset,
                limit=limit,
                txId=tx_id,
                recvWindow=recv_window,
            ),
        )

    def get_internal_transfer_records(
        self,
        *,
        coin: str,
        id: str | None = None,
        transfer_client_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """GET /openApi/wallets/v1/capital/innerTransfer/records. Timestamps use milliseconds."""
        return self._native_private(
            "get_internal_transfer_records",
            self._native_params(
                coin=coin,
                id=id,
                transferClientId=transfer_client_id,
                startTime=start_time,
                endTime=end_time,
                offset=offset,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def get_sub_account_internal_transfer_records(
        self,
        *,
        coin: str,
        transfer_client_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /openApi/wallets/v1/capital/subAccount/innerTransfer/records. Timestamps use
        milliseconds.
        """
        return self._native_private(
            "get_sub_account_internal_transfer_records",
            self._native_params(
                coin=coin,
                transferClientId=transfer_client_id,
                startTime=start_time,
                endTime=end_time,
                offset=offset,
                limit=limit,
                recvWindow=recv_window,
            ),
        )
