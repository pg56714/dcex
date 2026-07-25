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
