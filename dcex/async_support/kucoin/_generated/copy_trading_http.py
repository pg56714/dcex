"""Generated kucoin copy trading HTTP methods."""

from typing import Any

from .._trade_http import TradeHTTP


class GeneratedCopyTradingHTTP(TradeHTTP):
    """Copy trading API methods."""

    async def post_v1_copy_trade_futures_orders(
        self,
        *,
        client_oid: str,
        side: str,
        symbol: str,
        leverage: int | None = None,
        type_: str,
        stop: str | None = None,
        stop_price_type: str | None = None,
        stop_price: str | None = None,
        reduce_only: bool | None = None,
        close_order: bool | None = None,
        margin_mode: str | None = None,
        price: str | None = None,
        size: int,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        position_side: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Add Order.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/add-order
        """
        return await self._native_private(
            "post_v1_copy_trade_futures_orders",
            self._native_params(
                clientOid=client_oid,
                side=side,
                symbol=symbol,
                leverage=leverage,
                type=type_,
                stop=stop,
                stopPriceType=stop_price_type,
                stopPrice=stop_price,
                reduceOnly=reduce_only,
                closeOrder=close_order,
                marginMode=margin_mode,
                price=price,
                size=size,
                timeInForce=time_in_force,
                postOnly=post_only,
                positionSide=position_side,
            ),
        )

    async def post_v1_copy_trade_futures_orders_test(
        self,
        *,
        client_oid: str,
        side: str,
        symbol: str,
        leverage: int,
        type_: str,
        stop: str | None = None,
        stop_price_type: str | None = None,
        stop_price: str | None = None,
        reduce_only: bool | None = None,
        close_order: bool | None = None,
        margin_mode: str | None = None,
        price: str | None = None,
        size: int,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        position_side: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Add Order Test.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/add-order-test
        """
        return await self._native_private(
            "post_v1_copy_trade_futures_orders_test",
            self._native_params(
                clientOid=client_oid,
                side=side,
                symbol=symbol,
                leverage=leverage,
                type=type_,
                stop=stop,
                stopPriceType=stop_price_type,
                stopPrice=stop_price,
                reduceOnly=reduce_only,
                closeOrder=close_order,
                marginMode=margin_mode,
                price=price,
                size=size,
                timeInForce=time_in_force,
                postOnly=post_only,
                positionSide=position_side,
            ),
        )

    async def post_v1_copy_trade_futures_st_orders(
        self,
        *,
        client_oid: str,
        side: str,
        symbol: str,
        leverage: int,
        type_: str,
        stop_price_type: str | None = None,
        reduce_only: bool | None = None,
        close_order: bool | None = None,
        margin_mode: str | None = None,
        price: str | None = None,
        size: int,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        trigger_stop_up_price: str | None = None,
        trigger_stop_down_price: str | None = None,
        position_side: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Add Take Profit And Stop Loss Order.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/add-take-profit-and-stop-loss-order
        """
        return await self._native_private(
            "post_v1_copy_trade_futures_st_orders",
            self._native_params(
                clientOid=client_oid,
                side=side,
                symbol=symbol,
                leverage=leverage,
                type=type_,
                stopPriceType=stop_price_type,
                reduceOnly=reduce_only,
                closeOrder=close_order,
                marginMode=margin_mode,
                price=price,
                size=size,
                timeInForce=time_in_force,
                postOnly=post_only,
                triggerStopUpPrice=trigger_stop_up_price,
                triggerStopDownPrice=trigger_stop_down_price,
                positionSide=position_side,
            ),
        )

    async def delete_v1_copy_trade_futures_orders(self, *, order_id: str | None = None) -> Any:  # noqa: ANN401
        """
        Cancel Order By OrderId.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/cancel-order-by-orderid
        """
        return await self._native_private(
            "delete_v1_copy_trade_futures_orders", self._native_params(orderId=order_id)
        )

    async def delete_v1_copy_trade_futures_orders_client_order(
        self, *, symbol: str, client_oid: str
    ) -> Any:  # noqa: ANN401
        """
        Cancel Order By ClientOid.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/cancel-order-by-clientoid
        """
        return await self._native_private(
            "delete_v1_copy_trade_futures_orders_client_order",
            self._native_params(symbol=symbol, clientOid=client_oid),
        )

    async def get_v1_copy_trade_futures_get_max_open_size(
        self, *, symbol: str, price: str, leverage: int
    ) -> Any:  # noqa: ANN401
        """
        Get Max Open Size.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/get-max-open-size
        """
        return await self._native_private(
            "get_v1_copy_trade_futures_get_max_open_size",
            self._native_params(symbol=symbol, price=price, leverage=leverage),
        )

    async def get_v1_copy_trade_futures_position_margin_max_withdraw_margin(
        self, *, symbol: str, position_side: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Max Withdraw Margin.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/get-max-withdraw-margin
        """
        return await self._native_private(
            "get_v1_copy_trade_futures_position_margin_max_withdraw_margin",
            self._native_params(symbol=symbol, positionSide=position_side),
        )

    async def post_v1_copy_trade_futures_position_margin_deposit_margin(
        self, *, symbol: str, margin: str, biz_no: str, position_side: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Add Isolated Margin.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/add-isolated-margin
        """
        return await self._native_private(
            "post_v1_copy_trade_futures_position_margin_deposit_margin",
            self._native_params(
                symbol=symbol, margin=margin, bizNo=biz_no, positionSide=position_side
            ),
        )

    async def post_v1_copy_trade_futures_position_margin_withdraw_margin(
        self, *, symbol: str, withdraw_amount: str, position_side: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Remove Isolated Margin.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/remove-isolated-margin
        """
        return await self._native_private(
            "post_v1_copy_trade_futures_position_margin_withdraw_margin",
            self._native_params(
                symbol=symbol, withdrawAmount=withdraw_amount, positionSide=position_side
            ),
        )

    async def post_v1_copy_trade_futures_position_risk_limit_level_change(
        self, *, symbol: str, level: int
    ) -> Any:  # noqa: ANN401
        """
        Modify Isolated Margin Risk Limit.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/modify-isolated-margin-risk-limit
        """
        return await self._native_private(
            "post_v1_copy_trade_futures_position_risk_limit_level_change",
            self._native_params(symbol=symbol, level=level),
        )

    async def post_v1_copy_trade_futures_position_margin_auto_deposit_status(
        self, *, symbol: str, status: bool, position_side: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Modify Isolated Margin Auto-Deposit Status.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/modify-isolated-margin-auto-deposit-status
        """
        return await self._native_private(
            "post_v1_copy_trade_futures_position_margin_auto_deposit_status",
            self._native_params(symbol=symbol, status=status, positionSide=position_side),
        )

    async def post_v1_copy_trade_futures_position_change_margin_mode(
        self, *, symbol: str, margin_mode: str
    ) -> Any:  # noqa: ANN401
        """
        Switch Margin Mode.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/switch-margin-mode
        """
        return await self._native_private(
            "post_v1_copy_trade_futures_position_change_margin_mode",
            self._native_params(symbol=symbol, marginMode=margin_mode),
        )

    async def post_v2_copy_trade_futures_change_cross_user_leverage(
        self, *, symbol: str, leverage: str
    ) -> Any:  # noqa: ANN401
        """
        Modify Cross Margin Leverage.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/modify-cross-margin-leverage
        """
        return await self._native_private(
            "post_v2_copy_trade_futures_change_cross_user_leverage",
            self._native_params(symbol=symbol, leverage=leverage),
        )

    async def post_v2_copy_trade_get_cross_mode_margin_requirement(
        self, *, symbol: str, leverage: str, position_value: str
    ) -> Any:  # noqa: ANN401
        """
        Get Cross Margin Requirement.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/get-cross-margin-requirement
        """
        return await self._native_private(
            "post_v2_copy_trade_get_cross_mode_margin_requirement",
            self._native_params(symbol=symbol, leverage=leverage, positionValue=position_value),
        )

    async def post_v2_copy_trade_position_switch_position_mode(self, *, position_mode: str) -> Any:  # noqa: ANN401
        """
        Switch Position Mode.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/switch-position-mode
        """
        return await self._native_private(
            "post_v2_copy_trade_position_switch_position_mode",
            self._native_params(positionMode=position_mode),
        )
