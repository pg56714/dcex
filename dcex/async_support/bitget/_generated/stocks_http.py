"""Generated bitget stocks HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedStocksHTTP(MarketHTTP):
    """Stocks API methods."""

    async def stock_plus_assets_get_account(self, *, currency: str | None = None) -> dict[str, Any]:
        """
        Check Account.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/assets#check-account
        """
        return await self._native_private(
            "stock_plus_assets_get_account", self._native_params(**{"currency": currency})
        )

    async def stock_plus_assets_get_cash_flow(
        self,
        *,
        start_time: int | float,
        end_time: int | float,
        business_type: str | None = None,
        symbol: str | None = None,
        page: int | float | None = None,
        size: int | float | None = None,
    ) -> dict[str, Any]:
        """
        Check Cash Flow.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/assets#check-cash-flow
        """
        return await self._native_private(
            "stock_plus_assets_get_cash_flow",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "businessType": business_type,
                    "symbol": symbol,
                    "page": page,
                    "size": size,
                }
            ),
        )

    async def stock_plus_assets_get_stock_position(
        self, *, symbol: str | None = None
    ) -> dict[str, Any]:
        """
        Check Stock Position.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/assets#check-stock-position
        """
        return await self._native_private(
            "stock_plus_assets_get_stock_position", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_options_quotes_get_option_quote(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Option Real-time Quote.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/options-quotes#get-option-quote
        """
        return await self._native_private(
            "stock_plus_options_quotes_get_option_quote", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_options_quotes_get_option_chain_info(
        self, *, symbol: str, expiry_date: str
    ) -> dict[str, Any]:
        """
        Check Option Chain.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/options-quotes#get-option-chain-info
        """
        return await self._native_private(
            "stock_plus_options_quotes_get_option_chain_info",
            self._native_params(**{"symbol": symbol, "expiryDate": expiry_date}),
        )

    async def stock_plus_options_quotes_get_option_expiry_date(
        self, *, symbol: str
    ) -> dict[str, Any]:
        """
        Check Option Expiry Date List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/options-quotes#get-option-expiry-date
        """
        return await self._native_private(
            "stock_plus_options_quotes_get_option_expiry_date",
            self._native_params(**{"symbol": symbol}),
        )

    async def stock_plus_options_quotes_get_option_volume(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Option Volume.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/options-quotes#get-option-volume
        """
        return await self._native_private(
            "stock_plus_options_quotes_get_option_volume", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_orders_place_order(
        self,
        *,
        symbol: str,
        order_type: str,
        side: str,
        submitted_quantity: str,
        time_in_force: str,
        submitted_price: str | None = None,
        trigger_price: str | None = None,
        limit_offset: str | None = None,
        trailing_amount: str | None = None,
        trailing_percent: str | None = None,
        expire_date: str | None = None,
        outside_rth: str | None = None,
        limit_depth_level: int | float | None = None,
        trigger_count: int | float | None = None,
        monitor_price: str | None = None,
        remark: str | None = None,
    ) -> dict[str, Any]:
        """
        Place Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#place-order
        """
        return await self._native_private(
            "stock_plus_orders_place_order",
            self._native_params(
                **{
                    "symbol": symbol,
                    "orderType": order_type,
                    "side": side,
                    "submittedQuantity": submitted_quantity,
                    "timeInForce": time_in_force,
                    "submittedPrice": submitted_price,
                    "triggerPrice": trigger_price,
                    "limitOffset": limit_offset,
                    "trailingAmount": trailing_amount,
                    "trailingPercent": trailing_percent,
                    "expireDate": expire_date,
                    "outsideRth": outside_rth,
                    "limitDepthLevel": limit_depth_level,
                    "triggerCount": trigger_count,
                    "monitorPrice": monitor_price,
                    "remark": remark,
                }
            ),
        )

    async def stock_plus_orders_modify_order(
        self,
        *,
        order_id: str,
        quantity: str,
        price: str | None = None,
        trigger_price: str | None = None,
        limit_offset: str | None = None,
        trailing_amount: str | None = None,
        trailing_percent: str | None = None,
        limit_depth_level: int | float | None = None,
        trigger_count: int | float | None = None,
        monitor_price: str | None = None,
        remark: str | None = None,
    ) -> dict[str, Any]:
        """
        Modify Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#modify-order
        """
        return await self._native_private(
            "stock_plus_orders_modify_order",
            self._native_params(
                **{
                    "orderId": order_id,
                    "quantity": quantity,
                    "price": price,
                    "triggerPrice": trigger_price,
                    "limitOffset": limit_offset,
                    "trailingAmount": trailing_amount,
                    "trailingPercent": trailing_percent,
                    "limitDepthLevel": limit_depth_level,
                    "triggerCount": trigger_count,
                    "monitorPrice": monitor_price,
                    "remark": remark,
                }
            ),
        )

    async def stock_plus_orders_cancel_order(
        self, *, symbol: str, order_id: str | None = None, client_oid: str | None = None
    ) -> dict[str, Any]:
        """
        Cancel Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#cancel-order
        """
        return await self._native_private(
            "stock_plus_orders_cancel_order",
            self._native_params(**{"symbol": symbol, "orderId": order_id, "clientOid": client_oid}),
        )

    async def stock_plus_orders_get_today_orders(
        self,
        *,
        symbol: str | None = None,
        status: str | None = None,
        side: str | None = None,
        market: str | None = None,
        order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Check Today Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#check-today-orders
        """
        return await self._native_private(
            "stock_plus_orders_get_today_orders",
            self._native_params(
                **{
                    "symbol": symbol,
                    "status": status,
                    "side": side,
                    "market": market,
                    "orderId": order_id,
                }
            ),
        )

    async def stock_plus_orders_get_history_orders(
        self,
        *,
        symbol: str | None = None,
        status: str | None = None,
        side: str | None = None,
        market: str | None = None,
        start_at: int | float | None = None,
        end_at: int | float | None = None,
    ) -> dict[str, Any]:
        """
        Check History Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#check-history-orders
        """
        return await self._native_private(
            "stock_plus_orders_get_history_orders",
            self._native_params(
                **{
                    "symbol": symbol,
                    "status": status,
                    "side": side,
                    "market": market,
                    "startAt": start_at,
                    "endAt": end_at,
                }
            ),
        )

    async def stock_plus_orders_get_order_detail(self, *, order_id: str) -> dict[str, Any]:
        """
        Check Order Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#check-order-detail
        """
        return await self._native_private(
            "stock_plus_orders_get_order_detail", self._native_params(**{"orderId": order_id})
        )

    async def stock_plus_orders_get_today_executions(
        self, *, symbol: str | None = None, order_id: str | None = None
    ) -> dict[str, Any]:
        """
        Check Today Executions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#check-today-executions
        """
        return await self._native_private(
            "stock_plus_orders_get_today_executions",
            self._native_params(**{"symbol": symbol, "orderId": order_id}),
        )

    async def stock_plus_orders_get_history_executions(
        self,
        *,
        symbol: str | None = None,
        start_at: int | float | None = None,
        end_at: int | float | None = None,
    ) -> dict[str, Any]:
        """
        Check History Executions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#check-history-executions
        """
        return await self._native_private(
            "stock_plus_orders_get_history_executions",
            self._native_params(**{"symbol": symbol, "startAt": start_at, "endAt": end_at}),
        )

    async def stock_plus_stock_quotes_get_static_info(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Basic Information.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-basic-information
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_static_info", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_stock_quotes_get_candlestick(
        self,
        *,
        symbol: str,
        period: str,
        count: int,
        adjust_type: str,
        trade_sessions: str | None = None,
    ) -> dict[str, Any]:
        """
        Check Candlestick.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-candlestick
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_candlestick",
            self._native_params(
                **{
                    "symbol": symbol,
                    "period": period,
                    "count": count,
                    "adjustType": adjust_type,
                    "tradeSessions": trade_sessions,
                }
            ),
        )

    async def stock_plus_stock_quotes_get_history_candlestick(
        self,
        *,
        symbol: str,
        period: str,
        count: int,
        adjust_type: str,
        forward: bool | None = None,
        time: str | None = None,
        trade_sessions: str | None = None,
    ) -> dict[str, Any]:
        """
        Check History Candlestick.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-history-candlestick
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_history_candlestick",
            self._native_params(
                **{
                    "symbol": symbol,
                    "period": period,
                    "count": count,
                    "adjustType": adjust_type,
                    "forward": forward,
                    "time": time,
                    "tradeSessions": trade_sessions,
                }
            ),
        )

    async def stock_plus_stock_quotes_get_depth(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Order Book.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-order-book
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_depth", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_stock_quotes_get_intraday(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Intraday Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-intraday-data
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_intraday", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_stock_quotes_get_quote(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Real-time Quote.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-real-time-quote
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_quote", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_stock_quotes_get_trade_detail(
        self, *, symbol: str, count: int
    ) -> dict[str, Any]:
        """
        Check Trade Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-trade-detail
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_trade_detail",
            self._native_params(**{"symbol": symbol, "count": count}),
        )
