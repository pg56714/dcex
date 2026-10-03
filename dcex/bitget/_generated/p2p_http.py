"""Generated bitget p2p HTTP methods."""

from typing import Any

from dcex._operation_guards import require_confirmation

from .._market_http import MarketHTTP


class GeneratedP2pHTTP(MarketHTTP):
    """P2p API methods."""

    def classic_tax_get_p2_p_account_record(
        self,
        *,
        start_time: str,
        end_time: str,
        coin: str | None = None,
        limit: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        P2P Transaction Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-tax-tax-records/classic-tax#p2p-transaction-records
        """
        return self._native_private(
            "classic_tax_get_p2_p_account_record",
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

    def p2p_ad_management_get_ad_list(
        self,
        *,
        token: str,
        fiat: str,
        side: str,
        page_num: str,
        limit: str,
        amount: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Ad List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#get-ad-list
        """
        return self._native_private(
            "p2p_ad_management_get_ad_list",
            self._native_params(
                **{
                    "token": token,
                    "fiat": fiat,
                    "side": side,
                    "pageNum": page_num,
                    "limit": limit,
                    "amount": amount,
                }
            ),
        )

    def p2p_ad_management_get_exchange_rate(self, *, token: str, fiat: str) -> dict[str, Any]:
        """
        Get Exchange Rate.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#get-exchange-rate
        """
        return self._native_private(
            "p2p_ad_management_get_exchange_rate",
            self._native_params(**{"token": token, "fiat": fiat}),
        )

    def p2p_ad_management_fee_simulate(
        self, *, token: str, fiat: str, side: str, market_type: str, amount: str
    ) -> dict[str, Any]:
        """
        Fee Simulate.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#fee-simulate
        """
        return self._native_private(
            "p2p_ad_management_fee_simulate",
            self._native_params(
                **{
                    "token": token,
                    "fiat": fiat,
                    "side": side,
                    "marketType": market_type,
                    "amount": amount,
                }
            ),
        )

    def p2p_ad_management_get_ad_limit(self, *, token: str, fiat: str, side: str) -> dict[str, Any]:
        """
        Get Ad Limit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#get-ad-limit
        """
        return self._native_private(
            "p2p_ad_management_get_ad_limit",
            self._native_params(**{"token": token, "fiat": fiat, "side": side}),
        )

    def p2p_ad_management_create_ad(
        self,
        *,
        token: str,
        fiat: str,
        side: str,
        price_type: str,
        min_amount: str,
        max_amount: str,
        quantity: str,
        pay_method_ids: list[Any],
        pay_time_limit: str,
        price: str | None = None,
        premium: str | None = None,
        remark: str | None = None,
        trade_terms: str | None = None,
    ) -> dict[str, Any]:
        """
        Create Ad.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#create-ad
        """
        return self._native_private(
            "p2p_ad_management_create_ad",
            self._native_params(
                **{
                    "token": token,
                    "fiat": fiat,
                    "side": side,
                    "priceType": price_type,
                    "minAmount": min_amount,
                    "maxAmount": max_amount,
                    "quantity": quantity,
                    "payMethodIds": pay_method_ids,
                    "payTimeLimit": pay_time_limit,
                    "price": price,
                    "premium": premium,
                    "remark": remark,
                    "tradeTerms": trade_terms,
                }
            ),
        )

    def p2p_ad_management_update_ad(
        self,
        *,
        adv_id: str,
        pay_time_limit: str,
        price_type: str | None = None,
        price: str | None = None,
        premium: str | None = None,
        min_amount: str | None = None,
        max_amount: str | None = None,
        quantity: str | None = None,
        pay_method_ids: list[Any] | None = None,
        remark: str | None = None,
        trade_terms: str | None = None,
    ) -> dict[str, Any]:
        """
        Update Ad.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#update-ad
        """
        return self._native_private(
            "p2p_ad_management_update_ad",
            self._native_params(
                **{
                    "advId": adv_id,
                    "payTimeLimit": pay_time_limit,
                    "priceType": price_type,
                    "price": price,
                    "premium": premium,
                    "minAmount": min_amount,
                    "maxAmount": max_amount,
                    "quantity": quantity,
                    "payMethodIds": pay_method_ids,
                    "remark": remark,
                    "tradeTerms": trade_terms,
                }
            ),
        )

    def p2p_ad_management_operate_ad(self, *, adv_id: str, operation: str) -> dict[str, Any]:
        """
        Operate Ad.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#operate-ad
        """
        return self._native_private(
            "p2p_ad_management_operate_ad",
            self._native_params(**{"advId": adv_id, "operation": operation}),
        )

    def p2p_ad_management_get_ad_info(self, *, adv_id: str) -> dict[str, Any]:
        """
        Get Ad Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#get-ad-info
        """
        return self._native_private(
            "p2p_ad_management_get_ad_info", self._native_params(**{"advId": adv_id})
        )

    def p2p_ad_management_get_my_ads(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
        adv_id: str | None = None,
        token: str | None = None,
        fiat: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """
        Get My Ads.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#get-my-ads
        """
        return self._native_private(
            "p2p_ad_management_get_my_ads",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                    "advId": adv_id,
                    "token": token,
                    "fiat": fiat,
                    "status": status,
                }
            ),
        )

    def get_p2p_balance(self, *, token: str) -> dict[str, Any]:
        """
        Get Balance.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/common#get-balance
        """
        return self._native_private("get_p2p_balance", self._native_params(**{"token": token}))

    def p2p_order_management_get_pending_orders(
        self,
        *,
        order_id: str | None = None,
        side: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        cursor: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Pending Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/order-management#get-pending-orders
        """
        return self._native_private(
            "p2p_order_management_get_pending_orders",
            self._native_params(
                **{
                    "orderId": order_id,
                    "side": side,
                    "startTime": start_time,
                    "endTime": end_time,
                    "cursor": cursor,
                    "limit": limit,
                }
            ),
        )

    def p2p_order_management_get_all_orders(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
        order_id: str | None = None,
        side: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """
        Get All Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/order-management#get-all-orders
        """
        return self._native_private(
            "p2p_order_management_get_all_orders",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                    "orderId": order_id,
                    "side": side,
                    "status": status,
                }
            ),
        )

    def p2p_order_management_get_order_info(self, *, order_id: str) -> dict[str, Any]:
        """
        Get Order Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/order-management#get-order-info
        """
        return self._native_private(
            "p2p_order_management_get_order_info", self._native_params(**{"orderId": order_id})
        )

    def p2p_order_management_confirm_payment(
        self, *, order_id: str, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Confirm Payment.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/order-management#confirm-payment
        """
        require_confirmation(confirm)
        return self._native_private(
            "p2p_order_management_confirm_payment",
            self._native_params(**{"orderId": order_id, "confirm": confirm}),
        )

    def p2p_order_management_release_asset(
        self, *, order_id: str, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Release Asset.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/order-management#release-asset
        """
        require_confirmation(confirm)
        return self._native_private(
            "p2p_order_management_release_asset",
            self._native_params(**{"orderId": order_id, "confirm": confirm}),
        )

    def p2p_user_info_get_user_info(self) -> dict[str, Any]:
        """
        Get User Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/user-info#get-user-info
        """
        return self._native_private("p2p_user_info_get_user_info", self._native_params(**{}))

    def p2p_user_info_get_currencies(self) -> dict[str, Any]:
        """
        Get Currencies.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/user-info#get-currencies
        """
        return self._native_private("p2p_user_info_get_currencies", self._native_params(**{}))

    def p2p_user_info_get_pay_methods(self) -> dict[str, Any]:
        """
        Get Pay Methods.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/user-info#get-pay-methods
        """
        return self._native_private("p2p_user_info_get_pay_methods", self._native_params(**{}))
