"""Generated bingx earn HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedEarnHTTP(MarketHTTP):
    """Earn API methods."""

    def get_wealth_v1_product_dual_currency_order_records(
        self, *, page_id: int, page_size: int, order_no: str | None = None
    ) -> Any:  # noqa: ANN401
        """Dual-Currency Order Records.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Wealth/Dual-Currency/Dual-Currency%20Order%20Records
        """
        return self._native_private(
            "get_wealth_v1_product_dual_currency_order_records",
            self._native_params(**{"pageId": page_id, "pageSize": page_size, "orderNo": order_no}),
        )

    def get_wealth_v1_product_dual_currency_position(self, *, order_no: str | None = None) -> Any:  # noqa: ANN401
        """Dual-Currency Position Query.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Wealth/Dual-Currency/Dual-Currency%20Position%20Query
        """
        return self._native_private(
            "get_wealth_v1_product_dual_currency_position",
            self._native_params(**{"orderNo": order_no}),
        )

    def post_wealth_v1_product_dual_currency_invest_asset_list(
        self,
        *,
        page_index: int | None = None,
        page_size: int | None = None,
        begin_duration: int | None = None,
        end_duration: int | None = None,
        duration: int | None = None,
        investment_asset: str | None = None,
        exercise_asset: str | None = None,
        direction: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Dual-Currency Product List.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Wealth/Dual-Currency/Dual-Currency%20Product%20List
        """
        return self._native_private(
            "post_wealth_v1_product_dual_currency_invest_asset_list",
            self._native_params(
                **{
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "beginDuration": begin_duration,
                    "endDuration": end_duration,
                    "duration": duration,
                    "investmentAsset": investment_asset,
                    "exerciseAsset": exercise_asset,
                    "direction": direction,
                }
            ),
        )

    def post_wealth_v1_product_dual_currency_order(
        self,
        *,
        amount: str,
        sku: str,
        product_id: int,
        strike_price: str,
        quote_id: str,
        investment_asset: str | None = None,
        exercise_asset: str | None = None,
        select_accounts: list[Any] | None = None,
        settle_target_account: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Dual-Currency Place Order.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Wealth/Dual-Currency/Dual-Currency%20Place%20Order
        """
        return self._native_private(
            "post_wealth_v1_product_dual_currency_order",
            self._native_params(
                **{
                    "amount": amount,
                    "sku": sku,
                    "productId": product_id,
                    "strikePrice": strike_price,
                    "quoteId": quote_id,
                    "investmentAsset": investment_asset,
                    "exerciseAsset": exercise_asset,
                    "selectAccounts": select_accounts,
                    "settleTargetAccount": settle_target_account,
                }
            ),
        )

    def get_wealth_v1_product_dual_currency_pre_order(
        self, *, sku: str, strike_price: str, product_id: int
    ) -> Any:  # noqa: ANN401
        """Dual-Currency Pre-Order Quote.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Wealth/Dual-Currency/Dual-Currency%20Pre-Order%20Quote
        """
        return self._native_private(
            "get_wealth_v1_product_dual_currency_pre_order",
            self._native_params(
                **{"sku": sku, "strikePrice": strike_price, "productId": product_id}
            ),
        )
