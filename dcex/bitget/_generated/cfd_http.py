"""Generated bitget cfd HTTP methods."""

from typing import Any

from dcex._operation_guards import require_confirmation

from .._market_http import MarketHTTP


class GeneratedCfdHTTP(MarketHTTP):
    """Cfd API methods."""

    def cfd_account_get_fund_detail(self) -> dict[str, Any]:
        """
        Get Fund Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-account/cfd-account#get-cfd-fund-detail
        """
        return self._native_private("cfd_account_get_fund_detail", self._native_params(**{}))

    def cfd_account_transfer(
        self, *, coin: str, amount: str, account_type: str, direction: str
    ) -> dict[str, Any]:
        """
        Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-account/cfd-account#cfd-transfer
        """
        return self._native_private(
            "cfd_account_transfer",
            self._native_params(
                **{
                    "coin": coin,
                    "amount": amount,
                    "accountType": account_type,
                    "direction": direction,
                }
            ),
        )

    def cfd_account_get_transfer_records(
        self,
        *,
        transfer_id: str | None = None,
        sub_uid: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        direction: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Transfer Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-account/cfd-account#get-cfd-transfer-records
        """
        return self._native_private(
            "cfd_account_get_transfer_records",
            self._native_params(
                **{
                    "transferId": transfer_id,
                    "subUid": sub_uid,
                    "startTime": start_time,
                    "endTime": end_time,
                    "direction": direction,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def cfd_account_get_financial_records(
        self,
        *,
        type_: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Financial Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-account/cfd-account#get-cfd-financial-records
        """
        return self._native_private(
            "cfd_account_get_financial_records",
            self._native_params(
                **{
                    "type": type_,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def cfd_account_get_instruments(self, *, symbol: str | None = None) -> dict[str, Any]:
        """
        Get Instruments.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-account/cfd-account#get-cfd-instruments
        """
        return self._native_private(
            "cfd_account_get_instruments", self._native_params(**{"symbol": symbol})
        )

    def cfd_market_get_tickers(self, *, symbol: str | None = None) -> dict[str, Any]:
        """
        Get Tickers.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-market/cfd-market#get-cfd-tickers
        """
        return self._native_private(
            "cfd_market_get_tickers", self._native_params(**{"symbol": symbol})
        )

    def cfd_market_get_history_candlestick(
        self,
        *,
        symbol: str,
        interval: str,
        side: str,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Kline/Candlestick History.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-market/cfd-market#get-cfd-kline-candlestick-history
        """
        return self._native_private(
            "cfd_market_get_history_candlestick",
            self._native_params(
                **{
                    "symbol": symbol,
                    "interval": interval,
                    "side": side,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    def cfd_trade_place_order(
        self,
        *,
        symbol: str,
        order_type: str,
        side: str,
        qty: str,
        price: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
    ) -> dict[str, Any]:
        """
        Place CFD Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#place-cfd-order
        """
        return self._native_private(
            "cfd_trade_place_order",
            self._native_params(
                **{
                    "symbol": symbol,
                    "orderType": order_type,
                    "side": side,
                    "qty": qty,
                    "price": price,
                    "takeProfit": take_profit,
                    "stopLoss": stop_loss,
                }
            ),
        )

    def cfd_trade_modify_order(
        self,
        *,
        order_id: str,
        price: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
    ) -> dict[str, Any]:
        """
        Modify CFD Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#modify-cfd-order
        """
        return self._native_private(
            "cfd_trade_modify_order",
            self._native_params(
                **{
                    "orderId": order_id,
                    "price": price,
                    "takeProfit": take_profit,
                    "stopLoss": stop_loss,
                }
            ),
        )

    def cfd_trade_cancel_order(self, *, order_id: str) -> dict[str, Any]:
        """
        Cancel CFD Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#cancel-cfd-order
        """
        return self._native_private(
            "cfd_trade_cancel_order", self._native_params(**{"orderId": order_id})
        )

    def cfd_trade_cancel_all_orders(
        self, *, symbol: str | None = None, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Cancel All CFD Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#cancel-all-cfd-orders
        """
        require_confirmation(confirm)
        return self._native_private(
            "cfd_trade_cancel_all_orders",
            self._native_params(**{"symbol": symbol, "confirm": confirm}),
        )

    def cfd_trade_close_positions(self, *, position_id: str, qty: str) -> dict[str, Any]:
        """
        Close CFD Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#close-cfd-positions
        """
        return self._native_private(
            "cfd_trade_close_positions",
            self._native_params(**{"positionId": position_id, "qty": qty}),
        )

    def cfd_trade_close_all_positions(
        self, *, symbol: str | None = None, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Close All CFD Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#close-all-cfd-positions
        """
        require_confirmation(confirm)
        return self._native_private(
            "cfd_trade_close_all_positions",
            self._native_params(**{"symbol": symbol, "confirm": confirm}),
        )

    def cfd_trade_get_unfilled_orders(
        self, *, symbol: str, sub_uid: str | None = None
    ) -> dict[str, Any]:
        """
        Get CFD Unfilled Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#get-cfd-unfilled-orders
        """
        return self._native_private(
            "cfd_trade_get_unfilled_orders",
            self._native_params(**{"symbol": symbol, "subUid": sub_uid}),
        )

    def cfd_trade_get_order_history(
        self,
        *,
        symbol: str,
        sub_uid: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        page_no: str | None = None,
    ) -> dict[str, Any]:
        """
        Get CFD Order History.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#get-cfd-order-history
        """
        return self._native_private(
            "cfd_trade_get_order_history",
            self._native_params(
                **{
                    "symbol": symbol,
                    "subUid": sub_uid,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "pageNo": page_no,
                }
            ),
        )

    def cfd_trade_get_current_positions(
        self, *, symbol: str | None = None, sub_uid: str | None = None
    ) -> dict[str, Any]:
        """
        Get CFD Current Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#get-cfd-current-positions
        """
        return self._native_private(
            "cfd_trade_get_current_positions",
            self._native_params(**{"symbol": symbol, "subUid": sub_uid}),
        )
