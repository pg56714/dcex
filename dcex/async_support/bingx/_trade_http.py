"""BingX trade HTTP client."""

from typing import Any

from ..._keyword_aliases import legacy_keywords, wire_keywords
from ..._operation_guards import require_confirmation, require_scope
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for BingX trade-related API endpoints backed by Rust."""

    def _native_call_params(self, values: dict[str, Any]) -> list[tuple[str, str]]:
        values.pop("self", None)
        return self._native_params(**values)

    @legacy_keywords(
        {
            "timeInForce": "time_in_force",
            "quoteOrderQty": "quote_order_qty",
            "stopPrice": "stop_price",
            "newClientOrderId": "new_client_order_id",
            "clientOrderId": "client_order_id",
            "recvWindow": "recv_window",
        }
    )
    async def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        type_: str,
        time_in_force: str | None = None,
        quantity: float | str | None = None,
        quote_order_qty: float | str | None = None,
        price: float | str | None = None,
        stop_price: float | str | None = None,
        new_client_order_id: str | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_spot_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "timeInForce": "time_in_force",
                        "quoteOrderQty": "quote_order_qty",
                        "stopPrice": "stop_price",
                        "newClientOrderId": "new_client_order_id",
                        "clientOrderId": "client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "quoteOrderQty": "quote_order_qty",
            "clientOrderId": "client_order_id",
            "newClientOrderId": "new_client_order_id",
            "recvWindow": "recv_window",
        }
    )
    async def place_spot_market_buy_order(
        self,
        product_symbol: str,
        quote_order_qty: float | str,
        client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_spot_market_buy_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "quoteOrderQty": "quote_order_qty",
                        "clientOrderId": "client_order_id",
                        "newClientOrderId": "new_client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "clientOrderId": "client_order_id",
            "newClientOrderId": "new_client_order_id",
            "recvWindow": "recv_window",
        }
    )
    async def place_spot_market_sell_order(
        self,
        product_symbol: str,
        quantity: float | str,
        client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_spot_market_sell_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "clientOrderId": "client_order_id",
                        "newClientOrderId": "new_client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "timeInForce": "time_in_force",
            "clientOrderId": "client_order_id",
            "newClientOrderId": "new_client_order_id",
            "recvWindow": "recv_window",
        }
    )
    async def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float | str,
        price: float | str,
        time_in_force: str | None = None,
        client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_spot_limit_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "timeInForce": "time_in_force",
                        "clientOrderId": "client_order_id",
                        "newClientOrderId": "new_client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "timeInForce": "time_in_force",
            "clientOrderId": "client_order_id",
            "newClientOrderId": "new_client_order_id",
            "recvWindow": "recv_window",
        }
    )
    async def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        quantity: float | str,
        price: float | str,
        time_in_force: str | None = None,
        client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_spot_limit_buy_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "timeInForce": "time_in_force",
                        "clientOrderId": "client_order_id",
                        "newClientOrderId": "new_client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "timeInForce": "time_in_force",
            "clientOrderId": "client_order_id",
            "newClientOrderId": "new_client_order_id",
            "recvWindow": "recv_window",
        }
    )
    async def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        quantity: float | str,
        price: float | str,
        time_in_force: str | None = None,
        client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_spot_limit_sell_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "timeInForce": "time_in_force",
                        "clientOrderId": "client_order_id",
                        "newClientOrderId": "new_client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "clientOrderId": "client_order_id",
            "newClientOrderId": "new_client_order_id",
            "recvWindow": "recv_window",
        }
    )
    async def place_spot_post_only_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float | str,
        price: float | str,
        client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_spot_post_only_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "clientOrderId": "client_order_id",
                        "newClientOrderId": "new_client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "clientOrderId": "client_order_id",
            "newClientOrderId": "new_client_order_id",
            "recvWindow": "recv_window",
        }
    )
    async def place_spot_post_only_buy_order(
        self,
        product_symbol: str,
        quantity: float | str,
        price: float | str,
        client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_spot_post_only_buy_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "clientOrderId": "client_order_id",
                        "newClientOrderId": "new_client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "clientOrderId": "client_order_id",
            "newClientOrderId": "new_client_order_id",
            "recvWindow": "recv_window",
        }
    )
    async def place_spot_post_only_sell_order(
        self,
        product_symbol: str,
        quantity: float | str,
        price: float | str,
        client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_spot_post_only_sell_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "clientOrderId": "client_order_id",
                        "newClientOrderId": "new_client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def place_spot_batch_order(
        self,
        data: list[dict],
        sync: bool | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_spot_batch_order",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords(
        {
            "cancelReplaceMode": "cancel_replace_mode",
            "cancelOrderId": "cancel_order_id",
            "cancelClientOrderID": "cancel_client_order_id",
            "cancelRestrictions": "cancel_restrictions",
            "quoteOrderQty": "quote_order_qty",
            "stopPrice": "stop_price",
            "timeInForce": "time_in_force",
            "newClientOrderId": "new_client_order_id",
            "recvWindow": "recv_window",
        }
    )
    async def replace_spot_order(
        self,
        product_symbol: str,
        cancel_replace_mode: str,  # noqa: N803
        side: str,
        type_: str,
        cancel_order_id: int | str | None = None,  # noqa: N803
        cancel_client_order_id: str | None = None,  # noqa: N803
        cancel_restrictions: str | None = None,  # noqa: N803
        quantity: float | str | None = None,
        quote_order_qty: float | str | None = None,  # noqa: N803
        price: float | str | None = None,
        stop_price: float | str | None = None,  # noqa: N803
        time_in_force: str | None = None,  # noqa: N803
        new_client_order_id: str | None = None,  # noqa: N803
        recv_window: int | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Atomically request spot order cancellation and replacement."""
        return await self._native_private(
            "replace_spot_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "cancelReplaceMode": "cancel_replace_mode",
                        "cancelOrderId": "cancel_order_id",
                        "cancelClientOrderID": "cancel_client_order_id",
                        "cancelRestrictions": "cancel_restrictions",
                        "quoteOrderQty": "quote_order_qty",
                        "stopPrice": "stop_price",
                        "timeInForce": "time_in_force",
                        "newClientOrderId": "new_client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "orderId": "order_id",
            "clientOrderID": "client_order_id",
            "clientOrderId": "client_order_id",
            "cancelRestrictions": "cancel_restrictions",
            "recvWindow": "recv_window",
        }
    )
    async def cancel_spot_order(
        self,
        product_symbol: str,
        order_id: int | str | None = None,
        client_order_id: str | None = None,
        cancel_restrictions: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "cancel_spot_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderId": "order_id",
                        "clientOrderID": "client_order_id",
                        "cancelRestrictions": "cancel_restrictions",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "orderIds": "order_ids",
            "clientOrderIDs": "client_order_ids",
            "recvWindow": "recv_window",
        }
    )
    async def cancel_spot_batch_orders(
        self,
        product_symbol: str,
        order_ids: list[int | str] | str,
        client_order_ids: list[str] | str | None = None,
        process: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
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

    @legacy_keywords({"recvWindow": "recv_window"})
    async def cancel_spot_open_orders(
        self,
        product_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "cancel_spot_open_orders",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords({"timeOut": "time_out", "recvWindow": "recv_window"})
    async def set_spot_cancel_all_after(
        self,
        type_: str,
        time_out: int | None = None,  # noqa: N803
        recv_window: int | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Activate or close the spot order dead man's switch."""
        return await self._native_private(
            "set_spot_cancel_all_after",
            self._native_call_params(
                wire_keywords(locals(), {"timeOut": "time_out", "recvWindow": "recv_window"})
            ),
        )

    @legacy_keywords(
        {
            "orderId": "order_id",
            "clientOrderID": "client_order_id",
            "clientOrderId": "client_order_id",
            "recvWindow": "recv_window",
        }
    )
    async def get_spot_order(
        self,
        product_symbol: str,
        order_id: int | str | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_spot_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderId": "order_id",
                        "clientOrderID": "client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_spot_open_orders",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords(
        {
            "orderId": "order_id",
            "startTime": "start_time",
            "endTime": "end_time",
            "pageIndex": "page_index",
            "pageSize": "page_size",
            "recvWindow": "recv_window",
        }
    )
    async def get_spot_order_history(
        self,
        product_symbol: str | None = None,
        order_id: int | str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_index: int = 1,
        page_size: int = 100,
        status: str | None = None,
        type_: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_spot_order_history",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderId": "order_id",
                        "startTime": "start_time",
                        "endTime": "end_time",
                        "pageIndex": "page_index",
                        "pageSize": "page_size",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "orderId": "order_id",
            "startTime": "start_time",
            "endTime": "end_time",
            "fromId": "from_id",
            "recvWindow": "recv_window",
        }
    )
    async def get_spot_my_trades(
        self,
        product_symbol: str,
        order_id: int | str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        from_id: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_spot_my_trades",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderId": "order_id",
                        "startTime": "start_time",
                        "endTime": "end_time",
                        "fromId": "from_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_spot_commission_rate(
        self,
        product_symbol: str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_spot_commission_rate",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords(
        {
            "positionSide": "position_side",
            "reduceOnly": "reduce_only",
            "quoteOrderQty": "quote_order_qty",
            "stopPrice": "stop_price",
            "priceRate": "price_rate",
            "stopLoss": "stop_loss",
            "takeProfit": "take_profit",
            "workingType": "working_type",
            "clientOrderId": "client_order_id",
            "recvWindow": "recv_window",
            "timeInForce": "time_in_force",
            "closePosition": "close_position",
            "activationPrice": "activation_price",
            "stopGuaranteed": "stop_guaranteed",
            "positionId": "position_id",
        }
    )
    async def place_swap_order(
        self,
        product_symbol: str,
        type_: str,
        side: str,
        position_side: str | None = None,
        reduce_only: str | None = None,
        price: float | None = None,
        quantity: float | None = None,
        quote_order_qty: float | None = None,
        stop_price: float | None = None,
        price_rate: float | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        working_type: str | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
        time_in_force: str | None = None,
        close_position: str | None = None,
        activation_price: float | None = None,
        stop_guaranteed: str | None = None,
        position_id: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_swap_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionSide": "position_side",
                        "reduceOnly": "reduce_only",
                        "quoteOrderQty": "quote_order_qty",
                        "stopPrice": "stop_price",
                        "priceRate": "price_rate",
                        "stopLoss": "stop_loss",
                        "takeProfit": "take_profit",
                        "workingType": "working_type",
                        "clientOrderId": "client_order_id",
                        "recvWindow": "recv_window",
                        "timeInForce": "time_in_force",
                        "closePosition": "close_position",
                        "activationPrice": "activation_price",
                        "stopGuaranteed": "stop_guaranteed",
                        "positionId": "position_id",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "positionSide": "position_side",
            "reduceOnly": "reduce_only",
            "quoteOrderQty": "quote_order_qty",
            "stopPrice": "stop_price",
            "priceRate": "price_rate",
            "stopLoss": "stop_loss",
            "takeProfit": "take_profit",
            "workingType": "working_type",
            "clientOrderId": "client_order_id",
            "recvWindow": "recv_window",
            "timeInForce": "time_in_force",
            "closePosition": "close_position",
            "activationPrice": "activation_price",
            "stopGuaranteed": "stop_guaranteed",
            "positionId": "position_id",
        }
    )
    async def test_swap_order(
        self,
        product_symbol: str,
        type_: str,
        side: str,
        position_side: str | None = None,
        reduce_only: str | None = None,
        price: float | None = None,
        quantity: float | None = None,
        quote_order_qty: float | None = None,
        stop_price: float | None = None,
        price_rate: float | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        working_type: str | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
        time_in_force: str | None = None,
        close_position: str | None = None,
        activation_price: float | None = None,
        stop_guaranteed: str | None = None,
        position_id: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "test_swap_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionSide": "position_side",
                        "reduceOnly": "reduce_only",
                        "quoteOrderQty": "quote_order_qty",
                        "stopPrice": "stop_price",
                        "priceRate": "price_rate",
                        "stopLoss": "stop_loss",
                        "takeProfit": "take_profit",
                        "workingType": "working_type",
                        "clientOrderId": "client_order_id",
                        "recvWindow": "recv_window",
                        "timeInForce": "time_in_force",
                        "closePosition": "close_position",
                        "activationPrice": "activation_price",
                        "stopGuaranteed": "stop_guaranteed",
                        "positionId": "position_id",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "clientOrderId": "client_order_id",
            "reduceOnly": "reduce_only",
            "positionSide": "position_side",
            "recvWindow": "recv_window",
        }
    )
    async def place_swap_market_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float,
        client_order_id: str | None = None,
        reduce_only: str | None = None,
        position_side: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_swap_market_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "clientOrderId": "client_order_id",
                        "reduceOnly": "reduce_only",
                        "positionSide": "position_side",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "positionSide": "position_side",
            "clientOrderId": "client_order_id",
            "reduceOnly": "reduce_only",
            "recvWindow": "recv_window",
        }
    )
    async def place_swap_market_buy_order(
        self,
        product_symbol: str,
        quantity: float,
        position_side: str = "LONG",
        client_order_id: str | None = None,
        reduce_only: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_swap_market_buy_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionSide": "position_side",
                        "clientOrderId": "client_order_id",
                        "reduceOnly": "reduce_only",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "positionSide": "position_side",
            "clientOrderId": "client_order_id",
            "reduceOnly": "reduce_only",
            "recvWindow": "recv_window",
        }
    )
    async def place_swap_market_sell_order(
        self,
        product_symbol: str,
        quantity: float,
        position_side: str,
        client_order_id: str | None = None,
        reduce_only: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_swap_market_sell_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionSide": "position_side",
                        "clientOrderId": "client_order_id",
                        "reduceOnly": "reduce_only",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "clientOrderId": "client_order_id",
            "timeInForce": "time_in_force",
            "reduceOnly": "reduce_only",
            "positionSide": "position_side",
            "recvWindow": "recv_window",
        }
    )
    async def place_swap_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float,
        price: float,
        client_order_id: str | None = None,
        time_in_force: str = "GTC",
        reduce_only: str | None = None,
        position_side: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_swap_limit_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "clientOrderId": "client_order_id",
                        "timeInForce": "time_in_force",
                        "reduceOnly": "reduce_only",
                        "positionSide": "position_side",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "positionSide": "position_side",
            "timeInForce": "time_in_force",
            "clientOrderId": "client_order_id",
            "reduceOnly": "reduce_only",
            "recvWindow": "recv_window",
        }
    )
    async def place_swap_limit_buy_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        position_side: str = "LONG",
        time_in_force: str = "GTC",
        client_order_id: str | None = None,
        reduce_only: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_swap_limit_buy_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionSide": "position_side",
                        "timeInForce": "time_in_force",
                        "clientOrderId": "client_order_id",
                        "reduceOnly": "reduce_only",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "positionSide": "position_side",
            "timeInForce": "time_in_force",
            "clientOrderId": "client_order_id",
            "reduceOnly": "reduce_only",
            "recvWindow": "recv_window",
        }
    )
    async def place_swap_limit_sell_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        position_side: str,
        time_in_force: str = "GTC",
        client_order_id: str | None = None,
        reduce_only: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_swap_limit_sell_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionSide": "position_side",
                        "timeInForce": "time_in_force",
                        "clientOrderId": "client_order_id",
                        "reduceOnly": "reduce_only",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "clientOrderId": "client_order_id",
            "timeInForce": "time_in_force",
            "reduceOnly": "reduce_only",
            "positionSide": "position_side",
            "recvWindow": "recv_window",
        }
    )
    async def place_swap_post_only_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float,
        price: float,
        client_order_id: str | None = None,
        time_in_force: str = "PostOnly",
        reduce_only: str | None = None,
        position_side: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_swap_post_only_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "clientOrderId": "client_order_id",
                        "timeInForce": "time_in_force",
                        "reduceOnly": "reduce_only",
                        "positionSide": "position_side",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "positionSide": "position_side",
            "clientOrderId": "client_order_id",
            "reduceOnly": "reduce_only",
            "recvWindow": "recv_window",
        }
    )
    async def place_swap_post_only_buy_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        position_side: str = "LONG",
        client_order_id: str | None = None,
        reduce_only: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_swap_post_only_buy_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionSide": "position_side",
                        "clientOrderId": "client_order_id",
                        "reduceOnly": "reduce_only",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "positionSide": "position_side",
            "clientOrderId": "client_order_id",
            "reduceOnly": "reduce_only",
            "recvWindow": "recv_window",
        }
    )
    async def place_swap_post_only_sell_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        position_side: str,
        client_order_id: str | None = None,
        reduce_only: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_swap_post_only_sell_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionSide": "position_side",
                        "clientOrderId": "client_order_id",
                        "reduceOnly": "reduce_only",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords({"batchOrders": "batch_orders", "recvWindow": "recv_window"})
    async def place_swap_batch_order(
        self,
        batch_orders: list,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "place_swap_batch_order",
            self._native_call_params(
                wire_keywords(
                    locals(), {"batchOrders": "batch_orders", "recvWindow": "recv_window"}
                )
            ),
        )

    @legacy_keywords(
        {"orderId": "order_id", "clientOrderId": "client_order_id", "recvWindow": "recv_window"}
    )
    async def cancel_swap_order(
        self,
        product_symbol: str,
        order_id: int | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "cancel_swap_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderId": "order_id",
                        "clientOrderId": "client_order_id",
                        "recvWindow": "recv_window",
                    },
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
    async def cancel_swap_batch_order(
        self,
        product_symbol: str,
        order_id_list: list | None = None,
        client_order_id_list: list | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
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

    @legacy_keywords({"recvWindow": "recv_window"})
    async def cancel_swap_all_orders(
        self,
        product_symbol: str | None = None,
        type_: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "cancel_swap_all_orders",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords(
        {
            "cancelReplaceMode": "cancel_replace_mode",
            "positionSide": "position_side",
            "orderId": "order_id",
            "cancelClientOrderId": "cancel_client_order_id",
            "cancelOrderId": "cancel_order_id",
            "cancelRestrictions": "cancel_restrictions",
            "reduceOnly": "reduce_only",
            "quoteOrderQty": "quote_order_qty",
            "stopPrice": "stop_price",
            "priceRate": "price_rate",
            "workingType": "working_type",
            "stopLoss": "stop_loss",
            "takeProfit": "take_profit",
            "clientOrderId": "client_order_id",
            "closePosition": "close_position",
            "activationPrice": "activation_price",
            "stopGuaranteed": "stop_guaranteed",
            "timeInForce": "time_in_force",
            "positionId": "position_id",
            "recvWindow": "recv_window",
        }
    )
    async def replace_swap_order(
        self,
        product_symbol: str,
        cancel_replace_mode: str,
        type_: str,
        side: str,
        position_side: str,
        order_id: str | None = None,
        cancel_client_order_id: str | None = None,
        cancel_order_id: str | None = None,
        cancel_restrictions: str | None = None,
        reduce_only: str | None = None,
        price: float | None = None,
        quantity: float | None = None,
        quote_order_qty: float | None = None,
        stop_price: float | None = None,
        price_rate: float | None = None,
        working_type: str | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        client_order_id: str | None = None,
        close_position: str | None = None,
        activation_price: float | None = None,
        stop_guaranteed: str | None = None,
        time_in_force: str | None = None,
        position_id: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "replace_swap_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "cancelReplaceMode": "cancel_replace_mode",
                        "positionSide": "position_side",
                        "orderId": "order_id",
                        "cancelClientOrderId": "cancel_client_order_id",
                        "cancelOrderId": "cancel_order_id",
                        "cancelRestrictions": "cancel_restrictions",
                        "reduceOnly": "reduce_only",
                        "quoteOrderQty": "quote_order_qty",
                        "stopPrice": "stop_price",
                        "priceRate": "price_rate",
                        "workingType": "working_type",
                        "stopLoss": "stop_loss",
                        "takeProfit": "take_profit",
                        "clientOrderId": "client_order_id",
                        "closePosition": "close_position",
                        "activationPrice": "activation_price",
                        "stopGuaranteed": "stop_guaranteed",
                        "timeInForce": "time_in_force",
                        "positionId": "position_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords({"positionId": "position_id", "recvWindow": "recv_window"})
    async def close_swap_position(
        self,
        position_id: str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "close_swap_position",
            self._native_call_params(
                wire_keywords(locals(), {"positionId": "position_id", "recvWindow": "recv_window"})
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def close_swap_all_positions(
        self,
        product_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "close_swap_all_positions",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords(
        {"orderId": "order_id", "clientOrderId": "client_order_id", "recvWindow": "recv_window"}
    )
    async def get_order_detail(
        self,
        product_symbol: str,
        order_id: int | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_order_detail",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderId": "order_id",
                        "clientOrderId": "client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_open_orders(
        self,
        product_symbol: str | None = None,
        type_: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_open_orders",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords(
        {
            "orderId": "order_id",
            "startTime": "start_time",
            "endTime": "end_time",
            "recvWindow": "recv_window",
        }
    )
    async def get_order_history(
        self,
        product_symbol: str | None = None,
        currency: str | None = None,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_order_history",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderId": "order_id",
                        "startTime": "start_time",
                        "endTime": "end_time",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords({"marginType": "margin_type", "recvWindow": "recv_window"})
    async def change_margin_type(
        self,
        product_symbol: str,
        margin_type: str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "change_margin_type",
            self._native_call_params(
                wire_keywords(locals(), {"marginType": "margin_type", "recvWindow": "recv_window"})
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_margin_type(
        self,
        product_symbol: str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_margin_type",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def set_leverage(
        self,
        product_symbol: str,
        side: str,
        leverage: int,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "set_leverage",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_leverage(
        self,
        product_symbol: str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_leverage",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords({"dualSidePosition": "dual_side_position", "recvWindow": "recv_window"})
    async def set_position_mode(
        self,
        dual_side_position: str,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "set_position_mode",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {"dualSidePosition": "dual_side_position", "recvWindow": "recv_window"},
                )
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_position_mode(self, recv_window: int | None = None) -> dict[str, Any]:
        return await self._native_private(
            "get_position_mode",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords({"timeOut": "time_out", "recvWindow": "recv_window"})
    async def set_swap_cancel_all_after(
        self, type_: str, time_out: int, *, recv_window: int | None = None
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v2/trade/cancelAllAfter``."""
        return await self._native_private(
            "set_swap_cancel_all_after",
            self._native_call_params(
                wire_keywords(locals(), {"timeOut": "time_out", "recvWindow": "recv_window"})
            ),
        )

    @legacy_keywords(
        {"orderId": "order_id", "clientOrderId": "client_order_id", "recvWindow": "recv_window"}
    )
    async def get_swap_open_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v2/trade/openOrder``."""
        return await self._native_private(
            "get_swap_open_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderId": "order_id",
                        "clientOrderId": "client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "autoCloseType": "auto_close_type",
            "startTime": "start_time",
            "endTime": "end_time",
            "recvWindow": "recv_window",
        }
    )
    async def get_swap_force_orders(
        self,
        *,
        product_symbol: str | None = None,
        currency: str | None = None,
        auto_close_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v2/trade/forceOrders``."""
        return await self._native_private(
            "get_swap_force_orders",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "autoCloseType": "auto_close_type",
                        "startTime": "start_time",
                        "endTime": "end_time",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "tradingUnit": "trading_unit",
            "startTs": "start_ts",
            "endTs": "end_ts",
            "orderId": "order_id",
            "recvWindow": "recv_window",
        }
    )
    async def get_swap_trade_fills(
        self,
        trading_unit: str,
        start_ts: int,
        end_ts: int,
        *,
        order_id: int | None = None,
        currency: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v2/trade/allFillOrders``."""
        return await self._native_private(
            "get_swap_trade_fills",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "tradingUnit": "trading_unit",
                        "startTs": "start_ts",
                        "endTs": "end_ts",
                        "orderId": "order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {"positionSide": "position_side", "positionId": "position_id", "recvWindow": "recv_window"}
    )
    async def adjust_swap_position_margin(
        self,
        product_symbol: str,
        amount: str,
        type_: int,
        *,
        position_side: str | None = None,
        position_id: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v2/trade/positionMargin``."""
        return await self._native_private(
            "adjust_swap_position_margin",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionSide": "position_side",
                        "positionId": "position_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {"orderId": "order_id", "clientOrderId": "client_order_id", "recvWindow": "recv_window"}
    )
    async def amend_swap_order(
        self,
        product_symbol: str,
        quantity: str,
        *,
        order_id: str | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v1/trade/amend``."""
        return await self._native_private(
            "amend_swap_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderId": "order_id",
                        "clientOrderId": "client_order_id",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "positionSide": "position_side",
            "priceType": "price_type",
            "priceVariance": "price_variance",
            "triggerPrice": "trigger_price",
            "amountPerOrder": "amount_per_order",
            "totalAmount": "total_amount",
            "recvWindow": "recv_window",
        }
    )
    async def place_swap_twap_order(
        self,
        product_symbol: str,
        side: str,
        position_side: str,
        price_type: str,
        price_variance: str,
        trigger_price: str,
        interval: int,
        amount_per_order: str,
        total_amount: str,
        *,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v1/twap/order``."""
        return await self._native_private(
            "place_swap_twap_order",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionSide": "position_side",
                        "priceType": "price_type",
                        "priceVariance": "price_variance",
                        "triggerPrice": "trigger_price",
                        "amountPerOrder": "amount_per_order",
                        "totalAmount": "total_amount",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords({"mainOrderId": "main_order_id", "recvWindow": "recv_window"})
    async def cancel_swap_twap_order(
        self, main_order_id: str, *, recv_window: int | None = None
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v1/twap/cancelOrder``."""
        return await self._native_private(
            "cancel_swap_twap_order",
            self._native_call_params(
                wire_keywords(
                    locals(), {"mainOrderId": "main_order_id", "recvWindow": "recv_window"}
                )
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_swap_open_twap_orders(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/twap/openOrders``."""
        return await self._native_private(
            "get_swap_open_twap_orders",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords(
        {
            "pageIndex": "page_index",
            "pageSize": "page_size",
            "startTime": "start_time",
            "endTime": "end_time",
            "recvWindow": "recv_window",
        }
    )
    async def get_swap_twap_order_history(
        self,
        page_index: int,
        page_size: int,
        start_time: int,
        end_time: int,
        *,
        product_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/twap/historyOrders``."""
        return await self._native_private(
            "get_swap_twap_order_history",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "pageIndex": "page_index",
                        "pageSize": "page_size",
                        "startTime": "start_time",
                        "endTime": "end_time",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords({"mainOrderId": "main_order_id", "recvWindow": "recv_window"})
    async def get_swap_twap_order(
        self, main_order_id: str, *, recv_window: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/twap/orderDetail``."""
        return await self._native_private(
            "get_swap_twap_order",
            self._native_call_params(
                wire_keywords(
                    locals(), {"mainOrderId": "main_order_id", "recvWindow": "recv_window"}
                )
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_swap_asset_mode(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/trade/assetMode``."""
        return await self._native_private(
            "get_swap_asset_mode",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords({"assetMode": "asset_mode", "recvWindow": "recv_window"})
    async def set_swap_asset_mode(
        self, asset_mode: str, *, recv_window: int | None = None, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Call ``POST /openApi/swap/v1/trade/assetMode``.

        Requires confirm=True. This changes collateral accounting for swaps.
        """
        require_confirmation(confirm)
        return await self._native_private(
            "set_swap_asset_mode",
            self._native_call_params(
                wire_keywords(locals(), {"assetMode": "asset_mode", "recvWindow": "recv_window"})
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_swap_multi_asset_rules(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/trade/multiAssetsRules``."""
        return await self._native_private(
            "get_swap_multi_asset_rules",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_swap_margin_assets(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/user/marginAssets``."""
        return await self._native_private(
            "get_swap_margin_assets",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords(
        {
            "orderId": "order_id",
            "startTime": "start_time",
            "endTime": "end_time",
            "recvWindow": "recv_window",
        }
    )
    async def get_swap_full_orders(
        self,
        limit: int,
        *,
        product_symbol: str | None = None,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/trade/fullOrder``."""
        return await self._native_private(
            "get_swap_full_orders",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "orderId": "order_id",
                        "startTime": "start_time",
                        "endTime": "end_time",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "startTs": "start_ts",
            "endTs": "end_ts",
            "orderId": "order_id",
            "lastFillId": "last_fill_id",
            "pageIndex": "page_index",
            "pageSize": "page_size",
            "recvWindow": "recv_window",
        }
    )
    async def get_swap_fill_history(
        self,
        product_symbol: str,
        start_ts: int,
        end_ts: int,
        *,
        currency: str | None = None,
        order_id: int | None = None,
        last_fill_id: int | None = None,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v2/trade/fillHistory``."""
        return await self._native_private(
            "get_swap_fill_history",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "startTs": "start_ts",
                        "endTs": "end_ts",
                        "orderId": "order_id",
                        "lastFillId": "last_fill_id",
                        "pageIndex": "page_index",
                        "pageSize": "page_size",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "startTs": "start_ts",
            "endTs": "end_ts",
            "positionId": "position_id",
            "pageIndex": "page_index",
            "pageSize": "page_size",
            "recvWindow": "recv_window",
        }
    )
    async def get_swap_position_history(
        self,
        product_symbol: str,
        start_ts: int,
        end_ts: int,
        *,
        currency: str | None = None,
        position_id: int | None = None,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/trade/positionHistory``."""
        return await self._native_private(
            "get_swap_position_history",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "startTs": "start_ts",
                        "endTs": "end_ts",
                        "positionId": "position_id",
                        "pageIndex": "page_index",
                        "pageSize": "page_size",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords(
        {
            "positionId": "position_id",
            "startTime": "start_time",
            "endTime": "end_time",
            "pageIndex": "page_index",
            "pageSize": "page_size",
            "recvWindow": "recv_window",
        }
    )
    async def get_swap_margin_history(
        self,
        product_symbol: str,
        position_id: str,
        start_time: int,
        end_time: int,
        page_index: int,
        page_size: int,
        *,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/positionMargin/history``."""
        return await self._native_private(
            "get_swap_margin_history",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionId": "position_id",
                        "startTime": "start_time",
                        "endTime": "end_time",
                        "pageIndex": "page_index",
                        "pageSize": "page_size",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    @legacy_keywords({"recvWindow": "recv_window"})
    async def get_swap_maintenance_margin_ratios(
        self, product_symbol: str, *, recv_window: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /openApi/swap/v1/maintMarginRatio``."""
        return await self._native_private(
            "get_swap_maintenance_margin_ratios",
            self._native_call_params(wire_keywords(locals(), {"recvWindow": "recv_window"})),
        )

    @legacy_keywords(
        {
            "positionId": "position_id",
            "functionSwitch": "function_switch",
            "recvWindow": "recv_window",
        }
    )
    async def set_swap_auto_add_margin(
        self,
        product_symbol: str,
        position_id: int,
        function_switch: str,
        *,
        amount: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /openApi/swap/v1/trade/autoAddMargin``."""
        return await self._native_private(
            "set_swap_auto_add_margin",
            self._native_call_params(
                wire_keywords(
                    locals(),
                    {
                        "positionId": "position_id",
                        "functionSwitch": "function_switch",
                        "recvWindow": "recv_window",
                    },
                )
            ),
        )

    async def place_coin_swap_order(
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
        return await self._native_private(
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

    async def cancel_coin_swap_order(
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
        return await self._native_private(
            "cancel_coin_swap_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=order_id,
                clientOrderId=client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def cancel_coin_swap_all_orders(
        self,
        *,
        product_symbol: str | None = None,
        recv_window: int | None = None,
        all_symbols: bool = False,
    ) -> dict[str, Any]:
        """

        POST /openApi/cswap/v1/trade/allOpenOrders.

        Provide product_symbol, or all_symbols=True to cancel Coin-M orders across all symbols.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        require_scope(product_symbol, all_symbols)
        return await self._native_private(
            "cancel_coin_swap_all_orders",
            self._native_params(
                all_symbols=all_symbols, product_symbol=product_symbol, recvWindow=recv_window
            ),
        )

    async def close_coin_swap_all_positions(
        self,
        *,
        product_symbol: str | None = None,
        recv_window: int | None = None,
        all_symbols: bool = False,
    ) -> dict[str, Any]:
        """

        POST /openApi/cswap/v1/trade/closeAllPositions.

        Provide product_symbol, or all_symbols=True to close Coin-M positions across all symbols.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        require_scope(product_symbol, all_symbols)
        return await self._native_private(
            "close_coin_swap_all_positions",
            self._native_params(
                all_symbols=all_symbols, product_symbol=product_symbol, recvWindow=recv_window
            ),
        )

    async def get_coin_swap_open_orders(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/trade/openOrders.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return await self._native_private(
            "get_coin_swap_open_orders",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def get_coin_swap_order(
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
        return await self._native_private(
            "get_coin_swap_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=order_id,
                clientOrderId=client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def get_coin_swap_order_history(
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
        return await self._native_private(
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

    async def get_coin_swap_fills(
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
        return await self._native_private(
            "get_coin_swap_fills",
            self._native_params(
                orderId=order_id, pageIndex=page_index, pageSize=page_size, recvWindow=recv_window
            ),
        )

    async def get_coin_swap_force_orders(
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
        return await self._native_private(
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

    async def get_coin_swap_leverage(
        self, *, product_symbol: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/trade/leverage.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return await self._native_private(
            "get_coin_swap_leverage",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def set_coin_swap_leverage(
        self, *, product_symbol: str, side: str, leverage: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        POST /openApi/cswap/v1/trade/leverage.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return await self._native_private(
            "set_coin_swap_leverage",
            self._native_params(
                product_symbol=product_symbol, side=side, leverage=leverage, recvWindow=recv_window
            ),
        )

    async def get_coin_swap_margin_type(
        self, *, product_symbol: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/trade/marginType.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return await self._native_private(
            "get_coin_swap_margin_type",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def set_coin_swap_margin_type(
        self, *, product_symbol: str, margin_type: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        POST /openApi/cswap/v1/trade/marginType.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return await self._native_private(
            "set_coin_swap_margin_type",
            self._native_params(
                product_symbol=product_symbol, marginType=margin_type, recvWindow=recv_window
            ),
        )

    async def adjust_coin_swap_position_margin(
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
        return await self._native_private(
            "adjust_coin_swap_position_margin",
            self._native_params(
                product_symbol=product_symbol,
                positionSide=position_side,
                amount=amount,
                type_=type_,
                recvWindow=recv_window,
            ),
        )

    async def get_coin_swap_commission_rate(
        self, *, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/user/commissionRate.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return await self._native_private(
            "get_coin_swap_commission_rate", self._native_params(recvWindow=recv_window)
        )

    async def get_coin_swap_balance(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/user/balance.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return await self._native_private(
            "get_coin_swap_balance",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def get_coin_swap_positions(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/user/positions.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-trade/api-reference.md

        """
        return await self._native_private(
            "get_coin_swap_positions",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def place_spot_oco(
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
        return await self._native_private(
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

    async def cancel_spot_oco(
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
        return await self._native_private(
            "cancel_spot_oco",
            self._native_params(
                orderId=order_id, clientOrderId=client_order_id, recvWindow=recv_window
            ),
        )

    async def get_spot_oco(
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
        return await self._native_private(
            "get_spot_oco",
            self._native_params(
                orderListId=order_list_id, clientOrderId=client_order_id, recvWindow=recv_window
            ),
        )

    async def get_spot_open_oco(
        self, *, page_index: int, page_size: int, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/spot/v1/oco/openOrderList.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/spot-trade/api-reference.md

        """
        return await self._native_private(
            "get_spot_open_oco",
            self._native_params(pageIndex=page_index, pageSize=page_size, recvWindow=recv_window),
        )

    async def get_spot_oco_history(
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
        return await self._native_private(
            "get_spot_oco_history",
            self._native_params(
                pageIndex=page_index,
                pageSize=page_size,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    async def get_deposit_history(
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
        return await self._native_private(
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

    async def replace_swap_batch_orders(
        self, orders: list[dict[str, Any]], *, recv_window: int | None = None
    ) -> dict[str, Any]:
        """
        Cancel and replace multiple swap orders; preserve per-order failure results.

        Orders accept the native cancelReplace fields and product_symbol.
        """
        return await self._native_private(
            "replace_swap_batch_orders",
            self._native_params(batchOrders=orders, recvWindow=recv_window),
        )

    async def get_coin_network_config(
        self,
        *,
        coin: str | None = None,
        display_name: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """GET /openApi/wallets/v1/capital/config/getall. Timestamps use milliseconds."""
        return await self._native_private(
            "get_coin_network_config",
            self._native_params(coin=coin, displayName=display_name, recvWindow=recv_window),
        )

    async def get_deposit_addresses(
        self,
        *,
        coin: str,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """GET /openApi/wallets/v1/capital/deposit/address. Timestamps use milliseconds."""
        return await self._native_private(
            "get_deposit_addresses",
            self._native_params(coin=coin, offset=offset, limit=limit, recvWindow=recv_window),
        )

    async def get_deposit_risk_records(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """GET /openApi/wallets/v1/capital/deposit/riskRecords. Timestamps use milliseconds."""
        return await self._native_private(
            "get_deposit_risk_records", self._native_params(recvWindow=recv_window)
        )

    async def reverse_swap_position(
        self,
        *,
        type_: str,
        product_symbol: str,
        trigger_price: str | None = None,
        working_type: str | None = None,
        recv_window: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """
        POST /openApi/swap/v1/trade/reverse. Timestamps use milliseconds.

        Requires confirm=True. This closes and reverses the selected position.
        """
        require_confirmation(confirm)
        return await self._native_private(
            "reverse_swap_position",
            self._native_params(
                confirm=confirm,
                type_=type_,
                product_symbol=product_symbol,
                triggerPrice=trigger_price,
                workingType=working_type,
                recvWindow=recv_window,
            ),
        )

    async def adjust_simulated_trading_balance(
        self,
        *,
        adjust_type: str | None = None,
        amount: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """POST /openApi/swap/v2/trade/getVst. Timestamps use milliseconds."""
        return await self._native_private(
            "adjust_simulated_trading_balance",
            self._native_params(adjustType=adjust_type, amount=amount, recvWindow=recv_window),
        )

    async def get_standard_futures_positions(
        self, *, recv_window: int | None = None
    ) -> dict[str, Any]:
        """GET /openApi/contract/v1/allPosition. Timestamps use milliseconds."""
        return await self._native_private(
            "get_standard_futures_positions", self._native_params(recvWindow=recv_window)
        )

    async def get_standard_futures_orders(
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
        return await self._native_private(
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

    async def get_standard_futures_balance(
        self, *, recv_window: int | None = None
    ) -> dict[str, Any]:
        """GET /openApi/contract/v1/balance. Timestamps use milliseconds."""
        return await self._native_private(
            "get_standard_futures_balance", self._native_params(recvWindow=recv_window)
        )

    async def get_api_permissions(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """GET /openApi/v1/account/apiPermissions. Timestamps use milliseconds."""
        return await self._native_private(
            "get_api_permissions", self._native_params(recvWindow=recv_window)
        )

    async def create_sub_account(
        self, *, sub_account_string: str, note: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """POST /openApi/subAccount/v1/create. Timestamps use milliseconds."""
        return await self._native_private(
            "create_sub_account",
            self._native_params(
                subAccountString=sub_account_string, note=note, recvWindow=recv_window
            ),
        )

    async def set_sub_account_frozen(
        self, *, sub_uid: int, freeze: bool, recv_window: int | None = None
    ) -> dict[str, Any]:
        """POST /openApi/subAccount/v1/updateStatus. Timestamps use milliseconds."""
        return await self._native_private(
            "set_sub_account_frozen",
            self._native_params(subUid=sub_uid, freeze=freeze, recvWindow=recv_window),
        )

    async def create_sub_account_api_key(
        self,
        *,
        sub_uid: int,
        note: str,
        permissions: list[int],
        ip_addresses: list[str] | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """POST /openApi/subAccount/v1/apiKey/create. Timestamps use milliseconds."""
        return await self._native_private(
            "create_sub_account_api_key",
            self._native_params(
                subUid=sub_uid,
                note=note,
                permissions=permissions,
                ipAddresses=ip_addresses,
                recvWindow=recv_window,
            ),
        )

    async def modify_sub_account_api_key(
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
        return await self._native_private(
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

    async def delete_sub_account_api_key(
        self, *, sub_uid: int, api_key: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """POST /openApi/subAccount/v1/apiKey/del. Timestamps use milliseconds."""
        return await self._native_private(
            "delete_sub_account_api_key",
            self._native_params(subUid=sub_uid, apiKey=api_key, recvWindow=recv_window),
        )

    async def set_sub_account_transfer_authorization(
        self, *, sub_uids: str, transferable: bool, recv_window: int | None = None
    ) -> dict[str, Any]:
        """
        POST /openApi/account/v1/innerTransfer/authorizeSubAccount. Timestamps use milliseconds.
        """
        return await self._native_private(
            "set_sub_account_transfer_authorization",
            self._native_params(
                subUids=sub_uids, transferable=transferable, recvWindow=recv_window
            ),
        )

    async def get_sub_account_deposit_addresses(
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
        return await self._native_private(
            "get_sub_account_deposit_addresses",
            self._native_params(
                coin=coin, subUid=sub_uid, offset=offset, limit=limit, recvWindow=recv_window
            ),
        )

    async def get_sub_account_deposit_history(
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
        return await self._native_private(
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

    async def get_api_restrictions(self, *, recv_window: int | None = None) -> dict[str, Any]:
        """GET /openApi/v1/account/apiRestrictions. Timestamps use milliseconds."""
        return await self._native_private(
            "get_api_restrictions", self._native_params(recvWindow=recv_window)
        )

    async def create_sub_account_deposit_address(
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
        return await self._native_private(
            "create_sub_account_deposit_address",
            self._native_params(
                coin=coin,
                subUid=sub_uid,
                network=network,
                walletType=wallet_type,
                recvWindow=recv_window,
            ),
        )

    async def export_swap_income(
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
        return await self._native_client.export_swap_income_async(
            self._native_params(
                product_symbol=product_symbol,
                incomeType=income_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            )
        )

    async def get_withdrawal_history(
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
        return await self._native_private(
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

    async def get_internal_transfer_records(
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
        return await self._native_private(
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

    async def get_sub_account_internal_transfer_records(
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
        return await self._native_private(
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

    async def transfer_master_internal(
        self,
        *,
        coin: str,
        user_account_type: int,
        user_account: str,
        amount: str,
        calling_code: str | None = None,
        wallet_type: int,
        transfer_client_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /openApi/wallets/v1/capital/innerTransfer/apply.

        The English and Chinese docs disagree on the spot walletType code (4/15).
        This wrapper preserves the caller-selected integer without choosing either.
        Source: https://bingx-api.github.io/docs-v3/


        The recipient is a different user. API transfers have no second confirmation;
        they execute on submit. Verify the recipient UID, email, or phone first.
        """
        return await self._native_private(
            "transfer_master_internal",
            self._native_params(
                **{
                    "coin": coin,
                    "userAccountType": user_account_type,
                    "userAccount": user_account,
                    "amount": amount,
                    "callingCode": calling_code,
                    "walletType": wallet_type,
                    "transferClientId": transfer_client_id,
                    "recvWindow": recv_window,
                }
            ),
        )

    async def transfer_sub_account_internal(
        self,
        *,
        coin: str,
        user_account_type: int,
        user_account: str,
        amount: str,
        calling_code: str | None = None,
        wallet_type: int,
        transfer_client_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /openApi/wallets/v1/capital/subAccountInnerTransfer/apply.

        Sub-account-only operation; uses a signed JSON body.
        Source: https://bingx-api.github.io/docs-v3/
        """
        return await self._native_private(
            "transfer_sub_account_internal",
            self._native_params(
                **{
                    "coin": coin,
                    "userAccountType": user_account_type,
                    "userAccount": user_account,
                    "amount": amount,
                    "callingCode": calling_code,
                    "walletType": wallet_type,
                    "transferClientId": transfer_client_id,
                    "recvWindow": recv_window,
                }
            ),
        )

    async def create_withdrawal(
        self,
        *,
        coin: str,
        network: str | None = None,
        address: str,
        address_tag: str | None = None,
        amount: str,
        wallet_type: int,
        withdraw_order_id: str | None = None,
        vasp_entity_id: str | None = None,
        recipient_last_name: str | None = None,
        recipient_first_name: str | None = None,
        date_ofbirth: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /openApi/wallets/v1/capital/withdraw/apply.

        API withdrawals have no second confirmation; they execute on submit.
        Supply destination-specific memo and required Travel Rule information.
        The English and Chinese docs disagree on the spot walletType code (4/15).
        This wrapper preserves the caller-selected integer without choosing either.
        Source: https://bingx-api.github.io/docs-v3/
        """
        return await self._native_private(
            "create_withdrawal",
            self._native_params(
                **{
                    "coin": coin,
                    "network": network,
                    "address": address,
                    "addressTag": address_tag,
                    "amount": amount,
                    "walletType": wallet_type,
                    "withdrawOrderId": withdraw_order_id,
                    "vaspEntityId": vasp_entity_id,
                    "recipientLastName": recipient_last_name,
                    "recipientFirstName": recipient_first_name,
                    "dateOfbirth": date_ofbirth,
                    "recvWindow": recv_window,
                }
            ),
        )
