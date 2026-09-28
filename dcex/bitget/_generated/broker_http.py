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

    def classic_broker_apikey_create_subaccount_api_key(
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
        Create Subaccount ApiKey.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-apikey/classic-broker-apikey#create-subaccount-apikey
        """
        return self._native_private(
            "classic_broker_apikey_create_subaccount_api_key",
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

    def classic_broker_apikey_delete_subaccount_api_key(
        self, *, sub_uid: str, api_key: str, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Delete Subaccount ApiKey.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-apikey/classic-broker-apikey#delete-subaccount-apikey
        """
        require_confirmation(confirm)
        return self._native_private(
            "classic_broker_apikey_delete_subaccount_api_key",
            self._native_params(**{"subUid": sub_uid, "apiKey": api_key, "confirm": confirm}),
        )

    def classic_broker_apikey_subaccount_apikey_list(self, *, sub_uid: str) -> dict[str, Any]:
        """
        Get Subaccount Apikey.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-apikey/classic-broker-apikey#get-subaccount-apikey
        """
        return self._native_private(
            "classic_broker_apikey_subaccount_apikey_list",
            self._native_params(**{"subUid": sub_uid}),
        )

    def classic_broker_apikey_modify_subaccount_api_key(
        self,
        *,
        sub_uid: str,
        api_key: str,
        passphrase: str,
        perm_type: str,
        perm_list: list[Any],
        label: str | None = None,
        ip_list: list[Any] | None = None,
    ) -> dict[str, Any]:
        """
        Modify Subaccount ApiKey.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-apikey/classic-broker-apikey#modify-subaccount-apikey
        """
        return self._native_private(
            "classic_broker_apikey_modify_subaccount_api_key",
            self._native_params(
                **{
                    "subUid": sub_uid,
                    "apiKey": api_key,
                    "passphrase": passphrase,
                    "permType": perm_type,
                    "permList": perm_list,
                    "label": label,
                    "ipList": ip_list,
                }
            ),
        )

    def classic_broker_commission_get_total_commission(
        self, *, start_time: str | None = None, end_time: str | None = None
    ) -> dict[str, Any]:
        """
        Get Total Commission.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-commission/classic-broker-commission#get-total-commission
        """
        return self._native_private(
            "classic_broker_commission_get_total_commission",
            self._native_params(**{"startTime": start_time, "endTime": end_time}),
        )

    def classic_broker_commission_get_order_commission(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        uid: str | None = None,
        orderid: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Order Commission.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-commission/classic-broker-commission#get-order-commission
        """
        return self._native_private(
            "classic_broker_commission_get_order_commission",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "uid": uid,
                    "orderid": orderid,
                    "idLessThan": id_less_than,
                }
            ),
        )

    def classic_broker_commission_get_rebate_info(self, *, uid: str) -> dict[str, Any]:
        """
        Get Rebate Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-commission/classic-broker-commission#get-rebate-info
        """
        return self._native_private(
            "classic_broker_commission_get_rebate_info", self._native_params(**{"uid": uid})
        )

    def classic_broker_commission_get_sub_affiliate_info(
        self,
        *,
        uid: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        id_less_than: str | None = None,
        limit: str | None = None,
        include_down_line: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Sub-affiliate Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-commission/classic-broker-commission#get-sub-affiliate-info
        """
        return self._native_private(
            "classic_broker_commission_get_sub_affiliate_info",
            self._native_params(
                **{
                    "uid": uid,
                    "startTime": start_time,
                    "endTime": end_time,
                    "idLessThan": id_less_than,
                    "limit": limit,
                    "includeDownLine": include_down_line,
                }
            ),
        )

    def classic_broker_subaccount_get_broker_account_info(self) -> dict[str, Any]:
        """
        Get Broker Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-broker-info
        """
        return self._native_private(
            "classic_broker_subaccount_get_broker_account_info", self._native_params(**{})
        )

    def classic_broker_subaccount_modify_subaccount_email(
        self, *, sub_uid: str, subaccount_email: str
    ) -> dict[str, Any]:
        """
        Modify Subaccount Email.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#modify-subaccount-email
        """
        return self._native_private(
            "classic_broker_subaccount_modify_subaccount_email",
            self._native_params(**{"subUid": sub_uid, "subaccountEmail": subaccount_email}),
        )

    def classic_broker_subaccount_create_subaccount(
        self, *, subaccount_name: str, label: str | None = None
    ) -> dict[str, Any]:
        """
        Create Subaccount.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#create-subaccount
        """
        return self._native_private(
            "classic_broker_subaccount_create_subaccount",
            self._native_params(**{"subaccountName": subaccount_name, "label": label}),
        )

    def classic_broker_subaccount_get_subaccount_list(
        self,
        *,
        limit: str | None = None,
        id_less_than: str | None = None,
        status: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Subaccount List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-subaccount-list
        """
        return self._native_private(
            "classic_broker_subaccount_get_subaccount_list",
            self._native_params(
                **{
                    "limit": limit,
                    "idLessThan": id_less_than,
                    "status": status,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    def classic_broker_subaccount_modify_suaccount(
        self, *, sub_uid: str, perm_list: list[Any], status: str, language: str | None = None
    ) -> dict[str, Any]:
        """
        Modify Subaccount.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#modify-subaccount
        """
        return self._native_private(
            "classic_broker_subaccount_modify_suaccount",
            self._native_params(
                **{"subUid": sub_uid, "permList": perm_list, "status": status, "language": language}
            ),
        )

    def classic_broker_subaccount_get_subaccount_email(self, *, sub_uid: str) -> dict[str, Any]:
        """
        Get Subaccount Email.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-subaccount-email
        """
        return self._native_private(
            "classic_broker_subaccount_get_subaccount_email",
            self._native_params(**{"subUid": sub_uid}),
        )

    def classic_broker_subaccount_get_subaccount_spot_assets(
        self, *, sub_uid: str, coin: str | None = None, asset_type: str | None = None
    ) -> dict[str, Any]:
        """
        Get Subaccount Spot Assets.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-subaccount-spot-assets
        """
        return self._native_private(
            "classic_broker_subaccount_get_subaccount_spot_assets",
            self._native_params(**{"subUid": sub_uid, "coin": coin, "assetType": asset_type}),
        )

    def classic_broker_subaccount_get_subaccount_future_assets(
        self, *, sub_uid: str, product_type: str
    ) -> dict[str, Any]:
        """
        Get Subaccount Future Assets.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-subaccount-future-assets
        """
        return self._native_private(
            "classic_broker_subaccount_get_subaccount_future_assets",
            self._native_params(**{"subUid": sub_uid, "productType": product_type}),
        )

    def classic_broker_subaccount_create_subaccount_deposit_address(
        self, *, sub_uid: str, coin: str, chain: str | None = None
    ) -> dict[str, Any]:
        """
        Create Subaccount Deposit Address.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#create-subaccount-deposit-address
        """
        return self._native_private(
            "classic_broker_subaccount_create_subaccount_deposit_address",
            self._native_params(**{"subUid": sub_uid, "coin": coin, "chain": chain}),
        )

    def classic_broker_subaccount_subaccount_deposit_records(
        self,
        *,
        order_id: str | None = None,
        user_id: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        Sub Deposit Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#sub-deposit-records
        """
        return self._native_private(
            "classic_broker_subaccount_subaccount_deposit_records",
            self._native_params(
                **{
                    "orderId": order_id,
                    "userId": user_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "idLessThan": id_less_than,
                }
            ),
        )

    def classic_broker_subaccount_get_broker_subaccounts(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        page_size: str | None = None,
        page_no: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Broker Subaccounts.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-broker-subaccounts
        """
        return self._native_private(
            "classic_broker_subaccount_get_broker_subaccounts",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageSize": page_size,
                    "pageNo": page_no,
                }
            ),
        )

    def classic_broker_subaccount_get_broker_subaccounts_commissions(
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
        Get Broker Subaccounts Commissions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-broker-subaccounts-commissions
        """
        return self._native_private(
            "classic_broker_subaccount_get_broker_subaccounts_commissions",
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

    def classic_broker_subaccount_get_broker_trade_volume(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        page_size: str | None = None,
        page_no: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Broker Trade Volume.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-broker-trade-volume
        """
        return self._native_private(
            "classic_broker_subaccount_get_broker_trade_volume",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageSize": page_size,
                    "pageNo": page_no,
                }
            ),
        )
