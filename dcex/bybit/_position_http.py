"""Bybit position HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class PositionHTTP(HTTPManager):
    """HTTP client for Bybit position operations."""

    def get_positions(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        baseCoin: str | None = None,
        settleCoin: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get positions list."""
        return self._native_private(
            "get_positions",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                baseCoin=baseCoin,
                settleCoin=settleCoin,
                limit=limit,
                cursor=cursor,
            ),
        )

    def set_leverage(
        self,
        product_symbol: str,
        leverage: str,
    ) -> dict[str, Any]:
        """Set leverage for a product."""
        return self._native_private(
            "set_leverage",
            self._native_params(product_symbol=product_symbol, leverage=leverage),
        )

    def switch_position_mode(
        self,
        mode: int,
        product_symbol: str | None = None,
        coin: str | None = None,
        category: str = "linear",
    ) -> dict[str, Any]:
        """Switch position mode."""
        return self._native_private(
            "switch_position_mode",
            self._native_params(
                mode=mode,
                product_symbol=product_symbol,
                coin=coin,
                category=category,
            ),
        )

    def set_trading_stop(
        self,
        product_symbol: str,
        tpsl_mode: str,
        position_idx: int,
        *,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        trailing_stop: str | None = None,
        tp_trigger_by: str | None = None,
        sl_trigger_by: str | None = None,
        active_price: str | None = None,
        tp_order_type: str | None = None,
        sl_order_type: str | None = None,
        tp_limit_price: str | None = None,
        sl_limit_price: str | None = None,
        tp_size: str | None = None,
        sl_size: str | None = None,
    ) -> dict[str, Any]:
        """Set position take-profit, stop-loss, or trailing-stop."""
        return self._native_private(
            "set_trading_stop",
            self._native_params(
                product_symbol=product_symbol,
                tpslMode=tpsl_mode,
                positionIdx=position_idx,
                takeProfit=take_profit,
                stopLoss=stop_loss,
                trailingStop=trailing_stop,
                tpTriggerBy=tp_trigger_by,
                slTriggerBy=sl_trigger_by,
                activePrice=active_price,
                tpOrderType=tp_order_type,
                slOrderType=sl_order_type,
                tpLimitPrice=tp_limit_price,
                slLimitPrice=sl_limit_price,
                tpSize=tp_size,
                slSize=sl_size,
            ),
        )

    def add_position_margin(
        self, product_symbol: str, margin: str, position_idx: int | None = None
    ) -> dict[str, Any]:
        """Add or reduce isolated-position margin (negative margin reduces it)."""
        return self._native_private(
            "add_position_margin",
            self._native_params(
                product_symbol=product_symbol,
                margin=margin,
                positionIdx=position_idx,
            ),
        )

    def set_auto_add_margin(
        self, product_symbol: str, enabled: bool, position_idx: int | None = None
    ) -> dict[str, Any]:
        """Enable or disable automatic margin top-ups for a linear position."""
        return self._native_private(
            "set_auto_add_margin",
            self._native_params(
                product_symbol=product_symbol,
                autoAddMargin=int(enabled),
                positionIdx=position_idx,
            ),
        )

    def get_closed_pnl(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get closed PnL history."""
        return self._native_private(
            "get_closed_pnl",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )
