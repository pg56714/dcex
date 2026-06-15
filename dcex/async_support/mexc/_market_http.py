"""MEXC async public market-data HTTP client backed by Rust."""

from typing import Any

from ..._native_http import NativeResponse
from ...utils.common import Common
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Async HTTP client for MEXC public market-data APIs."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed MEXC public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("MEXC native client is required for public market methods.")
        status, headers, body = await self._native_client.public_request_async(method_name, params)
        response = NativeResponse(status, dict(headers), bytes(body))
        self._store_response_headers(response)
        return response.json()

    def _spot_symbol(self, product_symbol: str) -> str:
        """Map spot product symbol through PTM when available."""
        if hasattr(self, "ptm"):
            return self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)
        parts = product_symbol.split("-")
        if len(parts) >= 3:
            return f"{parts[0]}{parts[1]}"
        return product_symbol

    def _contract_symbol(self, product_symbol: str) -> str:
        """Map contract product symbol through PTM when available."""
        if hasattr(self, "ptm"):
            return self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)
        parts = product_symbol.split("-")
        if len(parts) >= 3:
            return f"{parts[0]}_{parts[1]}"
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

    async def ping(self) -> dict[str, Any] | list[Any]:
        """Test MEXC Spot API connectivity."""
        return await self._native_public("ping", [])

    async def get_spot_time(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot server time."""
        return await self._native_public("get_spot_time", [])

    async def get_spot_default_symbols(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot API default symbols."""
        return await self._native_public("get_spot_default_symbols", [])

    async def get_spot_exchange_info(
        self,
        product_symbol: str | None = None,
        status: str | int | None = None,
        tradeSideType: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot exchange information."""
        symbol = self._spot_symbol(product_symbol) if product_symbol is not None else None
        return await self._native_public(
            "get_spot_exchange_info",
            self._params(symbol=symbol, status=status, tradeSideType=tradeSideType),
        )

    async def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot orderbook depth."""
        return await self._native_public(
            "get_spot_orderbook",
            self._params(symbol=self._spot_symbol(product_symbol), limit=limit),
        )

    async def get_spot_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot recent trades."""
        return await self._native_public(
            "get_spot_recent_trades",
            self._params(symbol=self._spot_symbol(product_symbol), limit=limit),
        )

    async def get_spot_agg_trades(
        self,
        product_symbol: str,
        fromId: str | int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot aggregate trades."""
        return await self._native_public(
            "get_spot_agg_trades",
            self._params(
                symbol=self._spot_symbol(product_symbol),
                fromId=fromId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_spot_klines(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot candles."""
        return await self._native_public(
            "get_spot_klines",
            self._params(
                symbol=self._spot_symbol(product_symbol),
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_spot_avg_price(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot current average price."""
        return await self._native_public(
            "get_spot_avg_price",
            self._params(symbol=self._spot_symbol(product_symbol)),
        )

    async def get_spot_ticker_24hr(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot 24h ticker."""
        symbol = self._spot_symbol(product_symbol) if product_symbol is not None else None
        return await self._native_public("get_spot_ticker_24hr", self._params(symbol=symbol))

    async def get_spot_ticker_price(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot price ticker."""
        symbol = self._spot_symbol(product_symbol) if product_symbol is not None else None
        return await self._native_public("get_spot_ticker_price", self._params(symbol=symbol))

    async def get_spot_book_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot best bid/ask ticker."""
        symbol = self._spot_symbol(product_symbol) if product_symbol is not None else None
        return await self._native_public("get_spot_book_ticker", self._params(symbol=symbol))

    async def get_contract_time(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract server time."""
        return await self._native_public("get_contract_time", [])

    async def get_contract_details(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract metadata."""
        symbol = self._contract_symbol(product_symbol) if product_symbol is not None else None
        return await self._native_public("get_contract_details", self._params(symbol=symbol))

    async def get_contract_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract ticker."""
        symbol = self._contract_symbol(product_symbol) if product_symbol is not None else None
        return await self._native_public("get_contract_ticker", self._params(symbol=symbol))

    async def get_contract_depth(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract orderbook depth."""
        return await self._native_public(
            "get_contract_depth",
            self._params(symbol=self._contract_symbol(product_symbol), limit=limit),
        )

    async def get_contract_depth_commits(
        self,
        product_symbol: str,
        limit: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve recent MEXC Contract depth snapshots."""
        return await self._native_public(
            "get_contract_depth_commits",
            self._params(symbol=self._contract_symbol(product_symbol), limit=limit),
        )

    async def get_contract_index_price(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract index price."""
        return await self._native_public(
            "get_contract_index_price",
            self._params(symbol=self._contract_symbol(product_symbol)),
        )

    async def get_contract_fair_price(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract fair price."""
        return await self._native_public(
            "get_contract_fair_price",
            self._params(symbol=self._contract_symbol(product_symbol)),
        )

    async def get_contract_funding_rate(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract current funding rate."""
        return await self._native_public(
            "get_contract_funding_rate",
            self._params(symbol=self._contract_symbol(product_symbol)),
        )

    async def get_contract_kline(
        self,
        product_symbol: str,
        interval: str,
        start: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract candles."""
        return await self._native_public(
            "get_contract_kline",
            self._params(
                symbol=self._contract_symbol(product_symbol),
                interval=interval,
                start=start,
                end=end,
            ),
        )

    async def get_contract_index_price_kline(
        self,
        product_symbol: str,
        interval: str,
        start: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract index-price candles."""
        return await self._native_public(
            "get_contract_index_price_kline",
            self._params(
                symbol=self._contract_symbol(product_symbol),
                interval=interval,
                start=start,
                end=end,
            ),
        )

    async def get_contract_fair_price_kline(
        self,
        product_symbol: str,
        interval: str,
        start: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract fair-price candles."""
        return await self._native_public(
            "get_contract_fair_price_kline",
            self._params(
                symbol=self._contract_symbol(product_symbol),
                interval=interval,
                start=start,
                end=end,
            ),
        )

    async def get_contract_deals(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract recent deals."""
        return await self._native_public(
            "get_contract_deals",
            self._params(symbol=self._contract_symbol(product_symbol), limit=limit),
        )

    async def get_contract_risk_reverse(self) -> dict[str, Any] | list[Any]:
        """Retrieve all MEXC Contract risk fund balances."""
        return await self._native_public("get_contract_risk_reverse", [])

    async def get_contract_risk_reverse_history(
        self,
        product_symbol: str,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract risk fund balance history."""
        return await self._native_public(
            "get_contract_risk_reverse_history",
            self._params(
                symbol=self._contract_symbol(product_symbol),
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def get_contract_funding_rate_history(
        self,
        product_symbol: str,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract historical funding rates."""
        return await self._native_public(
            "get_contract_funding_rate_history",
            self._params(
                symbol=self._contract_symbol(product_symbol),
                page_num=page_num,
                page_size=page_size,
            ),
        )
