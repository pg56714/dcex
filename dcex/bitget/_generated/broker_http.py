"""Generated bitget broker HTTP methods."""

from typing import Any

from dcex._operation_guards import require_confirmation

from .._market_http import MarketHTTP


class GeneratedBrokerHTTP(MarketHTTP):
    """Broker API methods."""

    def broker_create_subaccount(self, *, subaccount_name: str, label: str) -> dict[str, Any]:
        """
        Create Broker Sub-Account.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#create-broker-sub-account
        """
        return self._native_private(
            "broker_create_subaccount",
            self._native_params(**{"subaccountName": subaccount_name, "label": label}),
        )

    def broker_create_subaccount_apikey(
        self,
        *,
        sub_uid: str,
        passphrase: str,
        label: str,
        ip_list: list[Any],
        perm_type: str,
        perm_list: list[Any],
    ) -> dict[str, Any]:
        """
        Create Broker Sub-Account API Key.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#create-broker-sub-account-api-key
        """
        return self._native_private(
            "broker_create_subaccount_apikey",
            self._native_params(
                **{
                    "subUid": sub_uid,
                    "passphrase": passphrase,
                    "label": label,
                    "ipList": ip_list,
                    "permType": perm_type,
                    "permList": perm_list,
                }
            ),
        )

    def broker_delete_subaccount_apikey(
        self, *, sub_uid: str, api_key: str, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Delete Broker Sub-Account API Key.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#delete-broker-sub-account-api-key
        """
        require_confirmation(confirm)
        return self._native_private(
            "broker_delete_subaccount_apikey",
            self._native_params(**{"subUid": sub_uid, "apiKey": api_key, "confirm": confirm}),
        )

    def broker_get_broker_commission(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        page_size: str | None = None,
        page_no: str | None = None,
        biz_type: str | None = None,
        sub_biz_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Broker Commission.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#get-broker-commission
        """
        return self._native_private(
            "broker_get_broker_commission",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageSize": page_size,
                    "pageNo": page_no,
                    "bizType": biz_type,
                    "subBizType": sub_biz_type,
                }
            ),
        )

    def broker_get_subaccount_apikey(self, *, sub_uid: str) -> dict[str, Any]:
        """
        Get Broker Sub-Account API Key.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#get-broker-sub-account-api-key
        """
        return self._native_private(
            "broker_get_subaccount_apikey", self._native_params(**{"subUid": sub_uid})
        )

    def broker_get_subaccount_list(
        self, *, limit: str | None = None, cursor: str | None = None, status: str | None = None
    ) -> dict[str, Any]:
        """
        Get Broker Sub-Account List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#get-broker-sub-account-list
        """
        return self._native_private(
            "broker_get_subaccount_list",
            self._native_params(**{"limit": limit, "cursor": cursor, "status": status}),
        )

    def broker_modify_subaccount_apikey(
        self,
        *,
        sub_uid: str,
        passphrase: str,
        api_key: str,
        label: str | None = None,
        ip_list: list[Any] | None = None,
        perm_type: str | None = None,
        perm_list: list[Any] | None = None,
    ) -> dict[str, Any]:
        """
        Modify Broker Sub-Account API Key.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#modify-broker-sub-account-api-key
        """
        return self._native_private(
            "broker_modify_subaccount_apikey",
            self._native_params(
                **{
                    "subUid": sub_uid,
                    "passphrase": passphrase,
                    "apiKey": api_key,
                    "label": label,
                    "ipList": ip_list,
                    "permType": perm_type,
                    "permList": perm_list,
                }
            ),
        )

    def broker_modify_subaccount(
        self, *, sub_uid: str, status: str | None = None, perm_list: str | None = None
    ) -> dict[str, Any]:
        """
        Modify Broker Sub-Account.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#modify-broker-sub-account
        """
        return self._native_private(
            "broker_modify_subaccount",
            self._native_params(**{"subUid": sub_uid, "status": status, "permList": perm_list}),
        )

    def broker_subaccount_deposit_address(
        self, *, sub_uid: str, coin: str, chain: str | None = None
    ) -> dict[str, Any]:
        """
        Get Broker Sub-Account Deposit Address.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#get-broker-sub-account-deposit-address
        """
        return self._native_private(
            "broker_subaccount_deposit_address",
            self._native_params(**{"subUid": sub_uid, "coin": coin, "chain": chain}),
        )

    def classic_affiliate_customer_info_get_commission_detail(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Agent Commission Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-affiliate-customer-info/classic-affiliate-customerinfo#get-agent-commission-detail
        """
        return self._native_private(
            "classic_affiliate_customer_info_get_commission_detail",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "idLessThan": id_less_than,
                }
            ),
        )

    def classic_affiliate_customer_info_get_customer_assets(
        self,
        *,
        page_no: str | None = None,
        page_size: str | None = None,
        uid: str | None = None,
        show_sub: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Agent Customer Assets List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-affiliate-customer-info/classic-affiliate-customerinfo#get-agent-customer-assets-list
        """
        return self._native_private(
            "classic_affiliate_customer_info_get_customer_assets",
            self._native_params(
                **{"pageNo": page_no, "pageSize": page_size, "uid": uid, "showSub": show_sub}
            ),
        )

    def classic_affiliate_customer_info_get_customer_deposit(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
        uid: str | None = None,
        show_sub: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Agent Customer Deposit List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-affiliate-customer-info/classic-affiliate-customerinfo#get-agent-customer-deposit-list
        """
        return self._native_private(
            "classic_affiliate_customer_info_get_customer_deposit",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "uid": uid,
                    "showSub": show_sub,
                }
            ),
        )

    def classic_affiliate_customer_info_get_customer_kyc_result(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        id_less_than: str | None = None,
        limit: str | None = None,
        uid: str | None = None,
        show_sub: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Agent Customer Kyc Result.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-affiliate-customer-info/classic-affiliate-customerinfo#get-agent-customer-kyc-result
        """
        return self._native_private(
            "classic_affiliate_customer_info_get_customer_kyc_result",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "idLessThan": id_less_than,
                    "limit": limit,
                    "uid": uid,
                    "showSub": show_sub,
                }
            ),
        )

    def classic_affiliate_customer_info_get_customer_list(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
        uid: str | None = None,
        referral_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Agent Customer List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-affiliate-customer-info/classic-affiliate-customerinfo#get-agent-customer-list
        """
        return self._native_private(
            "classic_affiliate_customer_info_get_customer_list",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "uid": uid,
                    "referralCode": referral_code,
                }
            ),
        )

    def classic_affiliate_customer_info_get_customer_trade_volume(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
        uid: str | None = None,
        show_sub: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Agent Customer Trade Volume List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-affiliate-customer-info/classic-affiliate-customerinfo#get-agent-customer-trade-volume-list
        """
        return self._native_private(
            "classic_affiliate_customer_info_get_customer_trade_volume",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "uid": uid,
                    "showSub": show_sub,
                }
            ),
        )

    def classic_affiliate_customer_info_get_direct_commissions(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        id_less_than: str | None = None,
        limit: str | None = None,
        uid: str | None = None,
        coin: str | None = None,
        symbol: str | None = None,
        show_sub: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Agent Direct commissions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-affiliate-customer-info/classic-affiliate-customerinfo#get-agent-direct-commissions
        """
        return self._native_private(
            "classic_affiliate_customer_info_get_direct_commissions",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "idLessThan": id_less_than,
                    "limit": limit,
                    "uid": uid,
                    "coin": coin,
                    "symbol": symbol,
                    "showSub": show_sub,
                }
            ),
        )

    def classic_affiliate_customer_info_get_sub_customer_list(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        id_less_than: str | None = None,
        limit: str | None = None,
        uid: str | None = None,
        show_sub: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Agent SubCustomer List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-affiliate-customer-info/classic-affiliate-customerinfo#get-agent-subcustomer-list
        """
        return self._native_private(
            "classic_affiliate_customer_info_get_sub_customer_list",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "idLessThan": id_less_than,
                    "limit": limit,
                    "uid": uid,
                    "showSub": show_sub,
                }
            ),
        )
