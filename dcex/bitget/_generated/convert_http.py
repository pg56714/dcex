"""Generated bitget convert HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedConvertHTTP(MarketHTTP):
    """Convert API methods."""

    def classic_spot_bgb_convert_bgb_convert(self, *, coin_list: list[Any]) -> dict[str, Any]:
        """
        Convert BGB.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-spot-bgb-convert/classic-spot-bgb-convert#convert-bgb
        """
        return self._native_private(
            "classic_spot_bgb_convert_bgb_convert", self._native_params(**{"coinList": coin_list})
        )

    def classic_spot_bgb_convert_get_bgb_convert_coins(self) -> dict[str, Any]:
        """
        Get BGB Convert Coins.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-spot-bgb-convert/classic-spot-bgb-convert#get-bgb-convert-coins
        """
        return self._native_private(
            "classic_spot_bgb_convert_get_bgb_convert_coins", self._native_params(**{})
        )

    def classic_spot_bgb_convert_get_bgb_convert_record(
        self,
        *,
        order_id: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        Get BGB Convert History.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-spot-bgb-convert/classic-spot-bgb-convert#get-bgb-convert-history
        """
        return self._native_private(
            "classic_spot_bgb_convert_get_bgb_convert_record",
            self._native_params(
                **{
                    "orderId": order_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "idLessThan": id_less_than,
                }
            ),
        )
