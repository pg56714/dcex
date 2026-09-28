"""Generated bitget tax HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedTaxHTTP(MarketHTTP):
    """Tax API methods."""

    def classic_tax_get_spot_account_record(
        self,
        *,
        start_time: str,
        end_time: str,
        coin: str | None = None,
        limit: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        Spot Transaction Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-tax-tax-records/classic-tax#spot-transaction-records
        """
        return self._native_private(
            "classic_tax_get_spot_account_record",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "coin": coin,
                    "limit": limit,
                    "idLessThan": id_less_than,
                }
            ),
        )

    def classic_tax_get_future_account_record(
        self,
        *,
        start_time: str,
        end_time: str,
        product_type: str | None = None,
        margin_coin: str | None = None,
        limit: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        Futures Transaction Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-tax-tax-records/classic-tax#futures-transaction-records
        """
        return self._native_private(
            "classic_tax_get_future_account_record",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "productType": product_type,
                    "marginCoin": margin_coin,
                    "limit": limit,
                    "idLessThan": id_less_than,
                }
            ),
        )

    def classic_tax_get_margin_account_record(
        self,
        *,
        start_time: str,
        end_time: str,
        margin_type: str | None = None,
        coin: str | None = None,
        limit: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        Margin Transaction History.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-tax-tax-records/classic-tax#margin-transaction-history
        """
        return self._native_private(
            "classic_tax_get_margin_account_record",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "marginType": margin_type,
                    "coin": coin,
                    "limit": limit,
                    "idLessThan": id_less_than,
                }
            ),
        )

    def tax_get_tax_records(
        self,
        *,
        biz_type: str,
        start_time: str,
        end_time: str,
        margin_type: str | None = None,
        coin: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Unified Account Tax Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/tax/tax-records#get-tax-records
        """
        return self._native_private(
            "tax_get_tax_records",
            self._native_params(
                **{
                    "bizType": biz_type,
                    "startTime": start_time,
                    "endTime": end_time,
                    "marginType": margin_type,
                    "coin": coin,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )
