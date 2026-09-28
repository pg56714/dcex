"""Generated hyperliquid market HTTP methods."""

from typing import Any

from .._trade_http import TradeHTTP


class GeneratedMarketHTTP(TradeHTTP):
    """Market API methods."""

    async def get_outcome_templates(self) -> Any:  # noqa: ANN401
        """
        Query outcomeTemplates.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions#action-format
        """
        return await self._native_public("get_outcome_templates", self._native_params())
