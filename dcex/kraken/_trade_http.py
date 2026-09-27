"""Kraken private trade HTTP client."""

from json import dumps
from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for Kraken private trading operations."""

    def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        ordertype: str,
        volume: str,
        price: str | None = None,
        price2: str | None = None,
        displayvol: str | None = None,
        leverage: str | None = None,
        oflags: str | None = None,
        timeinforce: str | None = None,
        expiretm: str | None = None,
        starttm: str | None = None,
        asset_class: str | None = None,
        trigger: str | None = None,
        stptype: str | None = None,
        reduce_only: bool | None = None,
        userref: int | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
        deadline: str | None = None,
        broker: str | None = None,
        close_ordertype: str | None = None,
        close_price: str | None = None,
        close_price2: str | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot order."""
        if userref is not None and cl_ord_id is not None:
            raise ValueError("userref and cl_ord_id are mutually exclusive.")
        return self._native_private(
            "place_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                ordertype=ordertype,
                volume=volume,
                price=price,
                price2=price2,
                displayvol=displayvol,
                leverage=leverage,
                oflags=oflags,
                timeinforce=timeinforce,
                expiretm=expiretm,
                starttm=starttm,
                asset_class=asset_class,
                trigger=trigger,
                stptype=stptype,
                reduce_only=reduce_only,
                userref=userref,
                cl_ord_id=cl_ord_id,
                validate=validate,
                deadline=deadline,
                broker=broker,
                **{
                    "close[ordertype]": close_ordertype,
                    "close[price]": close_price,
                    "close[price2]": close_price2,
                },
            ),
        )

    def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        volume: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot market order."""
        return self._native_private(
            "place_spot_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                volume=volume,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    def place_spot_market_buy_order(
        self,
        product_symbol: str,
        volume: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot market buy order."""
        return self._native_private(
            "place_spot_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    def place_spot_market_sell_order(
        self,
        product_symbol: str,
        volume: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot market sell order."""
        return self._native_private(
            "place_spot_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        volume: str,
        price: str,
        timeinforce: str | None = None,
        oflags: str | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot limit order."""
        return self._native_private(
            "place_spot_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                volume=volume,
                price=price,
                timeinforce=timeinforce,
                oflags=oflags,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        timeinforce: str | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot limit buy order."""
        return self._native_private(
            "place_spot_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                price=price,
                timeinforce=timeinforce,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        timeinforce: str | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot limit sell order."""
        return self._native_private(
            "place_spot_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                price=price,
                timeinforce=timeinforce,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        volume: str,
        price: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot post-only limit order."""
        return self._native_private(
            "place_spot_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                volume=volume,
                price=price,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot post-only limit buy order."""
        return self._native_private(
            "place_spot_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                price=price,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot post-only limit sell order."""
        return self._native_private(
            "place_spot_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                price=price,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    def get_spot_open_orders(
        self,
        trades: bool | None = None,
        userref: int | None = None,
        cl_ord_id: str | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot open orders."""
        return self._native_private(
            "get_spot_open_orders",
            self._native_params(
                trades=trades,
                userref=userref,
                cl_ord_id=cl_ord_id,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    def get_spot_closed_orders(
        self,
        trades: bool | None = None,
        userref: int | None = None,
        cl_ord_id: str | None = None,
        start: int | str | None = None,
        end: int | str | None = None,
        ofs: int | None = None,
        closetime: str | None = None,
        consolidate_taker: bool | None = None,
        without_count: bool | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot closed orders."""
        return self._native_private(
            "get_spot_closed_orders",
            self._native_params(
                trades=trades,
                userref=userref,
                cl_ord_id=cl_ord_id,
                start=start,
                end=end,
                ofs=ofs,
                closetime=closetime,
                consolidate_taker=consolidate_taker,
                without_count=without_count,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    def get_spot_orders(
        self,
        txid: str,
        trades: bool | None = None,
        userref: int | None = None,
        consolidate_taker: bool | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Query Kraken spot order info by transaction id."""
        return self._native_private(
            "get_spot_orders",
            self._native_params(
                txid=txid,
                trades=trades,
                userref=userref,
                consolidate_taker=consolidate_taker,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    def get_spot_trade_history(
        self,
        type_: str | None = None,
        trades: bool | None = None,
        start: int | str | None = None,
        end: int | str | None = None,
        ofs: int | None = None,
        without_count: bool | None = None,
        consolidate_taker: bool | None = None,
        ledgers: bool | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot trades/fills history."""
        return self._native_private(
            "get_spot_trade_history",
            self._native_params(
                type_=type_,
                trades=trades,
                start=start,
                end=end,
                ofs=ofs,
                without_count=without_count,
                consolidate_taker=consolidate_taker,
                ledgers=ledgers,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    def amend_spot_order(
        self,
        *,
        txid: str | None = None,
        cl_ord_id: str | None = None,
        order_qty: str | None = None,
        display_qty: str | None = None,
        limit_price: str | None = None,
        trigger_price: str | None = None,
        pair: str | None = None,
        post_only: bool | None = None,
        deadline: str | None = None,
    ) -> dict[str, Any]:
        """Amend a spot order in place, retaining its identifier where possible."""
        return self._native_private("amend_spot_order", self._native_params(**locals()))

    def cancel_spot_order(
        self,
        txid: str | None = None,
        userref: int | None = None,
        cl_ord_id: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Kraken spot order."""
        if sum(value is not None for value in (txid, userref, cl_ord_id)) != 1:
            raise ValueError("Specify exactly one of txid, userref, or cl_ord_id.")
        return self._native_private(
            "cancel_spot_order",
            self._native_params(txid=txid, userref=userref, cl_ord_id=cl_ord_id),
        )

    def cancel_spot_all_orders(self) -> dict[str, Any]:
        """Cancel all Kraken spot open orders."""
        return self._native_private("cancel_spot_all_orders", [])

    def cancel_spot_all_orders_after(self, timeout: str) -> dict[str, Any]:
        """Set Kraken's spot cancel-all dead-man switch timeout in seconds."""
        return self._native_private(
            "cancel_spot_all_orders_after", self._native_params(timeout=timeout)
        )

    def get_spot_websocket_token(self) -> dict[str, Any]:
        """Retrieve a Kraken authenticated WebSocket token."""
        return self._native_private("get_spot_websocket_token", [])

    def place_futures_order(
        self,
        product_symbol: str,
        side: str,
        orderType: str,
        size: int | str,
        limitPrice: str | None = None,
        stopPrice: str | None = None,
        cliOrdId: str | None = None,
        triggerSignal: str | None = None,
        reduceOnly: bool | None = None,
        processBefore: str | None = None,
        trailingStopMaxDeviation: str | None = None,
        trailingStopDeviationUnit: str | None = None,
        limitPriceOffsetValue: str | None = None,
        limitPriceOffsetUnit: str | None = None,
        broker: str | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures order."""
        return self._native_private(
            "place_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                orderType=orderType,
                size=size,
                limitPrice=limitPrice,
                stopPrice=stopPrice,
                cliOrdId=cliOrdId,
                triggerSignal=triggerSignal,
                reduceOnly=reduceOnly,
                processBefore=processBefore,
                trailingStopMaxDeviation=trailingStopMaxDeviation,
                trailingStopDeviationUnit=trailingStopDeviationUnit,
                limitPriceOffsetValue=limitPriceOffsetValue,
                limitPriceOffsetUnit=limitPriceOffsetUnit,
                broker=broker,
            ),
        )

    def place_futures_market_order(
        self,
        product_symbol: str,
        side: str,
        size: int | str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures market order."""
        return self._native_private(
            "place_futures_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    def place_futures_market_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures market buy order."""
        return self._native_private(
            "place_futures_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    def place_futures_market_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures market sell order."""
        return self._native_private(
            "place_futures_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    def place_futures_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures limit order."""
        return self._native_private(
            "place_futures_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    def place_futures_limit_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures limit buy order."""
        return self._native_private(
            "place_futures_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    def place_futures_limit_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures limit sell order."""
        return self._native_private(
            "place_futures_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    def place_futures_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures post-only limit order."""
        return self._native_private(
            "place_futures_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    def place_futures_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures post-only limit buy order."""
        return self._native_private(
            "place_futures_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    def place_futures_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures post-only limit sell order."""
        return self._native_private(
            "place_futures_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    def get_futures_open_orders(self) -> dict[str, Any]:
        """Retrieve Kraken Futures open orders."""
        return self._native_private("get_futures_open_orders", [])

    def get_futures_order_status(
        self,
        orderIds: list[str] | None = None,
        cliOrdIds: list[str] | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures order status for specific order IDs."""
        return self._native_private(
            "get_futures_order_status",
            self._native_params(orderIds=orderIds, cliOrdIds=cliOrdIds),
        )

    def edit_futures_order(
        self,
        *,
        orderId: str | None = None,  # noqa: N803
        cliOrdId: str | None = None,  # noqa: N803
        size: int | str | None = None,
        limitPrice: str | None = None,  # noqa: N803
        stopPrice: str | None = None,  # noqa: N803
        trailingStopMaxDeviation: str | None = None,  # noqa: N803
        trailingStopDeviationUnit: str | None = None,  # noqa: N803
        qtyMode: str | None = None,  # noqa: N803
        processBefore: str | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Edit an open Kraken futures order."""
        return self._native_private("edit_futures_order", self._native_params(**locals()))

    def cancel_futures_order(
        self,
        order_id: str | None = None,
        cliOrdId: str | None = None,
        processBefore: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Kraken Futures order."""
        if sum(value is not None for value in (order_id, cliOrdId)) != 1:
            raise ValueError("Specify exactly one of order_id or cliOrdId.")
        return self._native_private(
            "cancel_futures_order",
            self._native_params(
                order_id=order_id,
                cliOrdId=cliOrdId,
                processBefore=processBefore,
            ),
        )

    def cancel_futures_all_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Cancel all Kraken Futures open orders, optionally filtered by product."""
        return self._native_private(
            "cancel_futures_all_orders",
            self._native_params(product_symbol=product_symbol),
        )

    def cancel_futures_all_orders_after(self, timeout: int) -> dict[str, Any]:
        """Cancel all futures orders after timeout seconds; zero disables the timer."""
        return self._native_private(
            "cancel_futures_all_orders_after", self._native_params(timeout=timeout)
        )

    def place_spot_batch_orders(
        self,
        product_symbol: str,
        orders: list[dict[str, Any]],
        *,
        validate: bool | None = None,
        deadline: str | None = None,
        asset_class: str | None = None,
    ) -> dict[str, Any]:
        """Submit 2..15 orders for one pair as a signed JSON batch."""
        return self._native_private(
            "place_spot_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                orders=dumps(orders),
                validate=validate,
                deadline=deadline,
                asset_class=asset_class,
            ),
        )

    def cancel_spot_batch_orders(
        self, *, orders: list[str | int] | None = None, cl_ord_ids: list[str] | None = None
    ) -> dict[str, Any]:
        """Cancel up to 50 txids/userrefs or client order identifiers."""
        return self._native_private(
            "cancel_spot_batch_orders",
            self._native_params(
                orders=dumps(orders) if orders is not None else None,
                cl_ord_ids=dumps(cl_ord_ids) if cl_ord_ids is not None else None,
            ),
        )

    def get_spot_extended_balance(self, *, rebase_multiplier: str | None = None) -> dict[str, Any]:
        """Get balances including credits, used credit and funds held for trading."""
        return self._native_private(
            "get_spot_extended_balance", self._native_params(rebase_multiplier=rebase_multiplier)
        )

    def get_futures_leverage_preferences(self) -> dict[str, Any]:
        """Get configured futures margin and leverage preferences."""
        return self._native_private("get_futures_leverage_preferences", [])

    def set_futures_leverage_preference(
        self, product_symbol: str, *, max_leverage: str | None = None
    ) -> dict[str, Any]:
        """Set isolated margin with max_leverage; omit it to select cross margin."""
        return self._native_private(
            "set_futures_leverage_preference",
            self._native_params(product_symbol=product_symbol, maxLeverage=max_leverage),
        )

    def manage_futures_batch_orders(
        self, orders: list[dict[str, Any]], *, process_before: str | None = None
    ) -> dict[str, Any]:
        """Send, edit or cancel 1 to 500 instructions; price and size fields are JSON numbers."""
        return self._native_private(
            "manage_futures_batch_orders",
            self._native_params(orders=dumps(orders), processBefore=process_before),
        )

    def get_spot_trades_info(
        self, *, txid: str, trades: bool | None = None, rebase_multiplier: str | None = None
    ) -> dict[str, Any]:
        """
        POST /0/private/QueryTrades.

        Source: https://docs.kraken.com/api-reference/account-data/query-trades-info
        """
        return self._native_private(
            "get_spot_trades_info",
            self._native_params(txid=txid, trades=trades, rebase_multiplier=rebase_multiplier),
        )

    def get_futures_account_log_csv(self, *, conversion_details: bool | None = None) -> str:
        """

        GET /api/history/v3/accountlogcsv. Use response headers for the continuation token;
        timestamps are milliseconds.

        Source: https://docs.kraken.com/api-reference/account-history/account-log-csv

        """
        return self._native_private(
            "get_futures_account_log_csv",
            self._native_params(conversion_details=conversion_details),
        )

    def get_futures_account_log(
        self,
        *,
        since: int | None = None,
        before: int | None = None,
        from_account: int | None = None,
        to_account: int | None = None,
        sort: str | None = None,
        info: list[str] | None = None,
        count: int | None = None,
        conversion_details: bool | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/history/v3/account-log. Use response headers for the continuation token;
        timestamps are milliseconds.

        Source: https://docs.kraken.com/api-reference/account-history/get-account-log

        """
        return self._native_private(
            "get_futures_account_log",
            self._native_params(
                since=since,
                before=before,
                to=to_account,
                sort=sort,
                info=dumps(info) if info is not None else None,
                count=count,
                conversion_details=conversion_details,
                **{"from": from_account},
            ),
        )

    def get_futures_execution_events(
        self,
        *,
        since: int | None = None,
        before: int | None = None,
        sort: str | None = None,
        continuation_token: str | None = None,
        count: int | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/history/v3/executions. Use response headers for the continuation token;
        timestamps are milliseconds.

        Source: https://docs.kraken.com/api-reference/account-history/get-execution-events

        """
        return self._native_private(
            "get_futures_execution_events",
            self._native_params(
                since=since,
                before=before,
                sort=sort,
                continuation_token=continuation_token,
                count=count,
                product_symbol=product_symbol,
            ),
        )

    def get_futures_order_events(
        self,
        *,
        since: int | None = None,
        before: int | None = None,
        sort: str | None = None,
        continuation_token: str | None = None,
        count: int | None = None,
        product_symbol: str | None = None,
        opened: bool | None = None,
        closed: bool | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/history/v3/orders. Use response headers for the continuation token; timestamps
        are milliseconds.

        Source: https://docs.kraken.com/api-reference/account-history/get-order-events

        """
        return self._native_private(
            "get_futures_order_events",
            self._native_params(
                since=since,
                before=before,
                sort=sort,
                continuation_token=continuation_token,
                count=count,
                product_symbol=product_symbol,
                opened=opened,
                closed=closed,
            ),
        )

    def get_futures_position_events(
        self,
        *,
        since: int | None = None,
        before: int | None = None,
        sort: str | None = None,
        continuation_token: str | None = None,
        count: int | None = None,
        opened: bool | None = None,
        closed: bool | None = None,
        increased: bool | None = None,
        decreased: bool | None = None,
        reversed: bool | None = None,
        no_change: bool | None = None,
        trades: bool | None = None,
        funding_realization: bool | None = None,
        settlement: bool | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/history/v3/positions. Use response headers for the continuation token;
        timestamps are milliseconds.

        Source: https://docs.kraken.com/api-reference/account-history/get-position-update-events

        """
        return self._native_private(
            "get_futures_position_events",
            self._native_params(
                since=since,
                before=before,
                sort=sort,
                continuation_token=continuation_token,
                count=count,
                opened=opened,
                closed=closed,
                increased=increased,
                decreased=decreased,
                reversed=reversed,
                no_change=no_change,
                trades=trades,
                funding_realization=funding_realization,
                settlement=settlement,
                product_symbol=product_symbol,
            ),
        )

    def get_futures_trigger_events(
        self,
        *,
        since: int | None = None,
        before: int | None = None,
        sort: str | None = None,
        continuation_token: str | None = None,
        count: int | None = None,
        product_symbol: str | None = None,
        opened: bool | None = None,
        closed: bool | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/history/v3/triggers. Use response headers for the continuation token;
        timestamps are milliseconds.

        Source: https://docs.kraken.com/api-reference/account-history/get-trigger-events

        """
        return self._native_private(
            "get_futures_trigger_events",
            self._native_params(
                since=since,
                before=before,
                sort=sort,
                continuation_token=continuation_token,
                count=count,
                product_symbol=product_symbol,
                opened=opened,
                closed=closed,
            ),
        )

    def get_spot_deposit_addresses(
        self,
        *,
        asset: str,
        method: str,
        aclass: str | None = None,
        new_address: bool | None = None,
        amount: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /0/private/DepositAddresses. Legacy funding API: active but no longer updated.

        Source: https://docs.kraken.com/api-reference/funding/get-deposit-addresses
        """
        return self._native_private(
            "get_spot_deposit_addresses",
            self._native_params(
                asset=asset, method=method, aclass=aclass, new=new_address, amount=amount
            ),
        )

    def get_spot_deposit_methods(
        self, *, asset: str, aclass: str | None = None, rebase_multiplier: str | None = None
    ) -> dict[str, Any]:
        """
        POST /0/private/DepositMethods. Legacy funding API: active but no longer updated.

        Source: https://docs.kraken.com/api-reference/funding/get-deposit-methods
        """
        return self._native_private(
            "get_spot_deposit_methods",
            self._native_params(asset=asset, aclass=aclass, rebase_multiplier=rebase_multiplier),
        )

    def transfer_spot_sub_account(
        self,
        *,
        asset: str,
        amount: str,
        from_account: str,
        to_account: str,
        asset_class: str | None = None,
    ) -> dict[str, Any]:
        """

        POST /0/private/AccountTransfer. Master account API key and Kraken subaccount
        eligibility are required.

        Source: https://docs.kraken.com/api-reference/subaccounts/account-transfer

        """
        return self._native_private(
            "transfer_spot_sub_account",
            self._native_params(
                asset=asset,
                amount=amount,
                to=to_account,
                asset_class=asset_class,
                **{"from": from_account},
            ),
        )

    def transfer_futures_sub_account(
        self,
        *,
        from_user: str,
        to_user: str,
        from_account: str,
        to_account: str,
        unit: str,
        amount: str,
    ) -> dict[str, Any]:
        """
        POST /derivatives/api/v3/transfer/subaccount.

        Source: https://docs.kraken.com/api-reference/transfers/initiate-sub-account-transfer
        """
        return self._native_private(
            "transfer_futures_sub_account",
            self._native_params(
                fromUser=from_user,
                toUser=to_user,
                fromAccount=from_account,
                toAccount=to_account,
                unit=unit,
                amount=amount,
            ),
        )

    def get_spot_deposit_status(
        self,
        *,
        asset: str | None = None,
        aclass: str | None = None,
        method: str | None = None,
        start: str | None = None,
        end: str | None = None,
        cursor: str | bool | None = None,
        limit: int | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /0/private/DepositStatus. Legacy funding API: active but no longer updated.

        Source: https://docs.kraken.com/api-reference/funding/get-status-of-recent-deposits
        """
        return self._native_private(
            "get_spot_deposit_status",
            self._native_params(
                asset=asset,
                aclass=aclass,
                method=method,
                start=start,
                end=end,
                cursor=cursor,
                limit=limit,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    def get_spot_level3_orderbook(
        self, *, product_symbol: str, depth: int | None = None
    ) -> dict[str, Any]:
        """
        POST /0/private/Level3.

        Source: https://docs.kraken.com/api-reference/market-data/query-l3-order-book
        """
        return self._native_private(
            "get_spot_level3_orderbook",
            self._native_params(product_symbol=product_symbol, depth=depth),
        )

    def get_spot_api_key_info(self, *, otp: str | None = None) -> dict[str, Any]:
        """
        POST /0/private/GetApiKeyInfo.

        Source: https://docs.kraken.com/api-reference/account-data/get-api-key-info
        """
        return self._native_private("get_spot_api_key_info", self._native_params(otp=otp))

    def get_spot_credit_lines(self, *, rebase_multiplier: str | None = None) -> dict[str, Any]:
        """
        POST /0/private/CreditLines.

        Source: https://docs.kraken.com/api-reference/account-data/get-credit-lines
        """
        return self._native_private(
            "get_spot_credit_lines", self._native_params(rebase_multiplier=rebase_multiplier)
        )

    def get_spot_order_amends(
        self, *, order_id: str | None = None, rebase_multiplier: str | None = None
    ) -> dict[str, Any]:
        """
        POST /0/private/OrderAmends.

        Source: https://docs.kraken.com/api-reference/account-data/get-order-amends
        """
        return self._native_private(
            "get_spot_order_amends",
            self._native_params(order_id=order_id, rebase_multiplier=rebase_multiplier),
        )

    def get_spot_wallet_accounts(self) -> dict[str, Any]:
        """
        POST /0/private/ListWalletAccounts.

        Source: https://docs.kraken.com/api-reference/account-data/list-wallet-accounts
        """
        return self._native_private("get_spot_wallet_accounts", self._native_params())

    def get_spot_ledger_entries(
        self, *, ledger_ids: str, trades: bool | None = None, rebase_multiplier: str | None = None
    ) -> dict[str, Any]:
        """
        POST /0/private/QueryLedgers.

        Source: https://docs.kraken.com/api-reference/account-data/query-ledgers
        """
        return self._native_private(
            "get_spot_ledger_entries",
            self._native_params(id=ledger_ids, trades=trades, rebase_multiplier=rebase_multiplier),
        )

    def get_futures_portfolio_margin_parameters(self) -> dict[str, Any]:
        """

        GET /derivatives/api/v3/portfolio-margining/parameters.

        Source:
        https://docs.kraken.com/api-reference/account-information/get-portfolio-margin-parameters

        """
        return self._native_private(
            "get_futures_portfolio_margin_parameters", self._native_params()
        )

    def get_futures_unwind_queue(self) -> dict[str, Any]:
        """

        GET /derivatives/api/v3/unwindqueue.

        Source:
        https://docs.kraken.com/api-reference/account-information/get-position-percentile-of-unwind-queue

        """
        return self._native_private("get_futures_unwind_queue", self._native_params())

    def get_futures_notifications(self) -> dict[str, Any]:
        """
        GET /derivatives/api/v3/notifications.

        Source: https://docs.kraken.com/api-reference/general/get-notifications
        """
        return self._native_private("get_futures_notifications", self._native_params())

    def get_futures_self_trade_strategy(self) -> dict[str, Any]:
        """
        GET /derivatives/api/v3/self-trade-strategy.

        Source: https://docs.kraken.com/api-reference/trading-settings/get-self-trade-strategy
        """
        return self._native_private("get_futures_self_trade_strategy", self._native_params())

    def set_futures_self_trade_strategy(self, *, strategy: str) -> dict[str, Any]:
        """
        PUT /derivatives/api/v3/self-trade-strategy.

        Source: https://docs.kraken.com/api-reference/trading-settings/update-self-trade-strategy
        """
        return self._native_private(
            "set_futures_self_trade_strategy", self._native_params(strategy=strategy)
        )

    def get_futures_trading_instruments(
        self, *, contract_types: list[str] | None = None
    ) -> dict[str, Any]:
        """
        GET /derivatives/api/v3/trading/instruments.

        Source: https://docs.kraken.com/api-reference/instrument-details/get-trading-instruments
        """
        return self._native_private(
            "get_futures_trading_instruments",
            self._native_params(
                contractType=dumps(contract_types) if contract_types is not None else None
            ),
        )

    def get_futures_subaccount_trading_status(self, *, subaccount_uid: str) -> dict[str, Any]:
        """
        GET /derivatives/api/v3/subaccount/{subaccountUid}/trading-enabled.

        Source: https://docs.kraken.com/api-reference/subaccounts/check-subaccount-trading-status
        """
        return self._native_private(
            "get_futures_subaccount_trading_status",
            self._native_params(subaccountUid=subaccount_uid),
        )

    def set_futures_subaccount_trading_status(
        self, *, subaccount_uid: str, trading_enabled: bool
    ) -> dict[str, Any]:
        """
        PUT /derivatives/api/v3/subaccount/{subaccountUid}/trading-enabled.

        Source: https://docs.kraken.com/api-reference/subaccounts/update-subaccount-trading-status
        """
        return self._native_private(
            "set_futures_subaccount_trading_status",
            self._native_params(subaccountUid=subaccount_uid, tradingEnabled=trading_enabled),
        )

    def delete_spot_export_report(self, *, id: str, report_action: str) -> dict[str, Any]:
        """
        POST /0/private/RemoveExport.

        Source: https://docs.kraken.com/api-reference/account-data/delete-export-report
        """
        return self._native_private(
            "delete_spot_export_report", self._native_params(id=id, type=report_action)
        )

    def get_spot_export_status(self, *, report: str) -> dict[str, Any]:
        """
        POST /0/private/ExportStatus.

        Source: https://docs.kraken.com/api-reference/account-data/get-export-report-status
        """
        return self._native_private("get_spot_export_status", self._native_params(report=report))

    def request_spot_export_report(
        self,
        *,
        report: str,
        description: str,
        format: str | None = None,
        fields: str | None = None,
        starttm: int | None = None,
        endtm: int | None = None,
    ) -> dict[str, Any]:
        """
        POST /0/private/AddExport.

        Source: https://docs.kraken.com/api-reference/account-data/request-export-report
        """
        return self._native_private(
            "request_spot_export_report",
            self._native_params(
                report=report,
                format=format,
                description=description,
                fields=fields,
                starttm=starttm,
                endtm=endtm,
            ),
        )

    def simulate_futures_portfolio(self, *, portfolio: dict[str, Any]) -> dict[str, Any]:
        """

        POST /derivatives/api/v3/portfolio-margining/simulate. Available only in Kraken
        pre-production environments; configure futures_base_url.

        Source:
        https://docs.kraken.com/api-reference/account-information/calculate-portfolio-margin-pnl-and-greeks

        """
        return self._native_private(
            "simulate_futures_portfolio",
            self._native_params(json=dumps(portfolio, separators=(",", ":"))),
        )

    def check_futures_api_key(self) -> dict[str, Any]:
        """
        GET /api/auth/v1/api-keys/v3/check.

        Source: https://docs.kraken.com/api-reference/api-keys/check-v3-api-key
        """
        return self._native_private("check_futures_api_key", self._native_params())

    def get_futures_pnl_preferences(self) -> dict[str, Any]:
        """
        GET /derivatives/api/v3/pnlpreferences.

        Source: https://docs.kraken.com/api-reference/multi-collateral/get-pnl-currency-preferences
        """
        return self._native_private("get_futures_pnl_preferences", self._native_params())

    def set_futures_pnl_preference(self, *, symbol: str, pnl_preference: str) -> dict[str, Any]:
        """
        PUT /derivatives/api/v3/pnlpreferences.

        Source: https://docs.kraken.com/api-reference/multi-collateral/set-pnl-currency-preference
        """
        return self._native_private(
            "set_futures_pnl_preference",
            self._native_params(symbol=symbol, pnlPreference=pnl_preference),
        )

    def create_spot_subaccount(self, *, username: str, email: str) -> dict[str, Any]:
        """

        POST /0/private/CreateSubaccount. Requires an eligible institutional master account and
        Funds Withdraw permission.

        Source: https://docs.kraken.com/api-reference/subaccounts/create-subaccount

        """
        return self._native_private(
            "create_spot_subaccount", self._native_params(username=username, email=email)
        )

    def get_futures_subaccounts(self) -> dict[str, Any]:
        """
        GET /derivatives/api/v3/subaccounts.

        Source: https://docs.kraken.com/api-reference/subaccounts/get-subaccounts
        """
        return self._native_private("get_futures_subaccounts", self._native_params())

    def retrieve_spot_export(self, id: str) -> bytes:
        """Download a completed Spot export as ZIP bytes, preserving binary content."""
        if self._native_client is None:
            raise RuntimeError("Kraken native client is required.")
        return self._native_client.retrieve_spot_export(id)

    def get_withdrawal_addresses(
        self,
        *,
        asset: str | None = None,
        aclass: str | None = None,
        method: str | None = None,
        key: str | None = None,
        verified: bool | None = None,
    ) -> dict[str, Any]:
        """
        Read-only POST /0/private/WithdrawAddresses.

        Source: https://docs.kraken.com/api-reference/funding/get-withdrawal-addresses.md
        """
        return self._native_private(
            "get_withdrawal_addresses",
            self._native_params(
                asset=asset, aclass=aclass, method=method, key=key, verified=verified
            ),
        )

    def get_withdrawal_information(self, *, asset: str, key: str, amount: str) -> dict[str, Any]:
        """
        Read-only POST /0/private/WithdrawInfo.

        Source: https://docs.kraken.com/api-reference/funding/get-withdrawal-information.md
        """
        return self._native_private(
            "get_withdrawal_information", self._native_params(asset=asset, key=key, amount=amount)
        )

    def get_withdrawal_methods(
        self,
        *,
        asset: str | None = None,
        aclass: str | None = None,
        network: str | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """
        Read-only POST /0/private/WithdrawMethods.

        Source: https://docs.kraken.com/api-reference/funding/get-withdrawal-methods.md
        """
        return self._native_private(
            "get_withdrawal_methods",
            self._native_params(
                asset=asset, aclass=aclass, network=network, rebase_multiplier=rebase_multiplier
            ),
        )

    def get_withdrawal_status(
        self,
        *,
        asset: str | None = None,
        aclass: str | None = None,
        method: str | None = None,
        start: str | None = None,
        end: str | None = None,
        cursor: str | bool | None = None,
        limit: int | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """
        Read-only POST /0/private/WithdrawStatus.

        Source: https://docs.kraken.com/api-reference/funding/get-status-of-recent-withdrawals.md
        """
        return self._native_private(
            "get_withdrawal_status",
            self._native_params(
                asset=asset,
                aclass=aclass,
                method=method,
                start=start,
                end=end,
                cursor=cursor,
                limit=limit,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    def edit_spot_order(
        self,
        *,
        pair: str,
        txid: str,
        userref: int | None = None,
        volume: str | None = None,
        displayvol: str | None = None,
        asset_class: str | None = None,
        price: str | None = None,
        price2: str | None = None,
        oflags: str | None = None,
        deadline: str | None = None,
        cancel_response: bool | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel and replace an order, returning a new txid; queue priority is lost."""
        return self._native_private(
            "edit_spot_order",
            self._native_params(
                pair=pair,
                txid=txid,
                userref=userref,
                volume=volume,
                displayvol=displayvol,
                asset_class=asset_class,
                price=price,
                price2=price2,
                oflags=oflags,
                deadline=deadline,
                cancel_response=cancel_response,
                validate=validate,
            ),
        )
