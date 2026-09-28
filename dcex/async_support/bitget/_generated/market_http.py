"""Generated bitget market HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedMarketHTTP(MarketHTTP):
    """Market API methods."""

    async def classic_common_apidata_account_long_short(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get Futures Active Long Short Account Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-futures-active-long-short-account-data
        """
        return await self._native_public(
            "classic_common_apidata_account_long_short",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    async def classic_common_apidata_fund_net_flow(self, *, symbol: str) -> dict[str, Any]:
        """
        Get Spot 24H Net Capital Inflow Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-spot-24h-net-capital-inflow-info
        """
        return await self._native_public(
            "classic_common_apidata_fund_net_flow", self._native_params(**{"symbol": symbol})
        )

    async def classic_common_apidata_get_big_data_symbol(self) -> dict[str, Any]:
        """
        Get Trade data support symbols.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-trade-data-support-symbols
        """
        return await self._native_public(
            "classic_common_apidata_get_big_data_symbol", self._native_params(**{})
        )

    async def classic_common_apidata_get_spot_fund_flow(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get spot fund flow.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-spot-fund-flow
        """
        return await self._native_public(
            "classic_common_apidata_get_spot_fund_flow",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    async def classic_common_apidata_long_short(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get Futures Long and Short Ratio Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-futures-long-and-short-ratio-data
        """
        return await self._native_public(
            "classic_common_apidata_long_short",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    async def classic_common_apidata_position_long_short(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get Futures Active Long Short Position Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-futures-active-long-short-position-data
        """
        return await self._native_public(
            "classic_common_apidata_position_long_short",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    async def classic_common_apidata_taker_buy_sell(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get Futures Active Buy Sell Volume Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-futures-active-buy-sell-volume-data
        """
        return await self._native_public(
            "classic_common_apidata_taker_buy_sell",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    async def classic_common_apidata_whale_net_flow(self, *, symbol: str) -> dict[str, Any]:
        """
        Get Spot Whale Net Flow Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-spot-whale-net-flow-data
        """
        return await self._native_public(
            "classic_common_apidata_whale_net_flow", self._native_params(**{"symbol": symbol})
        )
