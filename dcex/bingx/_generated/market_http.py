"""Generated bingx market HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedMarketHTTP(MarketHTTP):
    """Market API methods."""

    def post_api_lindorm_v1_ai_kline_query(
        self,
        *,
        indicator_type: str,
        access_token: str,
        proxy_user: str,
        symbol: str | None = None,
        interval: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: str | None = None,
        size: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Internal Lindorm Query.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/bingx-trading-plan/api-reference.md#L3
        """
        return self._native_private(
            "post_api_lindorm_v1_ai_kline_query",
            self._native_params(
                **{
                    "indicatorType": indicator_type,
                    "access_token": access_token,
                    "proxy_user": proxy_user,
                    "symbol": symbol,
                    "interval": interval,
                    "startTime": start_time,
                    "endTime": end_time,
                    "offset": offset,
                    "size": size,
                }
            ),
        )
