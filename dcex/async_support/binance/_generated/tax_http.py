"""Generated binance tax HTTP methods."""

from json import dumps
from typing import Any

from dcex._schema_codec import normalize_params

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedTaxHTTP(MarketHTTP, TradeHTTP):
    """Tax API methods."""

    async def get_spot_rebate_history_records(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Spot Rebate History Records (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-rebate/api/rest-api/~#get-spot-rebate-history-records
        """
        return await self._native_private(
            "get_spot_rebate_history_records",
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
                        "page": page,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )
