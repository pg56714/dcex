"""Generated binance pay HTTP methods."""

from json import dumps
from typing import Any

from dcex._schema_codec import normalize_params

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedPayHTTP(MarketHTTP, TradeHTTP):
    """Pay API methods."""

    async def get_pay_trade_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Pay Trade History.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-pay/api/rest-api/~#get-pay-trade-history
        """
        return await self._native_private(
            "get_pay_trade_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "startTime": start_time,
                        "endTime": end_time,
                        "limit": limit,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )
