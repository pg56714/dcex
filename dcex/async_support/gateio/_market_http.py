"""Gate.io market data async HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Gate.io async market data HTTP client."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Gate.io public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Gate.io native client is required for public market methods.")
        response, data = await request_native_json_async(
            self._native_client,
            "public_request",
            method_name,
            params,
        )
        self._store_response_headers(response)
        return data

    async def get_all_futures_contracts(
        self,
        ccy: str = "usdt",
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """Get all futures contracts."""
        return await self._native_public(
            "get_all_futures_contracts",
            self._native_params(settle=ccy, limit=limit, offset=offset),
        )

    async def get_a_single_futures_contract(
        self,
        product_symbol: str,
        ccy: str = "usdt",
    ) -> dict[str, Any]:
        """Get a single futures contract information."""
        return await self._native_public(
            "get_a_single_futures_contract",
            self._native_params(settle=ccy, product_symbol=product_symbol),
        )

    async def get_contract_order_book(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        path: str = "futures",
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool = False,
    ) -> dict[str, Any]:
        """Get contract order book."""
        return await self._native_public(
            "get_contract_order_book",
            self._native_params(
                settle=ccy,
                path=path,
                product_symbol=product_symbol,
                interval=interval,
                limit=limit,
                with_id=with_id if with_id else None,
            ),
        )

    async def get_contract_kline(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        path: str = "futures",
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        limit: int | None = None,
        interval: str | None = None,
    ) -> dict[str, Any]:
        """Get contract kline/candlestick data."""
        return await self._native_public(
            "get_contract_kline",
            self._native_params(
                settle=ccy,
                path=path,
                product_symbol=product_symbol,
                from_=from_timestamp,
                to=to_timestamp,
                limit=limit,
                interval=interval,
            ),
        )

    async def get_contract_list_tickers(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        """Get contract ticker information."""
        return await self._native_public(
            "get_contract_list_tickers",
            self._native_params(
                settle=ccy,
                path=path,
                product_symbol=product_symbol,
            ),
        )

    async def get_futures_funding_rate_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        limit: int | None = None,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
    ) -> dict[str, Any]:
        """Get futures funding rate history."""
        return await self._native_public(
            "get_futures_funding_rate_history",
            self._native_params(
                settle=ccy,
                product_symbol=product_symbol,
                limit=limit,
                from_=from_timestamp,
                to=to_timestamp,
            ),
        )

    async def get_futures_contract_stats(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        interval: str | None = None,
        from_timestamp: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get futures contract statistics."""
        return await self._native_public(
            "get_futures_contract_stats",
            self._native_params(
                settle=ccy,
                product_symbol=product_symbol,
                interval=interval,
                from_=from_timestamp,
                limit=limit,
            ),
        )

    async def get_all_delivery_contracts(self) -> dict[str, Any]:
        """Get all delivery contracts."""
        return await self._native_public(
            "get_all_delivery_contracts",
            self._native_params(settle="usdt"),
        )

    async def get_spot_all_currency_pairs(self) -> dict[str, Any]:
        """Get all spot currency pairs."""
        return await self._native_public("get_spot_all_currency_pairs", [])

    async def get_spot_order_book(
        self,
        product_symbol: str,
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool = False,
    ) -> dict[str, Any]:
        """Get spot order book."""
        return await self._native_public(
            "get_spot_order_book",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                limit=limit,
                with_id=with_id if with_id else None,
            ),
        )

    async def get_spot_kline(
        self,
        product_symbol: str,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        limit: int | None = None,
        interval: str | None = None,
    ) -> dict[str, Any]:
        """Get spot kline/candlestick data."""
        return await self._native_public(
            "get_spot_kline",
            self._native_params(
                product_symbol=product_symbol,
                from_=from_timestamp,
                to=to_timestamp,
                limit=limit,
                interval=interval,
            ),
        )

    async def get_spot_list_tickers(
        self,
        product_symbol: str,
        timezone: str | None = None,
    ) -> dict[str, Any]:
        """Get spot ticker information."""
        return await self._native_public(
            "get_spot_list_tickers",
            self._native_params(
                product_symbol=product_symbol,
                timezone=timezone,
            ),
        )
