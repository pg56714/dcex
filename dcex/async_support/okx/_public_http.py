"""OKX public async HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ...utils.common import Common
from ._http_manager import HTTPManager


class PublicHTTP(HTTPManager):
    """Async HTTP client for OKX public data operations."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed OKX public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("OKX native client is required for public methods.")
        response, data = await request_native_json_async(
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

    async def get_public_instruments(
        self,
        instType: str,
        seriesId: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get public instruments information."""
        inst_id = self._exchange_symbol(product_symbol) if product_symbol is not None else None
        return await self._native_public(
            "get_public_instruments",
            self._params(
                instType=instType,
                seriesId=seriesId,
                instFamily=instFamily,
                instId=inst_id,
            ),
        )

    async def get_funding_rate(self, product_symbol: str) -> dict[str, Any]:
        """Get funding rate information."""
        return await self._native_public(
            "get_funding_rate",
            self._params(instId=self._exchange_symbol(product_symbol)),
        )

    async def get_funding_rate_history(
        self,
        product_symbol: str,
        before: str | None = None,
        after: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Get funding rate history."""
        return await self._native_public(
            "get_funding_rate_history",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                before=before,
                after=after,
                limit=limit,
            ),
        )

    async def get_open_interest(
        self,
        instType: str = "SWAP",
        instFamily: str | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get public open interest data."""
        inst_id = self._exchange_symbol(product_symbol) if product_symbol is not None else None
        return await self._native_public(
            "get_open_interest",
            self._params(instType=instType, instFamily=instFamily, instId=inst_id),
        )

    async def get_position_tiers(
        self,
        instType: str = "SWAP",
        tdMode: str = "isolated",
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ccy: str | None = None,
        tier: str | None = None,
    ) -> dict[str, Any]:
        """Get position tiers information."""
        inst_id = self._exchange_symbol(product_symbol) if product_symbol is not None else None
        if (
            inst_id is not None
            and instFamily is None
            and instType.upper() in {"SWAP", "FUTURES", "OPTION"}
        ):
            symbol_parts = inst_id.split("-")
            if len(symbol_parts) >= 2:
                instFamily = "-".join(symbol_parts[:2])
        return await self._native_public(
            "get_position_tiers",
            self._params(
                instType=instType,
                tdMode=tdMode,
                instFamily=instFamily,
                instId=inst_id,
                ccy=ccy,
                tier=tier,
            ),
        )

    async def get_trading_data_support_coin(self) -> dict[str, Any]:
        """Get currencies supported by OKX trading data endpoints."""
        return await self._native_public("get_trading_data_support_coin", [])

    async def get_taker_volume(
        self,
        ccy: str,
        instType: str = "SPOT",
        begin: int | None = None,
        end: int | None = None,
        period: str = "5m",
    ) -> dict[str, Any]:
        """Get taker volume by currency and instrument type."""
        return await self._native_public(
            "get_taker_volume",
            self._params(ccy=ccy, instType=instType, begin=begin, end=end, period=period),
        )

    async def get_contract_taker_volume(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
        unit: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Get contract taker volume history."""
        return await self._native_public(
            "get_contract_taker_volume",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                period=period,
                begin=begin,
                end=end,
                unit=unit,
                limit=limit,
            ),
        )

    async def get_long_short_ratio(
        self,
        ccy: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get long and short account ratio by currency."""
        return await self._native_public(
            "get_long_short_ratio",
            self._params(ccy=ccy, period=period, begin=begin, end=end),
        )

    async def get_contract_long_short_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Get contract long and short account ratio."""
        return await self._native_public(
            "get_contract_long_short_ratio",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                period=period,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    async def get_top_trader_long_short_account_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Get top trader contract long and short account ratio."""
        return await self._native_public(
            "get_top_trader_long_short_account_ratio",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                period=period,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    async def get_top_trader_long_short_position_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Get top trader contract long and short position ratio."""
        return await self._native_public(
            "get_top_trader_long_short_position_ratio",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                period=period,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    async def get_contracts_open_interest_and_volume(
        self,
        ccy: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get contracts open interest and volume by currency."""
        return await self._native_public(
            "get_contracts_open_interest_and_volume",
            self._params(ccy=ccy, period=period, begin=begin, end=end),
        )

    async def get_contract_open_interest_history(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Get contract open interest history."""
        return await self._native_public(
            "get_contract_open_interest_history",
            self._params(
                instId=self._exchange_symbol(product_symbol),
                period=period,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )
