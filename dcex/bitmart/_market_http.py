"""Bitmart market data HTTP client backed by Rust."""

from typing import Any

from .._native_http import NativeResponse
from ..utils.common import Common
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Market data HTTP client for Bitmart."""

    def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed BitMart public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("BitMart native client is required for public market methods.")
        status, headers, body = self._native_client.public_request(method_name, params)
        response = NativeResponse(status, dict(headers), bytes(body))
        self._store_response_headers(response)
        return response.json()

    def _exchange_symbol(self, product_symbol: str, *, spot: bool) -> str:
        """Map product symbol through PTM when available."""
        if hasattr(self, "ptm"):
            return self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)
        parts = product_symbol.split("-")
        if len(parts) >= 3:
            return f"{parts[0]}_{parts[1]}" if spot else f"{parts[0]}{parts[1]}"
        return product_symbol

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            params.append((key, str(value)))
        return params

    def get_spot_currencies(self) -> dict[str, Any]:
        """Get all available spot currencies."""
        return self._native_public("get_spot_currencies", [])

    def get_trading_pairs(self) -> dict[str, Any]:
        """Get all available trading pairs."""
        return self._native_public("get_trading_pairs", [])

    def get_trading_pairs_details(self) -> dict[str, Any]:
        """Get detailed information for all trading pairs."""
        return self._native_public("get_trading_pairs_details", [])

    def get_ticker_of_all_pairs(self) -> dict[str, Any]:
        """Get ticker information for all trading pairs."""
        return self._native_public("get_ticker_of_all_pairs", [])

    def get_ticker_of_a_pair(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Get ticker information for a specific trading pair."""
        return self._native_public(
            "get_ticker_of_a_pair",
            self._params(product_symbol=self._exchange_symbol(product_symbol, spot=True)),
        )

    def get_spot_kline(
        self,
        product_symbol: str,
        interval: str,
        before: int | None = None,
        after: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get spot kline data for a trading pair."""
        return self._native_public(
            "get_spot_kline",
            self._params(
                product_symbol=self._exchange_symbol(product_symbol, spot=True),
                interval=interval,
                before=before,
                after=after,
                limit=limit,
            ),
        )

    def get_contracts_details(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get futures contract details."""
        return self._native_public(
            "get_contracts_details",
            self._params(
                product_symbol=self._exchange_symbol(product_symbol, spot=False)
                if product_symbol is not None
                else None,
            ),
        )

    def get_depth(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Get order book depth for a futures contract."""
        return self._native_public(
            "get_depth",
            self._params(product_symbol=self._exchange_symbol(product_symbol, spot=False)),
        )

    def get_contract_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int,
        end_time: int,
    ) -> dict[str, Any]:
        """Get futures contract kline data."""
        return self._native_public(
            "get_contract_kline",
            self._params(
                product_symbol=self._exchange_symbol(product_symbol, spot=False),
                interval=interval,
                start_time=start_time,
                end_time=end_time,
            ),
        )

    def get_open_interest(self, product_symbol: str) -> dict[str, Any]:
        """Get futures contract open interest."""
        return self._native_public(
            "get_open_interest",
            self._params(product_symbol=self._exchange_symbol(product_symbol, spot=False)),
        )

    def get_mark_price_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int,
        end_time: int,
    ) -> dict[str, Any]:
        """Get futures mark price kline data."""
        return self._native_public(
            "get_mark_price_kline",
            self._params(
                product_symbol=self._exchange_symbol(product_symbol, spot=False),
                interval=interval,
                start_time=start_time,
                end_time=end_time,
            ),
        )

    def get_leverage_bracket(self, product_symbol: str) -> dict[str, Any]:
        """Get futures contract leverage bracket."""
        return self._native_public(
            "get_leverage_bracket",
            self._params(product_symbol=self._exchange_symbol(product_symbol, spot=False)),
        )

    def get_current_funding_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Get current funding rate for a futures contract."""
        return self._native_public(
            "get_current_funding_rate",
            self._params(product_symbol=self._exchange_symbol(product_symbol, spot=False)),
        )

    def get_funding_rate_history(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get funding rate history for a futures contract."""
        return self._native_public(
            "get_funding_rate_history",
            self._params(
                product_symbol=self._exchange_symbol(product_symbol, spot=False),
                limit=limit,
            ),
        )
