"""MEXC async public market-data HTTP client."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import ContractMarket, SpotMarket


class MarketHTTP(HTTPManager):
    """Async HTTP client for MEXC public market-data APIs."""

    def _spot_symbol(self, product_symbol: str) -> str:
        return self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)

    def _contract_symbol(self, product_symbol: str) -> str:
        return self.ptm.get_exchange_symbol(Common.MEXC, product_symbol)

    async def ping(self) -> dict[str, Any] | list[Any]:
        """Test MEXC Spot API connectivity."""
        return await self._request("GET", SpotMarket.PING, signed=False)

    async def get_spot_time(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot server time."""
        return await self._request("GET", SpotMarket.SERVER_TIME, signed=False)

    async def get_spot_default_symbols(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot API default symbols."""
        return await self._request("GET", SpotMarket.DEFAULT_SYMBOLS, signed=False)

    async def get_spot_exchange_info(
        self,
        product_symbol: str | None = None,
        status: str | int | None = None,
        tradeSideType: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot exchange information."""
        symbol = self._spot_symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            SpotMarket.EXCHANGE_INFO,
            {"symbol": symbol, "status": status, "tradeSideType": tradeSideType},
            signed=False,
        )

    async def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot orderbook depth."""
        return await self._request(
            "GET",
            SpotMarket.ORDERBOOK,
            {"symbol": self._spot_symbol(product_symbol), "limit": limit},
            signed=False,
        )

    async def get_spot_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot recent trades."""
        return await self._request(
            "GET",
            SpotMarket.RECENT_TRADES,
            {"symbol": self._spot_symbol(product_symbol), "limit": limit},
            signed=False,
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
        return await self._request(
            "GET",
            SpotMarket.AGG_TRADES,
            {
                "symbol": self._spot_symbol(product_symbol),
                "fromId": fromId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            signed=False,
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
        return await self._request(
            "GET",
            SpotMarket.KLINES,
            {
                "symbol": self._spot_symbol(product_symbol),
                "interval": interval,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
            signed=False,
        )

    async def get_spot_avg_price(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot current average price."""
        return await self._request(
            "GET",
            SpotMarket.AVG_PRICE,
            {"symbol": self._spot_symbol(product_symbol)},
            signed=False,
        )

    async def get_spot_ticker_24hr(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot 24h ticker."""
        symbol = self._spot_symbol(product_symbol) if product_symbol is not None else None
        return await self._request("GET", SpotMarket.TICKER_24HR, {"symbol": symbol}, signed=False)

    async def get_spot_ticker_price(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot price ticker."""
        symbol = self._spot_symbol(product_symbol) if product_symbol is not None else None
        return await self._request("GET", SpotMarket.TICKER_PRICE, {"symbol": symbol}, signed=False)

    async def get_spot_book_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot best bid/ask ticker."""
        symbol = self._spot_symbol(product_symbol) if product_symbol is not None else None
        return await self._request("GET", SpotMarket.BOOK_TICKER, {"symbol": symbol}, signed=False)

    async def get_contract_time(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract server time."""
        return await self._request("GET", ContractMarket.PING, signed=False, api="contract")

    async def get_contract_details(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract metadata."""
        symbol = self._contract_symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            ContractMarket.DETAIL,
            {"symbol": symbol},
            signed=False,
            api="contract",
        )

    async def get_contract_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract ticker."""
        symbol = self._contract_symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            ContractMarket.TICKER,
            {"symbol": symbol},
            signed=False,
            api="contract",
        )

    async def get_contract_depth(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract orderbook depth."""
        symbol = self._contract_symbol(product_symbol)
        path = str(ContractMarket.DEPTH).format(symbol=symbol)
        return await self._request("GET", path, {"limit": limit}, signed=False, api="contract")

    async def get_contract_depth_commits(
        self,
        product_symbol: str,
        limit: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve recent MEXC Contract depth snapshots."""
        symbol = self._contract_symbol(product_symbol)
        path = str(ContractMarket.DEPTH_COMMITS).format(symbol=symbol, limit=limit)
        return await self._request("GET", path, signed=False, api="contract")

    async def get_contract_index_price(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract index price."""
        symbol = self._contract_symbol(product_symbol)
        path = str(ContractMarket.INDEX_PRICE).format(symbol=symbol)
        return await self._request("GET", path, signed=False, api="contract")

    async def get_contract_fair_price(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract fair price."""
        symbol = self._contract_symbol(product_symbol)
        path = str(ContractMarket.FAIR_PRICE).format(symbol=symbol)
        return await self._request("GET", path, signed=False, api="contract")

    async def get_contract_funding_rate(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract current funding rate."""
        symbol = self._contract_symbol(product_symbol)
        path = str(ContractMarket.FUNDING_RATE).format(symbol=symbol)
        return await self._request("GET", path, signed=False, api="contract")

    async def get_contract_kline(
        self,
        product_symbol: str,
        interval: str,
        start: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract candles."""
        symbol = self._contract_symbol(product_symbol)
        path = str(ContractMarket.KLINE).format(symbol=symbol)
        return await self._request(
            "GET",
            path,
            {"interval": interval, "start": start, "end": end},
            signed=False,
            api="contract",
        )

    async def get_contract_index_price_kline(
        self,
        product_symbol: str,
        interval: str,
        start: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract index-price candles."""
        symbol = self._contract_symbol(product_symbol)
        path = str(ContractMarket.INDEX_PRICE_KLINE).format(symbol=symbol)
        return await self._request(
            "GET",
            path,
            {"interval": interval, "start": start, "end": end},
            signed=False,
            api="contract",
        )

    async def get_contract_fair_price_kline(
        self,
        product_symbol: str,
        interval: str,
        start: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract fair-price candles."""
        symbol = self._contract_symbol(product_symbol)
        path = str(ContractMarket.FAIR_PRICE_KLINE).format(symbol=symbol)
        return await self._request(
            "GET",
            path,
            {"interval": interval, "start": start, "end": end},
            signed=False,
            api="contract",
        )

    async def get_contract_deals(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract recent deals."""
        symbol = self._contract_symbol(product_symbol)
        path = str(ContractMarket.DEALS).format(symbol=symbol)
        return await self._request("GET", path, {"limit": limit}, signed=False, api="contract")

    async def get_contract_risk_reverse(self) -> dict[str, Any] | list[Any]:
        """Retrieve all MEXC Contract risk fund balances."""
        return await self._request("GET", ContractMarket.RISK_REVERSE, signed=False, api="contract")

    async def get_contract_risk_reverse_history(
        self,
        product_symbol: str,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract risk fund balance history."""
        return await self._request(
            "GET",
            ContractMarket.RISK_REVERSE_HISTORY,
            {
                "symbol": self._contract_symbol(product_symbol),
                "page_num": page_num,
                "page_size": page_size,
            },
            signed=False,
            api="contract",
        )

    async def get_contract_funding_rate_history(
        self,
        product_symbol: str,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract historical funding rates."""
        return await self._request(
            "GET",
            ContractMarket.FUNDING_RATE_HISTORY,
            {
                "symbol": self._contract_symbol(product_symbol),
                "page_num": page_num,
                "page_size": page_size,
            },
            signed=False,
            api="contract",
        )
