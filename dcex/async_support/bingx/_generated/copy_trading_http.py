"""Generated bingx copy trading HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedCopyTradingHTTP(MarketHTTP):
    """Copy trading API methods."""

    async def post_copy_trading_v1_swap_trace_set_tpsl(
        self,
        *,
        position_id: int,
        take_profit_mark_price: str,
        stop_loss_mark_price: str,
        recv_window: int,
    ) -> Any:  # noqa: ANN401
        """Traders set take profit and stop loss based on order numbers.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Traders%20set%20take%20profit%20and%20stop%20loss%20based%20on%20order%20numbers
        """
        return await self._native_private(
            "post_copy_trading_v1_swap_trace_set_tpsl",
            self._native_params(
                **{
                    "positionId": position_id,
                    "takeProfitMarkPrice": take_profit_mark_price,
                    "stopLossMarkPrice": stop_loss_mark_price,
                    "recvWindow": recv_window,
                }
            ),
        )

    async def get_copy_trading_v1_p_futures_trading_pairs(self, *, contract_type: str) -> Any:  # noqa: ANN401
        """Trader Gets Copy Trading Pairs.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Trader%20Gets%20Copy%20Trading%20Pairs
        """
        return await self._native_private(
            "get_copy_trading_v1_p_futures_trading_pairs",
            self._native_params(**{"contractType": contract_type}),
        )

    async def get_copy_trading_v1_p_futures_profit_history_summarys(self) -> Any:  # noqa: ANN401
        """Profit Overview.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Profit%20Overview
        """
        return await self._native_private(
            "get_copy_trading_v1_p_futures_profit_history_summarys", self._native_params(**{})
        )

    async def get_copy_trading_v1_p_futures_profit_detail(
        self,
        *,
        page_index: int,
        page_size: int,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Profit Details.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Profit%20Details
        """
        return await self._native_private(
            "get_copy_trading_v1_p_futures_profit_detail",
            self._native_params(
                **{
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    async def get_copy_trading_v1_p_futures_trader_detail(
        self, *, day_size: int | None = None
    ) -> Any:  # noqa: ANN401
        """Personal Trading Overview.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Personal%20Trading%20Overview
        """
        return await self._native_private(
            "get_copy_trading_v1_p_futures_trader_detail",
            self._native_params(**{"daySize": day_size}),
        )

    async def get_copy_trading_v1_spot_trader_detail(
        self, *, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """Personal Trading Overview.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/Spot%20Trading/Personal%20Trading%20Overview
        """
        return await self._native_private(
            "get_copy_trading_v1_spot_trader_detail",
            self._native_params(**{"recvWindow": recv_window}),
        )

    async def get_copy_trading_v1_spot_profit_detail(
        self,
        *,
        page_index: int,
        page_size: int,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Profit Details.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/Spot%20Trading/Profit%20Details
        """
        return await self._native_private(
            "get_copy_trading_v1_spot_profit_detail",
            self._native_params(
                **{
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    async def get_copy_trading_v1_spot_history_order(
        self,
        *,
        page_index: int,
        page_size: int,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Query Historical Orders.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/Spot%20Trading/Query%20Historical%20Orders
        """
        return await self._native_private(
            "get_copy_trading_v1_spot_history_order",
            self._native_params(
                **{
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "symbol": symbol,
                    "startTime": start_time,
                    "endTime": end_time,
                    "recvWindow": recv_window,
                }
            ),
        )

    async def post_copy_trading_v1_spot_trader_sell_order(self, *, order_id: int) -> Any:  # noqa: ANN401
        """Trader sells spot assets based on buy order number.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/Spot%20Trading/Trader%20sells%20spot%20assets%20based%20on%20buy%20order%20number
        """
        return await self._native_private(
            "post_copy_trading_v1_spot_trader_sell_order",
            self._native_params(**{"orderId": order_id}),
        )

    async def post_copy_trading_v1_p_futures_set_commission(self, *, new_commission: str) -> Any:  # noqa: ANN401
        """Set Commission Rate.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Set%20Commission%20Rate
        """
        return await self._native_private(
            "post_copy_trading_v1_p_futures_set_commission",
            self._native_params(**{"newCommission": new_commission}),
        )

    async def get_copy_trading_v1_spot_profit_history_summarys(self) -> Any:  # noqa: ANN401
        """Profit Summary.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/Spot%20Trading/Profit%20Summary
        """
        return await self._native_private(
            "get_copy_trading_v1_spot_profit_history_summarys", self._native_params(**{})
        )

    async def get_copy_trading_v1_swap_trace_current_track(
        self, *, symbol: str, offset: int | None = None, limit: int | None = None
    ) -> Any:  # noqa: ANN401
        """1. Trader's Current Orders.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/copytrade-swap/api-reference.md#L16
        """
        return await self._native_private(
            "get_copy_trading_v1_swap_trace_current_track",
            self._native_params(**{"symbol": symbol, "offset": offset, "limit": limit}),
        )

    async def post_copy_trading_v1_swap_trace_close_track_order(self, *, position_id: int) -> Any:  # noqa: ANN401
        """2. Close Position by Order Number.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/copytrade-swap/api-reference.md#L91
        """
        return await self._native_private(
            "post_copy_trading_v1_swap_trace_close_track_order",
            self._native_params(**{"positionId": position_id}),
        )
