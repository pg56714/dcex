"""Bybit position HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class PositionHTTP(HTTPManager):
    """HTTP client for Bybit position operations."""

    def get_positions(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        settleCoin: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get positions list."""
        return self._native_private(
            "get_positions",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                settleCoin=settleCoin,
                limit=limit,
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
    ) -> dict[str, Any]:
        """Switch position mode."""
        return self._native_private(
            "switch_position_mode",
            self._native_params(mode=mode, product_symbol=product_symbol, coin=coin),
        )

    def get_closed_pnl(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get closed PnL history."""
        return self._native_private(
            "get_closed_pnl",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                startTime=startTime,
                limit=limit,
            ),
        )
