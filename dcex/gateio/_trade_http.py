from typing import Any

from ..enums import OrderSide
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Gate.io trade HTTP client backed by Rust private dispatch."""

    def get_futures_all_positions(
        self,
        ccy: str = "usdt",
        holding: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_futures_all_positions",
            self._native_params(ccy=ccy, holding=holding, limit=limit, offset=offset),
        )

    def get_contract_single_positions(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "get_contract_single_positions",
            self._native_params(product_symbol=product_symbol, ccy=ccy, path=path),
        )

    def update_futures_positions_leverage(
        self,
        product_symbol: str,
        leverage: str,
        ccy: str = "usdt",
        cross_leverage_limit: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "update_futures_positions_leverage",
            self._native_params(
                product_symbol=product_symbol,
                leverage=leverage,
                ccy=ccy,
                cross_leverage_limit=cross_leverage_limit,
            ),
        )

    def future_dual_mode_switch(
        self,
        dual_mode: bool,
        ccy: str = "usdt",
    ) -> dict[str, Any]:
        return self._native_private(
            "future_dual_mode_switch",
            self._native_params(dual_mode=dual_mode, ccy=ccy),
        )

    def place_contract_order(
        self,
        product_symbol: str,
        size: int,
        ccy: str = "usdt",
        path: str = "futures",
        iceberg: int | None = None,
        price: str | None = None,
        close: bool | None = None,
        reduce_only: bool | None = None,
        tif: str | None = None,
        text: str | None = None,
        auto_size: str | None = None,
        stp_act: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_contract_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                ccy=ccy,
                path=path,
                iceberg=iceberg,
                price=price,
                close=close,
                reduce_only=reduce_only,
                tif=tif,
                text=text,
                auto_size=auto_size,
                stp_act=stp_act,
            ),
        )

    def place_contract_market_order(
        self,
        product_symbol: str,
        size: int,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "place_contract_market_order",
            self._native_params(product_symbol=product_symbol, size=size, ccy=ccy, path=path),
        )

    def place_contract_market_buy_order(
        self,
        product_symbol: str,
        size: int,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "place_contract_market_buy_order",
            self._native_params(product_symbol=product_symbol, size=size, ccy=ccy, path=path),
        )

    def place_contract_market_sell_order(
        self,
        product_symbol: str,
        size: int,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "place_contract_market_sell_order",
            self._native_params(product_symbol=product_symbol, size=size, ccy=ccy, path=path),
        )

    def place_contract_limit_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "place_contract_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                ccy=ccy,
                path=path,
            ),
        )

    def place_contract_limit_buy_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "place_contract_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                ccy=ccy,
                path=path,
            ),
        )

    def place_contract_limit_sell_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "place_contract_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                ccy=ccy,
                path=path,
            ),
        )

    def place_contract_post_only_limit_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "place_contract_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                ccy=ccy,
                path=path,
            ),
        )

    def place_contract_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "place_contract_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                ccy=ccy,
                path=path,
            ),
        )

    def place_contract_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "place_contract_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                ccy=ccy,
                path=path,
            ),
        )

    def place_futures_batch_order(
        self,
        orders: list[dict[str, Any]],
        ccy: str = "usdt",
    ) -> dict[str, Any]:
        if not isinstance(orders, list) or not all(isinstance(order, dict) for order in orders):
            raise TypeError("Orders must be a list of dictionaries.")
        if len(orders) > 10:
            raise ValueError("The number of orders cannot exceed 10.")
        return self._native_private(
            "place_futures_batch_order",
            self._native_params(orders=orders, ccy=ccy),
        )

    def get_contract_order_list(
        self,
        status: str,
        ccy: str = "usdt",
        path: str = "futures",
        product_symbol: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        last_id: str | None = None,
        count_total: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_contract_order_list",
            self._native_params(
                status=status,
                ccy=ccy,
                path=path,
                product_symbol=product_symbol,
                limit=limit,
                offset=offset,
                last_id=last_id,
                count_total=count_total,
            ),
        )

    def cancel_contract_all_order_matched(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        path: str = "futures",
        side: OrderSide | str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "cancel_contract_all_order_matched",
            self._native_params(product_symbol=product_symbol, ccy=ccy, path=path, side=side),
        )

    def get_contract_single_order(
        self,
        order_id: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "get_contract_single_order",
            self._native_params(order_id=order_id, ccy=ccy, path=path),
        )

    def cancel_contract_single_order(
        self,
        order_id: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return self._native_private(
            "cancel_contract_single_order",
            self._native_params(order_id=order_id, ccy=ccy, path=path),
        )

    def amend_futures_single_order(
        self,
        order_id: str,
        ccy: str = "usdt",
        size: int | None = None,
        price: str | None = None,
        amend_text: str | None = None,
        biz_info: str | None = None,
        bbo: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "amend_futures_single_order",
            self._native_params(
                order_id=order_id,
                ccy=ccy,
                size=size,
                price=price,
                amend_text=amend_text,
                biz_info=biz_info,
                bbo=bbo,
            ),
        )

    def get_trading_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        path: str = "futures",
        order: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        late_id: str | None = None,
        count_total: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_trading_history",
            self._native_params(
                product_symbol=product_symbol,
                ccy=ccy,
                path=path,
                order=order,
                limit=limit,
                offset=offset,
                late_id=late_id,
                count_total=count_total,
            ),
        )

    def get_futures_position_close_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        limit: int | None = None,
        offset: int | None = None,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        side: OrderSide | str | None = None,
        pnl: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_futures_position_close_history",
            self._native_params(
                product_symbol=product_symbol,
                ccy=ccy,
                limit=limit,
                offset=offset,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                side=side,
                pnl=pnl,
            ),
        )

    def get_futures_auto_deleveraging_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        limit: int | None = None,
        at_timestamp: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_futures_auto_deleveraging_history",
            self._native_params(
                product_symbol=product_symbol,
                ccy=ccy,
                limit=limit,
                at_timestamp=at_timestamp,
            ),
        )

    def get_delivery_all_positions(self, ccy: str = "usdt") -> dict[str, Any]:
        return self._native_private(
            "get_delivery_all_positions",
            self._native_params(ccy=ccy),
        )

    def update_delivery_positions_leverage(
        self,
        product_symbol: str,
        leverage: str,
        ccy: str = "usdt",
    ) -> dict[str, Any]:
        return self._native_private(
            "update_delivery_positions_leverage",
            self._native_params(product_symbol=product_symbol, leverage=leverage, ccy=ccy),
        )

    def get_delivery_position_close_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_delivery_position_close_history",
            self._native_params(product_symbol=product_symbol, ccy=ccy, limit=limit),
        )

    def place_spot_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        amount: str,
        text: str | None = None,
        order_type: str | None = None,
        account: str | None = None,
        price: str | None = None,
        time_in_force: str | None = None,
        iceberg: str | None = None,
        auto_borrow: bool = False,
        auto_repay: bool = False,
        stp_act: str | None = None,
        action_mode: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                amount=amount,
                text=text,
                order_type=order_type,
                account=account,
                price=price,
                time_in_force=time_in_force,
                iceberg=iceberg,
                auto_borrow=auto_borrow,
                auto_repay=auto_repay,
                stp_act=stp_act,
                action_mode=action_mode,
            ),
        )

    def place_spot_market_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        amount: str,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_market_order",
            self._native_params(product_symbol=product_symbol, side=side, amount=amount),
        )

    def place_spot_market_buy_order(self, product_symbol: str, amount: str) -> dict[str, Any]:
        return self._native_private(
            "place_spot_market_buy_order",
            self._native_params(product_symbol=product_symbol, amount=amount),
        )

    def place_spot_market_sell_order(self, product_symbol: str, amount: str) -> dict[str, Any]:
        return self._native_private(
            "place_spot_market_sell_order",
            self._native_params(product_symbol=product_symbol, amount=amount),
        )

    def place_spot_limit_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                amount=amount,
                price=price,
            ),
        )

    def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_limit_buy_order",
            self._native_params(product_symbol=product_symbol, amount=amount, price=price),
        )

    def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_limit_sell_order",
            self._native_params(product_symbol=product_symbol, amount=amount, price=price),
        )

    def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                amount=amount,
                price=price,
            ),
        )

    def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_post_only_limit_buy_order",
            self._native_params(product_symbol=product_symbol, amount=amount, price=price),
        )

    def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return self._native_private(
            "place_spot_post_only_limit_sell_order",
            self._native_params(product_symbol=product_symbol, amount=amount, price=price),
        )

    def get_spot_open_orders(
        self,
        page: str | None = None,
        limit: str | None = None,
        account: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_spot_open_orders",
            self._native_params(page=page, limit=limit, account=account),
        )

    def get_spot_order_list(
        self,
        product_symbol: str,
        status: str,
        page: str | None = None,
        limit: str | None = None,
        account: str | None = None,
        from_timestamp: str | None = None,
        to_timestamp: str | None = None,
        side: OrderSide | str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_spot_order_list",
            self._native_params(
                product_symbol=product_symbol,
                status=status,
                page=page,
                limit=limit,
                account=account,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                side=side,
            ),
        )

    def cancel_spot_order(
        self,
        product_symbol: str | None = None,
        side: OrderSide | str | None = None,
        account: str | None = None,
        action_mode: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "cancel_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                account=account,
                action_mode=action_mode,
            ),
        )

    def get_spot_single_order(
        self,
        order_id: str,
        product_symbol: str,
        account: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_spot_single_order",
            self._native_params(order_id=order_id, product_symbol=product_symbol, account=account),
        )

    def cancel_spot_single_order(
        self,
        order_id: str,
        product_symbol: str,
        account: str | None = None,
        action_mode: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "cancel_spot_single_order",
            self._native_params(
                order_id=order_id,
                product_symbol=product_symbol,
                account=account,
                action_mode=action_mode,
            ),
        )

    def amend_spot_single_order(
        self,
        order_id: str,
        product_symbol: str | None = None,
        account: str | None = None,
        amount: str | None = None,
        price: str | None = None,
        amend_text: str | None = None,
        action_mode: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "amend_spot_single_order",
            self._native_params(
                order_id=order_id,
                product_symbol=product_symbol,
                account=account,
                amount=amount,
                price=price,
                amend_text=amend_text,
                action_mode=action_mode,
            ),
        )

    def get_spot_trading_history(
        self,
        product_symbol: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        order_id: str | None = None,
        account: str | None = None,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_spot_trading_history",
            self._native_params(
                product_symbol=product_symbol,
                limit=limit,
                page=page,
                order_id=order_id,
                account=account,
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
            ),
        )
