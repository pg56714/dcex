"""BitMart async market data HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ...utils.common import Common
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """HTTP client for BitMart market-related API endpoints."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed BitMart public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("BitMart native client is required for public market methods.")
        response, data = await request_native_json_async(
            self._native_client,
            "public_request",
            method_name,
            params,
        )
        self._store_response_headers(response)
        return data

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

    async def get_spot_currencies(self) -> dict[str, Any]:
        """Get spot currencies."""
        return await self._native_public("get_spot_currencies", [])

    async def get_trading_pairs(self) -> dict[str, Any]:
        """Get trading pairs."""
        return await self._native_public("get_trading_pairs", [])

    async def get_trading_pairs_details(self) -> dict[str, Any]:
        """Get trading pairs details."""
        return await self._native_public("get_trading_pairs_details", [])

    async def get_ticker_of_all_pairs(self) -> dict[str, Any]:
        """Get ticker of all pairs."""
        return await self._native_public("get_ticker_of_all_pairs", [])

    async def get_ticker_of_a_pair(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Get ticker of a specific pair."""
        return await self._native_public(
            "get_ticker_of_a_pair",
            self._params(product_symbol=self._exchange_symbol(product_symbol, spot=True)),
        )

    async def get_spot_kline(
        self,
        product_symbol: str,
        interval: str,
        before: int | None = None,
        after: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get spot kline data."""
        return await self._native_public(
            "get_spot_kline",
            self._params(
                product_symbol=self._exchange_symbol(product_symbol, spot=True),
                interval=interval,
                before=before,
                after=after,
                limit=limit,
            ),
        )

    async def get_contracts_details(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get contracts details."""
        return await self._native_public(
            "get_contracts_details",
            self._params(
                product_symbol=self._exchange_symbol(product_symbol, spot=False)
                if product_symbol is not None
                else None,
            ),
        )

    async def get_depth(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Get order book depth."""
        return await self._native_public(
            "get_depth",
            self._params(product_symbol=self._exchange_symbol(product_symbol, spot=False)),
        )

    async def get_contract_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int,
        end_time: int,
    ) -> dict[str, Any]:
        """Get contract kline data."""
        return await self._native_public(
            "get_contract_kline",
            self._params(
                product_symbol=self._exchange_symbol(product_symbol, spot=False),
                interval=interval,
                start_time=start_time,
                end_time=end_time,
            ),
        )

    async def get_open_interest(self, product_symbol: str) -> dict[str, Any]:
        """Get futures contract open interest."""
        return await self._native_public(
            "get_open_interest",
            self._params(product_symbol=self._exchange_symbol(product_symbol, spot=False)),
        )

    async def get_mark_price_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int,
        end_time: int,
    ) -> dict[str, Any]:
        """Get futures mark price kline data."""
        return await self._native_public(
            "get_mark_price_kline",
            self._params(
                product_symbol=self._exchange_symbol(product_symbol, spot=False),
                interval=interval,
                start_time=start_time,
                end_time=end_time,
            ),
        )

    async def get_leverage_bracket(self, product_symbol: str) -> dict[str, Any]:
        """Get futures contract leverage bracket."""
        return await self._native_public(
            "get_leverage_bracket",
            self._params(product_symbol=self._exchange_symbol(product_symbol, spot=False)),
        )

    async def get_current_funding_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Get current funding rate."""
        return await self._native_public(
            "get_current_funding_rate",
            self._params(product_symbol=self._exchange_symbol(product_symbol, spot=False)),
        )

    async def get_funding_rate_history(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get funding rate history."""
        return await self._native_public(
            "get_funding_rate_history",
            self._params(
                product_symbol=self._exchange_symbol(product_symbol, spot=False),
                limit=limit,
            ),
        )
