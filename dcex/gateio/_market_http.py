"""Gate.io market data HTTP client backed by Rust."""

from typing import Any

from .._native_http import request_native_json
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Gate.io Market HTTP client for public market data operations."""

    def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Gate.io public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Gate.io native client is required for public market methods.")
        response, data = request_native_json(
            self._native_client,
            "public_request",
            method_name,
            params,
        )
        self._store_response_headers(response)
        return data

    def get_all_futures_contracts(
        self,
        ccy: str = "usdt",
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """Get all futures contracts for a settlement currency."""
        return self._native_public(
            "get_all_futures_contracts",
            self._native_params(settle=ccy, limit=limit, offset=offset),
        )

    def get_futures_insurance(self, ccy: str = "usdt") -> dict[str, Any]:
        """Retrieve Gate.io futures insurance fund history."""
        return self._native_public("get_futures_insurance", self._native_params(ccy=ccy))

    def get_futures_premium_index(self, product_symbol: str, ccy: str = "usdt") -> dict[str, Any]:
        """Retrieve Gate.io futures premium-index data."""
        return self._native_public(
            "get_futures_premium_index",
            self._native_params(ccy=ccy, product_symbol=product_symbol),
        )

    def get_a_single_futures_contract(
        self,
        product_symbol: str,
        ccy: str = "usdt",
    ) -> dict[str, Any]:
        """Get information for a single futures contract."""
        return self._native_public(
            "get_a_single_futures_contract",
            self._native_params(settle=ccy, product_symbol=product_symbol),
        )

    def get_contract_order_book(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        path: str = "futures",
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool = False,
    ) -> dict[str, Any]:
        """Get order book for a futures or delivery contract."""
        return self._native_public(
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

    def get_contract_kline(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        path: str = "futures",
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        limit: int | None = None,
        interval: str | None = None,
    ) -> dict[str, Any]:
        """Get kline/candlestick data for a futures or delivery contract."""
        return self._native_public(
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

    def get_contract_list_tickers(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        """Get ticker information for a futures or delivery contract."""
        return self._native_public(
            "get_contract_list_tickers",
            self._native_params(
                settle=ccy,
                path=path,
                product_symbol=product_symbol,
            ),
        )

    def get_futures_funding_rate_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        limit: int | None = None,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
    ) -> dict[str, Any]:
        """Get funding rate history for a futures contract."""
        return self._native_public(
            "get_futures_funding_rate_history",
            self._native_params(
                settle=ccy,
                product_symbol=product_symbol,
                limit=limit,
                from_=from_timestamp,
                to=to_timestamp,
            ),
        )

    def get_futures_contract_stats(
        self,
        product_symbol: str,
        ccy: str = "usdt",
        interval: str | None = None,
        from_timestamp: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get futures contract statistics."""
        return self._native_public(
            "get_futures_contract_stats",
            self._native_params(
                settle=ccy,
                product_symbol=product_symbol,
                interval=interval,
                from_=from_timestamp,
                limit=limit,
            ),
        )

    def get_all_delivery_contracts(self) -> dict[str, Any]:
        """Get all delivery contracts."""
        return self._native_public(
            "get_all_delivery_contracts",
            self._native_params(settle="usdt"),
        )

    def get_spot_all_currency_pairs(self) -> dict[str, Any]:
        """Get all spot currency pairs."""
        return self._native_public("get_spot_all_currency_pairs", [])

    def get_spot_order_book(
        self,
        product_symbol: str,
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool = False,
    ) -> dict[str, Any]:
        """Get order book for a spot currency pair."""
        return self._native_public(
            "get_spot_order_book",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                limit=limit,
                with_id=with_id if with_id else None,
            ),
        )

    def get_spot_kline(
        self,
        product_symbol: str,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        limit: int | None = None,
        interval: str | None = None,
    ) -> dict[str, Any]:
        """Get kline/candlestick data for a spot currency pair."""
        return self._native_public(
            "get_spot_kline",
            self._native_params(
                product_symbol=product_symbol,
                from_=from_timestamp,
                to=to_timestamp,
                limit=limit,
                interval=interval,
            ),
        )

    def get_spot_list_tickers(
        self,
        product_symbol: str,
        timezone: str | None = None,
    ) -> dict[str, Any]:
        """Get ticker information for a spot currency pair."""
        return self._native_public(
            "get_spot_list_tickers",
            self._native_params(
                product_symbol=product_symbol,
                timezone=timezone,
            ),
        )
