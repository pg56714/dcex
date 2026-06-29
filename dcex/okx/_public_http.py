"""OKX public HTTP client backed by Rust."""

from typing import Any

from .._native_http import request_native_json
from ..utils.common import Common
from ._http_manager import HTTPManager


class PublicHTTP(HTTPManager):
    """HTTP client for OKX public data operations."""

    def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed OKX public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("OKX native client is required for public methods.")
        response, data = request_native_json(
            self._native_client,
            "public_request",
            method_name,
            params,
        )
        self._store_response_headers(response)
        return data

    def _exchange_symbol(self, product_symbol: str) -> str:
        """Map product symbol through PTM when available."""
        if hasattr(self, "ptm"):
            return self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        parts = product_symbol.split("-")
        if len(parts) >= 3:
            return f"{parts[0]}-{parts[1]}" if parts[2] == "SPOT" else product_symbol
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

    def get_public_instruments(
        self,
        instType: str,
        uly: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get public instrument information."""
        inst_id = self._exchange_symbol(product_symbol) if product_symbol is not None else None
        return self._native_public(
            "get_public_instruments",
            self._params(instType=instType, uly=uly, instFamily=instFamily, instId=inst_id),
        )

    def get_funding_rate(self, product_symbol: str) -> dict[str, Any]:
        """Get current funding rate for a trading pair."""
        return self._native_public(
            "get_funding_rate",
            self._params(instId=self._exchange_symbol(product_symbol)),
        )

    def get_funding_rate_history(
        self,
        product_symbol: str,
        before: str | None = None,
        after: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Get historical funding rates for a trading pair."""
        return self._native_public(
            "get_funding_rate_history",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                before=before,
                after=after,
                limit=limit,
            ),
        )

    def get_open_interest(
        self,
        instType: str = "SWAP",
        uly: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get public open interest data."""
        inst_id = self._exchange_symbol(product_symbol) if product_symbol is not None else None
        return self._native_public(
            "get_open_interest",
            self._params(instType=instType, uly=uly, instFamily=instFamily, instId=inst_id),
        )

    def get_position_tiers(
        self,
        instType: str = "SWAP",
        tdMode: str = "isolated",
        instFamily: str | None = None,
        uly: str | None = None,
        product_symbol: str | None = None,
        ccy: str | None = None,
        tier: str | None = None,
    ) -> dict[str, Any]:
        """Get position tiers information."""
        inst_id = self._exchange_symbol(product_symbol) if product_symbol is not None else None
        if inst_id is not None and instFamily is None and uly is None:
            symbol_parts = inst_id.split("-")
            if len(symbol_parts) >= 2:
                instFamily = "-".join(symbol_parts[:2])
        return self._native_public(
            "get_position_tiers",
            self._params(
                instType=instType,
                tdMode=tdMode,
                instFamily=instFamily,
                uly=uly,
                instId=inst_id,
                ccy=ccy,
                tier=tier,
            ),
        )

    def get_trading_data_support_coin(self) -> dict[str, Any]:
        """Get currencies supported by OKX trading data endpoints."""
        return self._native_public("get_trading_data_support_coin", [])

    def get_taker_volume(
        self,
        ccy: str,
        instType: str = "SPOT",
        begin: int | None = None,
        end: int | None = None,
        period: str = "5m",
    ) -> dict[str, Any]:
        """Get taker volume by currency and instrument type."""
        return self._native_public(
            "get_taker_volume",
            self._params(ccy=ccy, instType=instType, begin=begin, end=end, period=period),
        )

    def get_contract_taker_volume(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get contract taker volume history."""
        return self._native_public(
            "get_contract_taker_volume",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                period=period,
                begin=begin,
                end=end,
            ),
        )

    def get_long_short_ratio(
        self,
        ccy: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get long and short account ratio by currency."""
        return self._native_public(
            "get_long_short_ratio",
            self._params(ccy=ccy, period=period, begin=begin, end=end),
        )

    def get_contract_long_short_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get contract long and short account ratio."""
        return self._native_public(
            "get_contract_long_short_ratio",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                period=period,
                begin=begin,
                end=end,
            ),
        )

    def get_top_trader_long_short_account_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get top trader contract long and short account ratio."""
        return self._native_public(
            "get_top_trader_long_short_account_ratio",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                period=period,
                begin=begin,
                end=end,
            ),
        )

    def get_top_trader_long_short_position_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get top trader contract long and short position ratio."""
        return self._native_public(
            "get_top_trader_long_short_position_ratio",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                period=period,
                begin=begin,
                end=end,
            ),
        )

    def get_contracts_open_interest_and_volume(
        self,
        ccy: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get contracts open interest and volume by currency."""
        return self._native_public(
            "get_contracts_open_interest_and_volume",
            self._params(ccy=ccy, period=period, begin=begin, end=end),
        )

    def get_contract_open_interest_history(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get contract open interest history."""
        return self._native_public(
            "get_contract_open_interest_history",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                period=period,
                begin=begin,
                end=end,
            ),
        )
