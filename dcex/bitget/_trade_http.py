"""Bitget private trade HTTP client backed by Rust."""

from typing import Any

from .._operation_guards import require_confirmation, require_scope
from ._batch_http import TradeHTTPBatchHTTP
from ._http_manager import HTTPManager
from ._transfers_http import TradeHTTPTransfersHTTP
from ._withdrawals_http import TradeHTTPWithdrawalsHTTP


class TradeHTTP(TradeHTTPBatchHTTP, TradeHTTPTransfersHTTP, TradeHTTPWithdrawalsHTTP, HTTPManager):
    """HTTP client for Bitget private trading operations."""

    def place_uta_order(
        self,
        category: str,
        product_symbol: str,
        side: str,
        order_type: str,
        qty: str,
        price: str | None = None,
        time_in_force: str | None = None,
        pos_side: str | None = None,
        client_oid: str | None = None,
        reduce_only: str | None = None,
        stp_mode: str | None = None,
        margin_mode: str | None = None,
        tp_trigger_by: str | None = None,
        sl_trigger_by: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        tp_order_type: str | None = None,
        sl_order_type: str | None = None,
        tp_limit_price: str | None = None,
        sl_limit_price: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget UTA order."""
        return self._native_private(
            "place_uta_order",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                side=side,
                orderType=order_type,
                qty=qty,
                price=price,
                timeInForce=time_in_force,
                posSide=pos_side,
                clientOid=client_oid,
                reduceOnly=reduce_only,
                stpMode=stp_mode,
                marginMode=margin_mode,
                tpTriggerBy=tp_trigger_by,
                slTriggerBy=sl_trigger_by,
                takeProfit=take_profit,
                stopLoss=stop_loss,
                tpOrderType=tp_order_type,
                slOrderType=sl_order_type,
                tpLimitPrice=tp_limit_price,
                slLimitPrice=sl_limit_price,
            ),
        )

    def place_reality_order(
        self,
        product_symbol: str,
        side: str,
        order_type: str,
        qty: str,
        price: str | None = None,
        category: str = "SPOT",
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget Reality stock order through the dedicated endpoint."""
        return self._native_private(
            "place_reality_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                orderType=order_type,
                qty=qty,
                price=price,
                category=category,
                clientOid=client_oid,
            ),
        )

    def cancel_uta_order(
        self,
        order_id: str | None = None,
        client_oid: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Bitget UTA order."""
        return self._native_private(
            "cancel_uta_order",
            self._native_params(orderId=order_id, clientOid=client_oid, category=category),
        )

    def cancel_reality_order(
        self,
        product_symbol: str,
        order_id: str | None = None,
        client_oid: str | None = None,
        category: str = "SPOT",
    ) -> dict[str, Any]:
        """Cancel a Bitget Reality stock order through the dedicated endpoint."""
        return self._native_private(
            "cancel_reality_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=order_id,
                clientOid=client_oid,
                category=category,
            ),
        )

    def get_uta_order(
        self,
        order_id: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve one Bitget UTA order."""
        return self._native_private(
            "get_uta_order",
            self._native_params(orderId=order_id, clientOid=client_oid),
        )

    def get_uta_open_orders(
        self,
        category: str | None = None,
        product_symbol: str | None = None,
        symbol: str | None = None,
        start_time: int | str | None = None,
        end_time: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA open orders."""
        return self._native_private(
            "get_uta_open_orders",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_uta_history_orders(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
        start_time: int | str | None = None,
        end_time: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA historical orders."""
        return self._native_private(
            "get_uta_history_orders",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_uta_fills(
        self,
        category: str | None = None,
        order_id: str | None = None,
        start_time: int | str | None = None,
        end_time: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA fills."""
        return self._native_private(
            "get_uta_fills",
            self._native_params(
                category=category,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_uta_positions(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
        pos_side: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA positions."""
        return self._native_private(
            "get_uta_positions",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
                posSide=pos_side,
            ),
        )

    def place_uta_strategy_order(
        self, category: str, product_symbol: str, **params: object
    ) -> dict[str, Any]:
        """Place a Bitget UTA TP/SL or trigger strategy order."""
        return self._native_private(
            "place_uta_strategy_order",
            self._native_params(category=category, product_symbol=product_symbol, **params),
        )

    def modify_uta_strategy_order(
        self,
        order_id: str,
        qty: str,
        client_oid: str | None = None,
        **params: object,
    ) -> dict[str, Any]:
        """Modify a Bitget UTA strategy order."""
        return self._native_private(
            "modify_uta_strategy_order",
            self._native_params(qty=qty, orderId=order_id, clientOid=client_oid, **params),
        )

    def cancel_uta_strategy_order(
        self,
        order_id: str,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Bitget UTA strategy order."""
        return self._native_private(
            "cancel_uta_strategy_order",
            self._native_params(orderId=order_id, clientOid=client_oid),
        )

    def get_uta_unfilled_strategy_orders(
        self,
        category: str,
        type: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve pending Bitget UTA strategy orders."""
        return self._native_private(
            "get_uta_unfilled_strategy_orders",
            self._native_params(
                category=category,
                type=type,
            ),
        )

    def get_uta_history_strategy_orders(
        self,
        category: str,
        type: str | None = None,
        start_time: int | str | None = None,
        end_time: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve historical Bitget UTA strategy orders."""
        return self._native_private(
            "get_uta_history_strategy_orders",
            self._native_params(
                category=category,
                type=type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def modify_uta_order(
        self,
        product_symbol: str,
        category: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
        qty: str | None = None,
        price: str | None = None,
        request_id: int | None = None,
        auto_cancel: str | None = None,
        tp_trigger_by: str | None = None,
        sl_trigger_by: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        tp_order_type: str | None = None,
        sl_order_type: str | None = None,
        tp_limit_price: str | None = None,
        sl_limit_price: str | None = None,
        px_amend_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Call ``POST /api/v3/trade/modify-order``. Symbol and category satisfy the September 30,
        2026 requirements.
        """
        return self._native_private(
            "modify_uta_order",
            self._native_params(
                product_symbol=product_symbol,
                category=category,
                orderId=order_id,
                clientOid=client_oid,
                qty=qty,
                price=price,
                requestId=request_id,
                autoCancel=auto_cancel,
                tpTriggerBy=tp_trigger_by,
                slTriggerBy=sl_trigger_by,
                takeProfit=take_profit,
                stopLoss=stop_loss,
                tpOrderType=tp_order_type,
                slOrderType=sl_order_type,
                tpLimitPrice=tp_limit_price,
                slLimitPrice=sl_limit_price,
                pxAmendType=px_amend_type,
            ),
        )

    def cancel_uta_orders_by_symbol(
        self, category: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/trade/cancel-symbol-order``."""
        return self._native_private(
            "cancel_uta_orders_by_symbol",
            self._native_params(category=category, product_symbol=product_symbol),
        )

    def set_uta_cancel_countdown(self, countdown: str) -> dict[str, Any]:
        """
        Call ``POST /api/v3/trade/countdown-cancel-all``. Exchange approval is required;
        countdown is 0 or 5..60 seconds.
        """
        return self._native_private(
            "set_uta_cancel_countdown", self._native_params(countdown=countdown)
        )

    def close_uta_positions(
        self,
        category: str,
        *,
        product_symbol: str | None = None,
        pos_side: str | None = None,
        all_symbols: bool = False,
    ) -> dict[str, Any]:
        """
        Call ``POST /api/v3/trade/close-positions``.

        Provide a product symbol or all_symbols=True to close all positions in this category.
        """
        require_scope(product_symbol, all_symbols)
        return self._native_private(
            "close_uta_positions",
            self._native_params(
                all_symbols=all_symbols,
                category=category,
                product_symbol=product_symbol,
                posSide=pos_side,
            ),
        )

    def get_uta_position_history(
        self,
        category: str,
        *,
        product_symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/position/history-position``."""
        return self._native_private(
            "get_uta_position_history",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def adjust_uta_position_margin(
        self, category: str, product_symbol: str, pos_side: str, operation: str, amount: str
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/set-margin``."""
        return self._native_private(
            "adjust_uta_position_margin",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                posSide=pos_side,
                operation=operation,
                amount=amount,
            ),
        )

    def get_uta_financial_records(
        self,
        category: str,
        *,
        coin: str | None = None,
        type_: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/financial-records``."""
        return self._native_private(
            "get_uta_financial_records",
            self._native_params(
                category=category,
                coin=coin,
                type=type_,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_futures_estimated_open_count(
        self,
        product_symbol: str,
        product_type: str,
        margin_coin: str,
        open_amount: str,
        open_price: str,
        *,
        leverage: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/open-count``."""
        return self._native_private(
            "get_futures_estimated_open_count",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
                openAmount=open_amount,
                openPrice=open_price,
                leverage=leverage,
            ),
        )

    def get_futures_liquidation_price(
        self,
        product_symbol: str,
        product_type: str,
        margin_coin: str,
        pos_side: str,
        order_type: str,
        open_amount: str,
        *,
        open_price: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/liq-price``."""
        return self._native_private(
            "get_futures_liquidation_price",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
                posSide=pos_side,
                orderType=order_type,
                openAmount=open_amount,
                openPrice=open_price,
            ),
        )

    def get_futures_interest_history(
        self,
        product_type: str,
        start_time: int,
        end_time: int,
        *,
        coin: str | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/interest-history``."""
        return self._native_private(
            "get_futures_interest_history",
            self._native_params(
                productType=product_type,
                startTime=start_time,
                endTime=end_time,
                coin=coin,
                idLessThan=id_less_than,
                limit=limit,
            ),
        )

    def set_futures_all_leverage(self, product_type: str, leverage: str) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/account/set-all-leverage``."""
        return self._native_private(
            "set_futures_all_leverage",
            self._native_params(productType=product_type, leverage=leverage),
        )

    def set_futures_auto_margin(
        self, product_symbol: str, auto_margin: str, margin_coin: str, hold_side: str
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/account/set-auto-margin``."""
        return self._native_private(
            "set_futures_auto_margin",
            self._native_params(
                product_symbol=product_symbol,
                autoMargin=auto_margin,
                marginCoin=margin_coin,
                holdSide=hold_side,
            ),
        )

    def set_futures_asset_mode(
        self, product_type: str, asset_mode: str, *, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Call ``POST /api/v2/mix/account/set-asset-mode``.

        Requires confirm=True. This changes collateral accounting for futures.
        """
        require_confirmation(confirm)
        return self._native_private(
            "set_futures_asset_mode",
            self._native_params(confirm=confirm, productType=product_type, assetMode=asset_mode),
        )

    def convert_futures_union_asset(self, coin: str, amount: str) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/account/union-convert``."""
        return self._native_private(
            "convert_futures_union_asset", self._native_params(coin=coin, amount=amount)
        )

    def get_futures_union_config(self) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/union-config``."""
        return self._native_private("get_futures_union_config", self._native_params())

    def get_futures_isolated_symbols(self, product_type: str) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/isolated-symbols``."""
        return self._native_private(
            "get_futures_isolated_symbols", self._native_params(productType=product_type)
        )

    def reverse_futures_position(
        self,
        product_symbol: str,
        margin_coin: str,
        product_type: str,
        side: str,
        *,
        size: str | None = None,
        trade_side: str | None = None,
        client_oid: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """
        Call ``POST /api/v2/mix/order/click-backhand``.

        Requires confirm=True. This closes and reverses the selected position.
        """
        require_confirmation(confirm)
        return self._native_private(
            "reverse_futures_position",
            self._native_params(
                confirm=confirm,
                product_symbol=product_symbol,
                marginCoin=margin_coin,
                productType=product_type,
                side=side,
                size=size,
                tradeSide=trade_side,
                clientOid=client_oid,
            ),
        )

    def get_cross_margin_risk_rate(self) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/account/risk-rate``."""
        return self._native_private("get_cross_margin_risk_rate", self._native_params())

    def flash_repay_cross_margin_assets(self, *, coin: str | None = None) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/account/flash-repay``."""
        return self._native_private(
            "flash_repay_cross_margin_assets", self._native_params(coin=coin)
        )

    def get_cross_margin_flash_repay_result(self, id_list: list[str]) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/account/query-flash-repay-status``."""
        return self._native_private(
            "get_cross_margin_flash_repay_result", self._native_params(idList=id_list)
        )

    def get_cross_margin_interest_rate_limits(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/interest-rate-and-limit``."""
        return self._native_private(
            "get_cross_margin_interest_rate_limits", self._native_params(coin=coin)
        )

    def get_cross_margin_tiers(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/tier-data``."""
        return self._native_private("get_cross_margin_tiers", self._native_params(coin=coin))

    def get_cross_margin_borrow_history(
        self,
        start_time: int,
        *,
        loan_id: str | None = None,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/borrow-history``."""
        return self._native_private(
            "get_cross_margin_borrow_history",
            self._native_params(
                startTime=start_time,
                loanId=loan_id,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    def get_cross_margin_repay_history(
        self,
        start_time: int,
        *,
        repay_id: str | None = None,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/repay-history``."""
        return self._native_private(
            "get_cross_margin_repay_history",
            self._native_params(
                startTime=start_time,
                repayId=repay_id,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    def get_cross_margin_interest_history(
        self,
        start_time: int,
        *,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/interest-history``."""
        return self._native_private(
            "get_cross_margin_interest_history",
            self._native_params(
                startTime=start_time,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    def get_cross_margin_liquidation_history(
        self,
        start_time: int,
        *,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/liquidation-history``."""
        return self._native_private(
            "get_cross_margin_liquidation_history",
            self._native_params(
                startTime=start_time, endTime=end_time, limit=limit, idLessThan=id_less_than
            ),
        )

    def get_isolated_margin_risk_rate(
        self,
        *,
        product_symbol: str | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/account/risk-rate``."""
        return self._native_private(
            "get_isolated_margin_risk_rate",
            self._native_params(
                product_symbol=product_symbol, pageNum=page_num, pageSize=page_size
            ),
        )

    def flash_repay_isolated_margin_assets(
        self, *, symbol_list: list[str] | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/account/flash-repay``."""
        return self._native_private(
            "flash_repay_isolated_margin_assets", self._native_params(symbolList=symbol_list)
        )

    def get_isolated_margin_flash_repay_result(self, id_list: list[str]) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/account/query-flash-repay-status``."""
        return self._native_private(
            "get_isolated_margin_flash_repay_result", self._native_params(idList=id_list)
        )

    def get_isolated_margin_interest_rate_limits(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/interest-rate-and-limit``."""
        return self._native_private(
            "get_isolated_margin_interest_rate_limits",
            self._native_params(product_symbol=product_symbol),
        )

    def get_isolated_margin_tiers(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/tier-data``."""
        return self._native_private(
            "get_isolated_margin_tiers", self._native_params(product_symbol=product_symbol)
        )

    def get_isolated_margin_borrow_history(
        self,
        product_symbol: str,
        start_time: int,
        *,
        loan_id: str | None = None,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/borrow-history``."""
        return self._native_private(
            "get_isolated_margin_borrow_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                loanId=loan_id,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    def get_isolated_margin_repay_history(
        self,
        product_symbol: str,
        start_time: int,
        *,
        repay_id: str | None = None,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/repay-history``."""
        return self._native_private(
            "get_isolated_margin_repay_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                repayId=repay_id,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    def get_isolated_margin_interest_history(
        self,
        product_symbol: str,
        start_time: int,
        *,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/interest-history``."""
        return self._native_private(
            "get_isolated_margin_interest_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    def get_isolated_margin_liquidation_history(
        self,
        product_symbol: str,
        start_time: int,
        *,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/liquidation-history``."""
        return self._native_private(
            "get_isolated_margin_liquidation_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    def get_uta_funding_assets(self, *, coin: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/account/funding-assets``."""
        return self._native_private("get_uta_funding_assets", self._native_params(coin=coin))

    def get_uta_funding_records(
        self,
        *,
        coin: str | None = None,
        type_: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/funding-financial-records``."""
        return self._native_private(
            "get_uta_funding_records",
            self._native_params(
                coin=coin,
                type=type_,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_uta_fee_rate(self, product_symbol: str, category: str) -> dict[str, Any]:
        """Call ``GET /api/v3/account/fee-rate``."""
        return self._native_private(
            "get_uta_fee_rate",
            self._native_params(product_symbol=product_symbol, category=category),
        )

    def set_uta_collateral_type(
        self,
        collateral_type: str,
        *,
        collateral_coins: str | None = None,
        allow_cashplus: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/set-collateral-type``."""
        return self._native_private(
            "set_uta_collateral_type",
            self._native_params(
                collateralType=collateral_type,
                collateralCoins=collateral_coins,
                allowCashplus=allow_cashplus,
            ),
        )

    def get_uta_settings(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/settings``."""
        return self._native_private("get_uta_settings", self._native_params())

    def get_uta_delta_info(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/delta-info``."""
        return self._native_private("get_uta_delta_info", self._native_params())

    def get_uta_repayable_coins(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/repayable-coins``."""
        return self._native_private("get_uta_repayable_coins", self._native_params())

    def get_uta_payment_coins(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/payment-coins``."""
        return self._native_private("get_uta_payment_coins", self._native_params())

    def borrow_uta_asset(
        self, coin: str, amount: str, *, client_oid: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/borrow``."""
        return self._native_private(
            "borrow_uta_asset", self._native_params(coin=coin, amount=amount, clientOid=client_oid)
        )

    def get_uta_max_borrowable(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v3/account/max-borrowable``."""
        return self._native_private("get_uta_max_borrowable", self._native_params(coin=coin))

    def get_uta_account_open_interest_limit(
        self, product_symbol: str, category: str
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/open-interest-limit``."""
        return self._native_private(
            "get_uta_account_open_interest_limit",
            self._native_params(product_symbol=product_symbol, category=category),
        )

    def get_uta_max_open_available(
        self,
        category: str,
        product_symbol: str,
        order_type: str,
        side: str,
        *,
        price: str | None = None,
        size: str | None = None,
        auto_borrow: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/max-open-available``."""
        return self._native_private(
            "get_uta_max_open_available",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                orderType=order_type,
                side=side,
                price=price,
                size=size,
                autoBorrow=auto_borrow,
            ),
        )

    def set_uta_repay_mode(self, repay_mode: str) -> dict[str, Any]:
        """Call ``POST /api/v3/account/set-repay-mode``."""
        return self._native_private("set_uta_repay_mode", self._native_params(repayMode=repay_mode))

    def get_uta_eligible_discount_rates(self, *, coin: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/account/eligible-discount-rate``."""
        return self._native_private(
            "get_uta_eligible_discount_rates", self._native_params(coin=coin)
        )

    def get_uta_eligible_loan_info(self, *, coin: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/account/eligible-loan-info``."""
        return self._native_private("get_uta_eligible_loan_info", self._native_params(coin=coin))

    def get_uta_eligible_margin_tiers(self, *, coin: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/account/eligible-margin-tier``."""
        return self._native_private("get_uta_eligible_margin_tiers", self._native_params(coin=coin))

    def get_uta_eligible_symbols(self, *, product_symbol: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/account/eligible-symbols``."""
        return self._native_private(
            "get_uta_eligible_symbols", self._native_params(product_symbol=product_symbol)
        )

    def get_uta_convert_records(
        self,
        *,
        from_coin: str | None = None,
        to_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/convert-records``."""
        return self._native_private(
            "get_uta_convert_records",
            self._native_params(
                fromCoin=from_coin,
                toCoin=to_coin,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def set_uta_account_mode(
        self,
        mode: str,
        *,
        delta_switch: str | None = None,
        target_uid: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """
        Call ``POST /api/v3/account/adjust-account-mode``. Uses advanced mode with delta_switch;
        the deprecated delta mode is not accepted.

        Requires confirm=True. This changes the account margin mode.
        """
        require_confirmation(confirm)
        return self._native_private(
            "set_uta_account_mode",
            self._native_params(
                confirm=confirm, mode=mode, deltaSwitch=delta_switch, targetUid=target_uid
            ),
        )

    def get_uta_adl_rank(self) -> dict[str, Any]:
        """Call ``GET /api/v3/position/adlRank``."""
        return self._native_private("get_uta_adl_rank", self._native_params())

    def get_uta_sub_accounts(
        self, *, limit: int | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/user/sub-list``."""
        return self._native_private(
            "get_uta_sub_accounts", self._native_params(limit=limit, cursor=cursor)
        )

    def get_uta_sub_account_assets(
        self, *, sub_uid: str | None = None, cursor: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/sub-unified-assets``."""
        return self._native_private(
            "get_uta_sub_account_assets",
            self._native_params(subUid=sub_uid, cursor=cursor, limit=limit),
        )

    def get_uta_strategy_sub_orders(
        self, order_id: str, *, limit: int | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/trade/strategy-sub-orders``."""
        return self._native_private(
            "get_uta_strategy_sub_orders",
            self._native_params(orderId=order_id, limit=limit, cursor=cursor),
        )

    def get_uta_deposit_records(
        self,
        start_time: int,
        end_time: int,
        *,
        coin: str | None = None,
        order_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/deposit-records``."""
        return self._native_private(
            "get_uta_deposit_records",
            self._native_params(
                coin=coin,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_all_trade_rates(self, business_type: str) -> dict[str, Any]:
        """Call ``GET /api/v2/common/all-trade-rate``."""
        return self._native_private(
            "get_all_trade_rates", self._native_params(businessType=business_type)
        )

    def set_uta_fee_deduction(self, deduct: str) -> dict[str, Any]:
        """Call ``POST /api/v3/account/switch-deduct``."""
        return self._native_private("set_uta_fee_deduction", self._native_params(deduct=deduct))

    def get_uta_fee_deduction(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/deduct-info``."""
        return self._native_private("get_uta_fee_deduction", self._native_params())

    def switch_to_classic_account(self, *, confirm: bool = False) -> dict[str, Any]:
        """
        Call ``POST /api/v3/account/switch``.

        Requires confirm=True. Warning: this leaves UTA and switches to a classic account.
        """
        require_confirmation(confirm)
        return self._native_private(
            "switch_to_classic_account", self._native_params(confirm=confirm)
        )

    def get_account_switch_status(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/switch-status``."""
        return self._native_private("get_account_switch_status", self._native_params())

    def get_futures_margin_mode_switch_quota(self) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/switch-union-usdt``."""
        return self._native_private("get_futures_margin_mode_switch_quota", self._native_params())

    def get_cross_margin_liquidation_orders(
        self,
        *,
        type_: str | None = None,
        product_symbol: str | None = None,
        from_coin: str | None = None,
        to_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/liquidation-order``."""
        return self._native_private(
            "get_cross_margin_liquidation_orders",
            self._native_params(
                type=type_,
                product_symbol=product_symbol,
                fromCoin=from_coin,
                toCoin=to_coin,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    def get_isolated_margin_liquidation_orders(
        self,
        *,
        type_: str | None = None,
        product_symbol: str | None = None,
        from_coin: str | None = None,
        to_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/liquidation-order``."""
        return self._native_private(
            "get_isolated_margin_liquidation_orders",
            self._native_params(
                type=type_,
                product_symbol=product_symbol,
                fromCoin=from_coin,
                toCoin=to_coin,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    def set_spot_deposit_account(self, account_type: str, coin: str) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/wallet/modify-deposit-account``."""
        return self._native_private(
            "set_spot_deposit_account", self._native_params(accountType=account_type, coin=coin)
        )

    def get_deposit_address(
        self, coin: str, *, chain: str | None = None, size: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/wallet/deposit-address``."""
        return self._native_private(
            "get_deposit_address", self._native_params(coin=coin, chain=chain, size=size)
        )

    def get_sub_account_deposit_address(
        self, sub_uid: str, coin: str, *, chain: str | None = None, size: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/wallet/subaccount-deposit-address``."""
        return self._native_private(
            "get_sub_account_deposit_address",
            self._native_params(subUid=sub_uid, coin=coin, chain=chain, size=size),
        )

    def get_sub_account_deposit_records(
        self,
        sub_uid: str,
        *,
        coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/wallet/subaccount-deposit-records``."""
        return self._native_private(
            "get_sub_account_deposit_records",
            self._native_params(
                subUid=sub_uid,
                coin=coin,
                startTime=start_time,
                endTime=end_time,
                idLessThan=id_less_than,
                limit=limit,
            ),
        )

    def set_uta_deposit_account(self, coin: str, account_type: str) -> dict[str, Any]:
        """Call ``POST /api/v3/account/deposit-account``."""
        return self._native_private(
            "set_uta_deposit_account", self._native_params(coin=coin, accountType=account_type)
        )

    def create_uta_sub_account(
        self, username: str, *, account_mode: str | None = None, note: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/user/create-sub``."""
        return self._native_private(
            "create_uta_sub_account",
            self._native_params(username=username, accountMode=account_mode, note=note),
        )

    def get_uta_deposit_address(
        self, coin: str, *, chain: str | None = None, size: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/deposit-address``."""
        return self._native_private(
            "get_uta_deposit_address", self._native_params(coin=coin, chain=chain, size=size)
        )

    def get_uta_sub_deposit_address(
        self, sub_uid: str, coin: str, *, chain: str | None = None, size: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/sub-deposit-address``."""
        return self._native_private(
            "get_uta_sub_deposit_address",
            self._native_params(subUid=sub_uid, coin=coin, chain=chain, size=size),
        )

    def get_uta_sub_deposit_records(
        self,
        sub_uid: str,
        start_time: int,
        end_time: int,
        *,
        coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/sub-deposit-records``."""
        return self._native_private(
            "get_uta_sub_deposit_records",
            self._native_params(
                subUid=sub_uid,
                startTime=start_time,
                endTime=end_time,
                coin=coin,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_uta_rate_limit_quota(
        self,
        category: str,
        *,
        uid: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/user/rate-limit-quota``."""
        return self._native_private(
            "get_uta_rate_limit_quota",
            self._native_params(category=category, uid=uid, cursor=cursor, limit=limit),
        )

    def uta_set_rate_limit_quota(
        self, category: str, uids: list[str], quota: str
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/user/set-rate-limit-quota``."""
        return self._native_private(
            "uta_set_rate_limit_quota",
            self._native_params(category=category, uids=uids, quota=quota),
        )

    def get_uta_small_assets_history(
        self,
        *,
        order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/convert/small-assets-history``."""
        return self._native_private(
            "get_uta_small_assets_history",
            self._native_params(
                orderId=order_id, startTime=start_time, endTime=end_time, limit=limit, cursor=cursor
            ),
        )

    def get_uta_small_assets(self) -> dict[str, Any]:
        """Call ``GET /api/v3/convert/small-assets``."""
        return self._native_private("get_uta_small_assets", self._native_params())

    def convert_uta_small_assets(self, from_coin_list: list[str]) -> dict[str, Any]:
        """Call ``POST /api/v3/convert/small-assets-trade``."""
        return self._native_private(
            "convert_uta_small_assets", self._native_params(fromCoinList=from_coin_list)
        )

    def delete_uta_subaccount(self, sub_uid: str, *, confirm: bool = False) -> dict[str, Any]:
        """
        Call ``POST /api/v3/user/delete-sub``.

        Requires confirm=True. This deletes the sub-account.
        """
        require_confirmation(confirm)
        return self._native_private(
            "delete_uta_subaccount", self._native_params(confirm=confirm, subUid=sub_uid)
        )

    def uta_freeze_sub(self, sub_uid: str, operation: str) -> dict[str, Any]:
        """Call ``POST /api/v3/user/freeze-sub``."""
        return self._native_private(
            "uta_freeze_sub", self._native_params(subUid=sub_uid, operation=operation)
        )

    def uta_create_sub_api(
        self,
        sub_uid: str,
        note: str,
        type_: str,
        passphrase: str,
        permissions: list[str],
        ips: list[str],
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/user/create-sub-api``."""
        return self._native_private(
            "uta_create_sub_api",
            self._native_params(
                subUid=sub_uid,
                note=note,
                type=type_,
                passphrase=passphrase,
                permissions=permissions,
                ips=ips,
            ),
        )

    def uta_update_sub_api(
        self,
        api_key: str,
        passphrase: str,
        *,
        type_: str | None = None,
        permissions: list[str] | None = None,
        ips: list[str] | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/user/update-sub-api``."""
        return self._native_private(
            "uta_update_sub_api",
            self._native_params(
                apiKey=api_key, passphrase=passphrase, type=type_, permissions=permissions, ips=ips
            ),
        )

    def uta_delete_sub_api(self, api_key: str) -> dict[str, Any]:
        """Call ``POST /api/v3/user/delete-sub-api``."""
        return self._native_private("uta_delete_sub_api", self._native_params(apiKey=api_key))

    def get_uta_sub_api_list(
        self, sub_uid: str, *, limit: int | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/user/sub-api-list``."""
        return self._native_private(
            "get_uta_sub_api_list", self._native_params(subUid=sub_uid, limit=limit, cursor=cursor)
        )

    def classic_create_virtual_subaccount(self, sub_account_list: list[str]) -> dict[str, Any]:
        """Call ``POST /api/v2/user/create-virtual-subaccount``."""
        return self._native_private(
            "classic_create_virtual_subaccount",
            self._native_params(subAccountList=sub_account_list),
        )

    def classic_create_virtual_subaccount_apikey(
        self,
        sub_account_uid: str,
        passphrase: str,
        label: str,
        perm_list: list[str],
        *,
        ip_list: list[str] | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/user/create-virtual-subaccount-apikey``."""
        return self._native_private(
            "classic_create_virtual_subaccount_apikey",
            self._native_params(
                subAccountUid=sub_account_uid,
                passphrase=passphrase,
                label=label,
                permList=perm_list,
                ipList=ip_list,
            ),
        )

    def classic_modify_virtual_subaccount(
        self, sub_account_uid: str, perm_list: list[str], status: str
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/user/modify-virtual-subaccount``."""
        return self._native_private(
            "classic_modify_virtual_subaccount",
            self._native_params(subAccountUid=sub_account_uid, permList=perm_list, status=status),
        )

    def classic_modify_virtual_subaccount_apikey(
        self,
        sub_account_uid: str,
        passphrase: str,
        label: str,
        sub_account_api_key: str,
        *,
        ip_list: list[str] | None = None,
        perm_list: list[str] | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/user/modify-virtual-subaccount-apikey``."""
        return self._native_private(
            "classic_modify_virtual_subaccount_apikey",
            self._native_params(
                subAccountUid=sub_account_uid,
                passphrase=passphrase,
                label=label,
                subAccountApiKey=sub_account_api_key,
                ipList=ip_list,
                permList=perm_list,
            ),
        )

    def get_classic_virtual_subaccount_list(
        self,
        *,
        limit: int | None = None,
        id_less_than: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/user/virtual-subaccount-list``."""
        return self._native_private(
            "get_classic_virtual_subaccount_list",
            self._native_params(limit=limit, idLessThan=id_less_than, status=status),
        )

    def get_classic_virtual_subaccount_apikey_list(self, sub_account_uid: str) -> dict[str, Any]:
        """Call ``GET /api/v2/user/virtual-subaccount-apikey-list``."""
        return self._native_private(
            "get_classic_virtual_subaccount_apikey_list",
            self._native_params(subAccountUid=sub_account_uid),
        )

    def get_classic_quoted_price(
        self,
        from_coin: str,
        to_coin: str,
        *,
        from_coin_size: str | None = None,
        to_coin_size: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/convert/quoted-price``."""
        return self._native_private(
            "get_classic_quoted_price",
            self._native_params(
                fromCoin=from_coin,
                toCoin=to_coin,
                fromCoinSize=from_coin_size,
                toCoinSize=to_coin_size,
            ),
        )

    def convert_classic_asset(
        self,
        from_coin: str,
        from_coin_size: str,
        cnvt_price: str,
        to_coin: str,
        to_coin_size: str,
        trace_id: str,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/convert/trade``."""
        return self._native_private(
            "convert_classic_asset",
            self._native_params(
                fromCoin=from_coin,
                fromCoinSize=from_coin_size,
                cnvtPrice=cnvt_price,
                toCoin=to_coin,
                toCoinSize=to_coin_size,
                traceId=trace_id,
            ),
        )

    def get_classic_convert_record(
        self,
        start_time: int,
        end_time: int,
        *,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/convert/convert-record``."""
        return self._native_private(
            "get_classic_convert_record",
            self._native_params(
                startTime=start_time, endTime=end_time, limit=limit, idLessThan=id_less_than
            ),
        )

    def move_uta_positions(
        self,
        from_uid: str,
        to_uid: str,
        category: str,
        position_list: list[dict[str, Any]],
        *,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """
        Move up to 10 cross-margin positions within the same account family.

        Requires a whitelisted master account. Bitget cancels pending orders for
        the moved symbols in both accounts. Only USDT/USDC futures are supported.
        Nested symbols use native exchange IDs. Execution uses the mark price.

        Requires confirm=True. This transfers positions and cancels related pending orders.
        """
        require_confirmation(confirm)
        return self._native_private(
            "move_uta_positions",
            self._native_params(
                confirm=confirm,
                fromUid=from_uid,
                toUid=to_uid,
                category=category,
                positionList=position_list,
            ),
        )

    def get_classic_account_bot_assets(self, *, account_type: str | None = None) -> dict[str, Any]:
        """
        GET /api/v2/account/bot-assets. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/classic-common-account/classic-common-account#bot-account
        """
        return self._native_private(
            "get_classic_account_bot_assets", self._native_params(accountType=account_type)
        )

    def get_classic_earn_elite_product(self) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/product. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-elite-product
        """
        return self._native_private("get_classic_earn_elite_product", self._native_params())

    def subscribe_classic_elite(
        self,
        *,
        product_sub_id: str,
        amount: str,
        coin: str | None = None,
        payment_account: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v2/earn/elite/subscribe. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#elite-subscribe
        """
        return self._native_private(
            "subscribe_classic_elite",
            self._native_params(
                productSubId=product_sub_id,
                amount=amount,
                coin=coin,
                paymentAccount=payment_account,
            ),
        )

    def get_classic_earn_elite_subscribe_result(self, *, order_id: str) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/subscribe-result. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-elite-subscribe-result
        """
        return self._native_private(
            "get_classic_earn_elite_subscribe_result", self._native_params(orderId=order_id)
        )

    def get_classic_earn_elite_subscribe_info(self, *, product_id: str) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/subscribe-info. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-elite-subscribe-info
        """
        return self._native_private(
            "get_classic_earn_elite_subscribe_info", self._native_params(productId=product_id)
        )

    def redeem_classic_elite(
        self,
        *,
        product_id: str,
        product_sub_id: str,
        redeem_type: str,
        amount: str,
        receive_account: str,
        advanced_settle: str | None = None,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v2/earn/elite/redeem. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#elite-redeem
        """
        return self._native_private(
            "redeem_classic_elite",
            self._native_params(
                productId=product_id,
                productSubId=product_sub_id,
                redeemType=redeem_type,
                amount=amount,
                receiveAccount=receive_account,
                advancedSettle=advanced_settle,
                coin=coin,
            ),
        )

    def get_classic_earn_elite_redeem_info(self, *, product_id: str) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/redeem-info. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-redeem-info
        """
        return self._native_private(
            "get_classic_earn_elite_redeem_info", self._native_params(productId=product_id)
        )

    def get_classic_earn_elite_assets(self) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/assets. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-elite-assets
        """
        return self._native_private("get_classic_earn_elite_assets", self._native_params())

    def get_classic_earn_elite_records(
        self,
        *,
        type_: str,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/records. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-elite-records
        """
        return self._native_private(
            "get_classic_earn_elite_records",
            self._native_params(
                type=type_, startTime=start_time, endTime=end_time, limit=limit, cursor=cursor
            ),
        )

    def borrow_classic_earn_loan(
        self,
        *,
        loan_coin: str,
        pledge_coin: str,
        daily: str,
        pledge_amount: str | None = None,
        loan_amount: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v2/earn/loan/borrow. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#borrow
        """
        return self._native_private(
            "borrow_classic_earn_loan",
            self._native_params(
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                daily=daily,
                pledgeAmount=pledge_amount,
                loanAmount=loan_amount,
            ),
        )

    def get_classic_earn_loan_ongoing_orders(
        self,
        *,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/ongoing-orders. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-loan-orders
        """
        return self._native_private(
            "get_classic_earn_loan_ongoing_orders",
            self._native_params(orderId=order_id, loanCoin=loan_coin, pledgeCoin=pledge_coin),
        )

    def repay_classic_earn_loan(
        self,
        *,
        order_id: str,
        repay_all: str,
        amount: str | None = None,
        repay_unlock: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v2/earn/loan/repay. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#repay
        """
        return self._native_private(
            "repay_classic_earn_loan",
            self._native_params(
                orderId=order_id, repayAll=repay_all, amount=amount, repayUnlock=repay_unlock
            ),
        )

    def get_classic_earn_loan_repay_history(
        self,
        *,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/repay-history. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-repay-history
        """
        return self._native_private(
            "get_classic_earn_loan_repay_history",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                pageNo=page_no,
                pageSize=page_size,
            ),
        )

    def classic_earn_loan_revise_pledge(
        self, *, order_id: str, amount: str, pledge_coin: str, revise_type: str
    ) -> dict[str, Any]:
        """
        POST /api/v2/earn/loan/revise-pledge. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#modify-pledge-rate
        """
        return self._native_private(
            "classic_earn_loan_revise_pledge",
            self._native_params(
                orderId=order_id, amount=amount, pledgeCoin=pledge_coin, reviseType=revise_type
            ),
        )

    def get_classic_earn_loan_revise_history(
        self,
        *,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        revise_side: str | None = None,
        pledge_coin: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/revise-history. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-pledge-rate-history
        """
        return self._native_private(
            "get_classic_earn_loan_revise_history",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                reviseSide=revise_side,
                pledgeCoin=pledge_coin,
                pageNo=page_no,
                pageSize=page_size,
            ),
        )

    def get_classic_earn_loan_borrow_history(
        self,
        *,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
        status: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/borrow-history. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-loan-history
        """
        return self._native_private(
            "get_classic_earn_loan_borrow_history",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                status=status,
                pageNo=page_no,
                pageSize=page_size,
            ),
        )

    def get_classic_earn_loan_debts(self) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/debts. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-debts
        """
        return self._native_private("get_classic_earn_loan_debts", self._native_params())

    def get_classic_earn_loan_reduces(
        self,
        *,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
        status: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/reduces. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-liquidation-records
        """
        return self._native_private(
            "get_classic_earn_loan_reduces",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                status=status,
                pageNo=page_no,
                pageSize=page_size,
            ),
        )

    def uta_trade_grid_add_investment(
        self,
        *,
        category: str,
        bot_id: str,
        coin: str,
        size: str,
        funds_source: list[str],
        adjust_type: str | None = None,
        reinvest_profit: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/add-investment. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#add-investment-amount
        """
        return self._native_private(
            "uta_trade_grid_add_investment",
            self._native_params(
                category=category,
                botId=bot_id,
                coin=coin,
                size=size,
                fundsSource=funds_source,
                adjustType=adjust_type,
                reinvestProfit=reinvest_profit,
            ),
        )

    def get_uta_trade_grid_bot_detail(self, *, bot_id: str) -> dict[str, Any]:
        """
        GET /api/v3/trade/grid/bot-detail. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#get-grid-bot-detail
        """
        return self._native_private(
            "get_uta_trade_grid_bot_detail", self._native_params(botId=bot_id)
        )

    def uta_trade_grid_close_bot(self, *, bot_id: str) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/close-bot. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#close-grid-bot
        """
        return self._native_private("uta_trade_grid_close_bot", self._native_params(botId=bot_id))

    def uta_trade_grid_create_bot(
        self,
        *,
        category: str,
        symbol: str,
        max_price: str,
        min_price: str,
        grid_num: str,
        grid_order_mode: str,
        investment_amount: list[dict[str, str]],
        funds_source: list[str],
        slippage: str,
        auto_transfer_profits: str,
        grid_type: str | None = None,
        leverage: str | None = None,
        auto_reserve_margin: str | None = None,
        reserved_margin: str | None = None,
        trigger_condition: str | None = None,
        trigger_params: list[dict[str, str]] | None = None,
        trigger_price: str | None = None,
        termination_condition: str | None = None,
        termination_params: list[dict[str, str]] | None = None,
        termination_sell: str | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        trailing_grid: str | None = None,
        moving_average_gains: str | None = None,
        stop_upward_price: str | None = None,
        hodl_mode: str | None = None,
        market_open: str | None = None,
        loss_reserve: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/create-bot. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#create-grid-bot
        """
        return self._native_private(
            "uta_trade_grid_create_bot",
            self._native_params(
                category=category,
                symbol=symbol,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
                gridOrderMode=grid_order_mode,
                investmentAmount=investment_amount,
                fundsSource=funds_source,
                slippage=slippage,
                autoTransferProfits=auto_transfer_profits,
                gridType=grid_type,
                leverage=leverage,
                autoReserveMargin=auto_reserve_margin,
                reservedMargin=reserved_margin,
                triggerCondition=trigger_condition,
                triggerParams=trigger_params,
                triggerPrice=trigger_price,
                terminationCondition=termination_condition,
                terminationParams=termination_params,
                terminationSell=termination_sell,
                stopLoss=stop_loss,
                takeProfit=take_profit,
                trailingGrid=trailing_grid,
                movingAverageGains=moving_average_gains,
                stopUpwardPrice=stop_upward_price,
                hodlMode=hodl_mode,
                marketOpen=market_open,
                lossReserve=loss_reserve,
            ),
        )

    def uta_trade_grid_create_neutral_bot(
        self,
        *,
        category: str,
        symbol: str,
        max_price: str,
        min_price: str,
        grid_num: str,
        grid_order_mode: str,
        funds_source: list[str],
        leverage: str | None = None,
        investment_amount: list[dict[str, str]] | None = None,
        trigger_price: str | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        auto_transfer_profits: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/create-neutral-bot. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#create-neutral-grid-bot
        """
        return self._native_private(
            "uta_trade_grid_create_neutral_bot",
            self._native_params(
                category=category,
                symbol=symbol,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
                gridOrderMode=grid_order_mode,
                fundsSource=funds_source,
                leverage=leverage,
                investmentAmount=investment_amount,
                triggerPrice=trigger_price,
                stopLoss=stop_loss,
                takeProfit=take_profit,
                autoTransferProfits=auto_transfer_profits,
            ),
        )

    def get_uta_trade_grid_list_details(self, *, category: str, bot_id: str) -> dict[str, Any]:
        """
        GET /api/v3/trade/grid/list-details. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#get-grid-bot-order-details
        """
        return self._native_private(
            "get_uta_trade_grid_list_details", self._native_params(category=category, botId=bot_id)
        )

    def uta_trade_grid_modify_bot(
        self,
        *,
        bot_id: str,
        category: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        termination_condition: str | None = None,
        termination_params: list[dict[str, str]] | None = None,
        hodl_mode: str | None = None,
        auto_transfer_profits: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/modify-bot. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#modify-grid-bot-parameters
        """
        return self._native_private(
            "uta_trade_grid_modify_bot",
            self._native_params(
                botId=bot_id,
                category=category,
                takeProfit=take_profit,
                stopLoss=stop_loss,
                terminationCondition=termination_condition,
                terminationParams=termination_params,
                hodlMode=hodl_mode,
                autoTransferProfits=auto_transfer_profits,
            ),
        )

    def uta_trade_grid_modify_grid_interval(
        self, *, category: str, bot_id: str, max_price: str, min_price: str, grid_num: str
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/modify-grid-interval. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#modify-grid-interval-and-grid-number
        """
        return self._native_private(
            "uta_trade_grid_modify_grid_interval",
            self._native_params(
                category=category,
                botId=bot_id,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
            ),
        )

    def uta_trade_grid_modify_neutral_bot(
        self,
        *,
        bot_id: str,
        category: str,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        auto_transfer_profits: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/modify-neutral-bot. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#modify-neutral-grid-bot-parameters
        """
        return self._native_private(
            "uta_trade_grid_modify_neutral_bot",
            self._native_params(
                botId=bot_id,
                category=category,
                takeProfit=take_profit,
                stopLoss=stop_loss,
                autoTransferProfits=auto_transfer_profits,
            ),
        )

    def uta_trade_grid_modify_neutral_grid_interval(
        self, *, category: str, bot_id: str, max_price: str, min_price: str, grid_num: str
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/modify-neutral-grid-interval. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#modify-neutral-grid-interval-and-grid-number
        """
        return self._native_private(
            "uta_trade_grid_modify_neutral_grid_interval",
            self._native_params(
                category=category,
                botId=bot_id,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
            ),
        )

    def get_uta_trade_grid_neutral_bot_detail(self, *, bot_id: str) -> dict[str, Any]:
        """
        GET /api/v3/trade/grid/neutral-bot-detail. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#get-neutral-grid-bot-detail
        """
        return self._native_private(
            "get_uta_trade_grid_neutral_bot_detail", self._native_params(botId=bot_id)
        )

    def get_uta_trade_grid_neutral_list_details(
        self, *, category: str, bot_id: str
    ) -> dict[str, Any]:
        """
        GET /api/v3/trade/grid/neutral-list-details. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#get-neutral-grid-bot-order-details
        """
        return self._native_private(
            "get_uta_trade_grid_neutral_list_details",
            self._native_params(category=category, botId=bot_id),
        )

    def uta_trade_grid_validate_neutral(
        self,
        *,
        category: str,
        symbol: str,
        max_price: str,
        min_price: str,
        grid_num: str,
        grid_order_mode: str,
        leverage: str | None = None,
        investment_amount: list[dict[str, str]] | None = None,
        trigger_price: str | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        auto_transfer_profits: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/validate-neutral. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#validate-neutral-grid-parameters
        """
        return self._native_private(
            "uta_trade_grid_validate_neutral",
            self._native_params(
                category=category,
                symbol=symbol,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
                gridOrderMode=grid_order_mode,
                leverage=leverage,
                investmentAmount=investment_amount,
                triggerPrice=trigger_price,
                stopLoss=stop_loss,
                takeProfit=take_profit,
                autoTransferProfits=auto_transfer_profits,
            ),
        )

    def uta_trade_grid_validate(
        self,
        *,
        category: str,
        symbol: str,
        max_price: str,
        min_price: str,
        grid_num: str,
        grid_order_mode: str,
        investment_amount: list[dict[str, str]],
        auto_transfer_profits: str,
        grid_type: str | None = None,
        leverage: str | None = None,
        reserved_margin: str | None = None,
        trigger_condition: str | None = None,
        trigger_params: list[dict[str, str]] | None = None,
        trigger_price: str | None = None,
        termination_condition: str | None = None,
        termination_params: list[dict[str, str]] | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        trailing_grid: str | None = None,
        moving_average_gains: str | None = None,
        stop_upward_price: str | None = None,
        hodl_mode: str | None = None,
        market_open: str | None = None,
        loss_reserve: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/validate. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#validate-grid-parameters
        """
        return self._native_private(
            "uta_trade_grid_validate",
            self._native_params(
                category=category,
                symbol=symbol,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
                gridOrderMode=grid_order_mode,
                investmentAmount=investment_amount,
                autoTransferProfits=auto_transfer_profits,
                gridType=grid_type,
                leverage=leverage,
                reservedMargin=reserved_margin,
                triggerCondition=trigger_condition,
                triggerParams=trigger_params,
                triggerPrice=trigger_price,
                terminationCondition=termination_condition,
                terminationParams=termination_params,
                stopLoss=stop_loss,
                takeProfit=take_profit,
                trailingGrid=trailing_grid,
                movingAverageGains=moving_average_gains,
                stopUpwardPrice=stop_upward_price,
                hodlMode=hodl_mode,
                marketOpen=market_open,
                lossReserve=loss_reserve,
            ),
        )

    def create_uta_agent_sub_account(
        self, *, username: str, passphrase: str, note: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Create Agent Sub-account.

        The response includes an API secret. Do not log or persist the secret in plaintext.
        Source: https://www.bitget.com/docs/catalog/account/sub-accounts#create-agent-sub-account
        """
        return self._native_private(
            "create_uta_agent_sub_account",
            self._native_params(username=username, passphrase=passphrase, note=note),
        )

    def create_classic_agent_sub_account(
        self, *, username: str, passphrase: str, note: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Create Agent Subaccount.

        The response includes an API secret. Do not log or persist the secret in plaintext.
        Source: https://www.bitget.com/docs/catalog/classic-common-vsubaccount/classic-common-vsubaccount#create-agent-subaccount
        """
        return self._native_private(
            "create_classic_agent_sub_account",
            self._native_params(username=username, passphrase=passphrase, note=note),
        )
