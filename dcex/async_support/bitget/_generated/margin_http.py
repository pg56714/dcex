"""Generated bitget margin HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedMarginHTTP(MarketHTTP):
    """Margin API methods."""

    async def classic_common_apidata_margin_ls_ratio(
        self, *, symbol: str, period: str | None = None, coin: str | None = None
    ) -> dict[str, Any]:
        """
        Get Leveraged long-short ratio Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-leveraged-long-short-ratio-data
        """
        return await self._native_public(
            "classic_common_apidata_margin_ls_ratio",
            self._native_params(**{"symbol": symbol, "period": period, "coin": coin}),
        )
