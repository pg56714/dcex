"""Generated bingx coin futures HTTP methods."""

from typing import Any

from dcex._operation_guards import require_scope

from .._market_http import MarketHTTP


class GeneratedCoinFuturesHTTP(MarketHTTP):
    """Coin futures API methods."""

    def post_cswap_v2_trade_order(
        self,
        *,
        symbol: str,
        type_: str,
        side: str,
        position_side: str,
        price: str | None = None,
        quantity: str | None = None,
        stop_price: str | None = None,
        working_type: str | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
        time_in_force: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Trade order.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Coin-M%20Futures/Trades%20Endpoints/Trade%20order
        """
        return self._native_private(
            "post_cswap_v2_trade_order",
            self._native_params(
                **{
                    "symbol": symbol,
                    "type": type_,
                    "side": side,
                    "positionSide": position_side,
                    "price": price,
                    "quantity": quantity,
                    "stopPrice": stop_price,
                    "workingType": working_type,
                    "stopLoss": stop_loss,
                    "takeProfit": take_profit,
                    "clientOrderId": client_order_id,
                    "recvWindow": recv_window,
                    "timeInForce": time_in_force,
                }
            ),
        )

    def delete_cswap_v1_trade_all_open_orders(
        self,
        *,
        symbol: str | None = None,
        recv_window: int | None = None,
        all_symbols: bool = False,
    ) -> Any:  # noqa: ANN401
        """
        Cancel all orders.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Coin-M%20Futures/Trades%20Endpoints/Cancel%20all%20orders
        """
        require_scope(symbol, all_symbols)
        return self._native_private(
            "delete_cswap_v1_trade_all_open_orders",
            self._native_params(
                **{"symbol": symbol, "recvWindow": recv_window, "all_symbols": all_symbols}
            ),
        )
