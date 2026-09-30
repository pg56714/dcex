"""Generated binance c2c HTTP methods."""

from json import dumps
from typing import Any

from dcex._schema_codec import normalize_params

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedC2cHTTP(MarketHTTP, TradeHTTP):
    """C2c API methods."""

    async def get_c2c_trade_history(
        self,
        *,
        trade_type: str | None = None,
        start_timestamp: int | None = None,
        end_timestamp: int | None = None,
        page: int | None = None,
        rows: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get C2C Trade History (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-c2-c/api/rest-api/~#get-c2-ctrade-history
        """
        return await self._native_private(
            "get_c2c_trade_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "tradeType": trade_type,
                        "startTimestamp": start_timestamp,
                        "endTimestamp": end_timestamp,
                        "page": page,
                        "rows": rows,
                    }
                ).items()
                if value is not None
            ],
        )
