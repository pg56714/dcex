"""Generated bitget earn HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedEarnHTTP(MarketHTTP):
    """Earn API methods."""

    def classic_earn_sharkfin_get_product(
        self, *, coin: str, limit: str | None = None, id_less_than: str | None = None
    ) -> dict[str, Any]:
        """
        Get Sharkfin Products.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#get-sharkfin-products
        """
        return self._native_private(
            "classic_earn_sharkfin_get_product",
            self._native_params(**{"coin": coin, "limit": limit, "idLessThan": id_less_than}),
        )

    def classic_earn_sharkfin_get_account(self) -> dict[str, Any]:
        """
        SharkFin Account.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#sharkfin-account
        """
        return self._native_private("classic_earn_sharkfin_get_account", self._native_params(**{}))

    def classic_earn_sharkfin_get_assets(
        self,
        *,
        status: str,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        SharkFin Assets.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#sharkfin-assets
        """
        return self._native_private(
            "classic_earn_sharkfin_get_assets",
            self._native_params(
                **{
                    "status": status,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "idLessThan": id_less_than,
                }
            ),
        )

    def classic_earn_sharkfin_get_records(
        self,
        *,
        type_: str,
        coin: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        SharkFin Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#sharkfin-records
        """
        return self._native_private(
            "classic_earn_sharkfin_get_records",
            self._native_params(
                **{
                    "type": type_,
                    "coin": coin,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "idLessThan": id_less_than,
                }
            ),
        )

    def classic_earn_sharkfin_get_subscribe_info(self, *, product_id: str) -> dict[str, Any]:
        """
        SharkFin Subscription Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#sharkfin-subscription-detail
        """
        return self._native_private(
            "classic_earn_sharkfin_get_subscribe_info",
            self._native_params(**{"productId": product_id}),
        )

    def classic_earn_sharkfin_subscribe(self, *, product_id: str, amount: str) -> dict[str, Any]:
        """
        Subscribe SharkFin.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#subscribe-sharkfin
        """
        return self._native_private(
            "classic_earn_sharkfin_subscribe",
            self._native_params(**{"productId": product_id, "amount": amount}),
        )

    def classic_earn_sharkfin_get_subscribe_result(self, *, order_id: str) -> dict[str, Any]:
        """
        SharkFin Subscription Result.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#sharkfin-subscription-result
        """
        return self._native_private(
            "classic_earn_sharkfin_get_subscribe_result",
            self._native_params(**{"orderId": order_id}),
        )
