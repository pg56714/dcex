"""Typed wrappers generated from the official Bitget operation schemas."""

from typing import Any

from dcex._operation_guards import require_confirmation

from ._market_http import MarketHTTP


class InventoryHTTP(MarketHTTP):
    """Additional broker, copy-trading, P2P, CFD and Stock+ endpoints."""

    async def broker_create_subaccount(self, *, subaccount_name: str, label: str) -> dict[str, Any]:
        """
        Create Broker Sub-Account.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#create-broker-sub-account
        """
        return await self._native_private(
            "broker_create_subaccount",
            self._native_params(**{"subaccountName": subaccount_name, "label": label}),
        )

    async def broker_create_subaccount_apikey(
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
        return await self._native_private(
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

    async def broker_delete_subaccount_apikey(
        self, *, sub_uid: str, api_key: str, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Delete Broker Sub-Account API Key.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#delete-broker-sub-account-api-key
        """
        require_confirmation(confirm)
        return await self._native_private(
            "broker_delete_subaccount_apikey",
            self._native_params(**{"subUid": sub_uid, "apiKey": api_key, "confirm": confirm}),
        )

    async def broker_get_all_subaccount_deposit_withdrawal(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """
        Get All Broker Sub-Account Deposit Withdrawal.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#get-all-broker-sub-account-deposit-withdrawal
        """
        return await self._native_private(
            "broker_get_all_subaccount_deposit_withdrawal",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                    "status": status,
                }
            ),
        )

    async def broker_get_broker_commission(
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
        return await self._native_private(
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

    async def broker_get_subaccount_apikey(self, *, sub_uid: str) -> dict[str, Any]:
        """
        Get Broker Sub-Account API Key.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#get-broker-sub-account-api-key
        """
        return await self._native_private(
            "broker_get_subaccount_apikey", self._native_params(**{"subUid": sub_uid})
        )

    async def broker_get_subaccount_list(
        self, *, limit: str | None = None, cursor: str | None = None, status: str | None = None
    ) -> dict[str, Any]:
        """
        Get Broker Sub-Account List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#get-broker-sub-account-list
        """
        return await self._native_private(
            "broker_get_subaccount_list",
            self._native_params(**{"limit": limit, "cursor": cursor, "status": status}),
        )

    async def broker_modify_subaccount_apikey(
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
        return await self._native_private(
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

    async def broker_modify_subaccount(
        self, *, sub_uid: str, status: str | None = None, perm_list: str | None = None
    ) -> dict[str, Any]:
        """
        Modify Broker Sub-Account.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#modify-broker-sub-account
        """
        return await self._native_private(
            "broker_modify_subaccount",
            self._native_params(**{"subUid": sub_uid, "status": status, "permList": perm_list}),
        )

    async def broker_subaccount_deposit_address(
        self, *, sub_uid: str, coin: str, chain: str | None = None
    ) -> dict[str, Any]:
        """
        Get Broker Sub-Account Deposit Address.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#get-broker-sub-account-deposit-address
        """
        return await self._native_private(
            "broker_subaccount_deposit_address",
            self._native_params(**{"subUid": sub_uid, "coin": coin, "chain": chain}),
        )

    async def broker_subaccount_withdrawal(
        self,
        *,
        sub_uid: str,
        coin: str,
        dest: str,
        address: str,
        amount: str,
        chain: str | None = None,
        tag: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """
        Broker Sub-Account Withdrawal.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/broker/broker#broker-sub-account-withdrawal

        API withdrawals have no second confirmation; they execute on submit.
        """
        return await self._native_private(
            "broker_subaccount_withdrawal",
            self._native_params(
                **{
                    "subUid": sub_uid,
                    "coin": coin,
                    "dest": dest,
                    "address": address,
                    "amount": amount,
                    "chain": chain,
                    "tag": tag,
                    "clientOid": client_oid,
                }
            ),
        )

    async def cfd_account_get_fund_detail(self) -> dict[str, Any]:
        """
        Get Fund Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-account/cfd-account#get-cfd-fund-detail
        """
        return await self._native_private("cfd_account_get_fund_detail", self._native_params(**{}))

    async def cfd_account_transfer(
        self, *, coin: str, amount: str, account_type: str, direction: str
    ) -> dict[str, Any]:
        """
        Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-account/cfd-account#cfd-transfer
        """
        return await self._native_private(
            "cfd_account_transfer",
            self._native_params(
                **{
                    "coin": coin,
                    "amount": amount,
                    "accountType": account_type,
                    "direction": direction,
                }
            ),
        )

    async def cfd_account_get_transfer_records(
        self,
        *,
        transfer_id: str | None = None,
        sub_uid: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        direction: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Transfer Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-account/cfd-account#get-cfd-transfer-records
        """
        return await self._native_private(
            "cfd_account_get_transfer_records",
            self._native_params(
                **{
                    "transferId": transfer_id,
                    "subUid": sub_uid,
                    "startTime": start_time,
                    "endTime": end_time,
                    "direction": direction,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    async def cfd_account_get_financial_records(
        self,
        *,
        type_: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Financial Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-account/cfd-account#get-cfd-financial-records
        """
        return await self._native_private(
            "cfd_account_get_financial_records",
            self._native_params(
                **{
                    "type": type_,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    async def cfd_account_get_instruments(self, *, symbol: str | None = None) -> dict[str, Any]:
        """
        Get Instruments.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-account/cfd-account#get-cfd-instruments
        """
        return await self._native_private(
            "cfd_account_get_instruments", self._native_params(**{"symbol": symbol})
        )

    async def cfd_market_get_tickers(self, *, symbol: str | None = None) -> dict[str, Any]:
        """
        Get Tickers.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-market/cfd-market#get-cfd-tickers
        """
        return await self._native_private(
            "cfd_market_get_tickers", self._native_params(**{"symbol": symbol})
        )

    async def cfd_market_get_history_candlestick(
        self,
        *,
        symbol: str,
        interval: str,
        side: str,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Kline/Candlestick History.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-market/cfd-market#get-cfd-kline-candlestick-history
        """
        return await self._native_private(
            "cfd_market_get_history_candlestick",
            self._native_params(
                **{
                    "symbol": symbol,
                    "interval": interval,
                    "side": side,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    async def cfd_trade_place_order(
        self,
        *,
        symbol: str,
        order_type: str,
        side: str,
        qty: str,
        price: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
    ) -> dict[str, Any]:
        """
        Place CFD Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#place-cfd-order
        """
        return await self._native_private(
            "cfd_trade_place_order",
            self._native_params(
                **{
                    "symbol": symbol,
                    "orderType": order_type,
                    "side": side,
                    "qty": qty,
                    "price": price,
                    "takeProfit": take_profit,
                    "stopLoss": stop_loss,
                }
            ),
        )

    async def cfd_trade_modify_order(
        self,
        *,
        order_id: str,
        price: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
    ) -> dict[str, Any]:
        """
        Modify CFD Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#modify-cfd-order
        """
        return await self._native_private(
            "cfd_trade_modify_order",
            self._native_params(
                **{
                    "orderId": order_id,
                    "price": price,
                    "takeProfit": take_profit,
                    "stopLoss": stop_loss,
                }
            ),
        )

    async def cfd_trade_cancel_order(self, *, order_id: str) -> dict[str, Any]:
        """
        Cancel CFD Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#cancel-cfd-order
        """
        return await self._native_private(
            "cfd_trade_cancel_order", self._native_params(**{"orderId": order_id})
        )

    async def cfd_trade_cancel_all_orders(
        self, *, symbol: str | None = None, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Cancel All CFD Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#cancel-all-cfd-orders
        """
        require_confirmation(confirm)
        return await self._native_private(
            "cfd_trade_cancel_all_orders",
            self._native_params(**{"symbol": symbol, "confirm": confirm}),
        )

    async def cfd_trade_close_positions(self, *, position_id: str, qty: str) -> dict[str, Any]:
        """
        Close CFD Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#close-cfd-positions
        """
        return await self._native_private(
            "cfd_trade_close_positions",
            self._native_params(**{"positionId": position_id, "qty": qty}),
        )

    async def cfd_trade_close_all_positions(
        self, *, symbol: str | None = None, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Close All CFD Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#close-all-cfd-positions
        """
        require_confirmation(confirm)
        return await self._native_private(
            "cfd_trade_close_all_positions",
            self._native_params(**{"symbol": symbol, "confirm": confirm}),
        )

    async def cfd_trade_get_unfilled_orders(
        self, *, symbol: str, sub_uid: str | None = None
    ) -> dict[str, Any]:
        """
        Get CFD Unfilled Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#get-cfd-unfilled-orders
        """
        return await self._native_private(
            "cfd_trade_get_unfilled_orders",
            self._native_params(**{"symbol": symbol, "subUid": sub_uid}),
        )

    async def cfd_trade_get_order_history(
        self,
        *,
        symbol: str,
        sub_uid: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        page_no: str | None = None,
    ) -> dict[str, Any]:
        """
        Get CFD Order History.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#get-cfd-order-history
        """
        return await self._native_private(
            "cfd_trade_get_order_history",
            self._native_params(
                **{
                    "symbol": symbol,
                    "subUid": sub_uid,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "pageNo": page_no,
                }
            ),
        )

    async def cfd_trade_get_current_positions(
        self, *, symbol: str | None = None, sub_uid: str | None = None
    ) -> dict[str, Any]:
        """
        Get CFD Current Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-trade/cfd-trade#get-cfd-current-positions
        """
        return await self._native_private(
            "cfd_trade_get_current_positions",
            self._native_params(**{"symbol": symbol, "subUid": sub_uid}),
        )

    async def classic_affiliate_customer_info_get_commission_detail(
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
        return await self._native_private(
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

    async def classic_affiliate_customer_info_get_customer_assets(
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
        return await self._native_private(
            "classic_affiliate_customer_info_get_customer_assets",
            self._native_params(
                **{"pageNo": page_no, "pageSize": page_size, "uid": uid, "showSub": show_sub}
            ),
        )

    async def classic_affiliate_customer_info_get_customer_deposit(
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
        return await self._native_private(
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

    async def classic_affiliate_customer_info_get_customer_kyc_result(
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
        return await self._native_private(
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

    async def classic_affiliate_customer_info_get_customer_list(
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
        return await self._native_private(
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

    async def classic_affiliate_customer_info_get_customer_trade_volume(
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
        return await self._native_private(
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

    async def classic_affiliate_customer_info_get_direct_commissions(
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
        return await self._native_private(
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

    async def classic_affiliate_customer_info_get_sub_customer_list(
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
        return await self._native_private(
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

    async def classic_broker_apikey_create_subaccount_api_key(
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
        return await self._native_private(
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

    async def classic_broker_apikey_delete_subaccount_api_key(
        self, *, sub_uid: str, api_key: str, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Delete Subaccount ApiKey.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-apikey/classic-broker-apikey#delete-subaccount-apikey
        """
        require_confirmation(confirm)
        return await self._native_private(
            "classic_broker_apikey_delete_subaccount_api_key",
            self._native_params(**{"subUid": sub_uid, "apiKey": api_key, "confirm": confirm}),
        )

    async def classic_broker_apikey_subaccount_apikey_list(self, *, sub_uid: str) -> dict[str, Any]:
        """
        Get Subaccount Apikey.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-apikey/classic-broker-apikey#get-subaccount-apikey
        """
        return await self._native_private(
            "classic_broker_apikey_subaccount_apikey_list",
            self._native_params(**{"subUid": sub_uid}),
        )

    async def classic_broker_apikey_modify_subaccount_api_key(
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
        return await self._native_private(
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

    async def classic_broker_commission_get_total_commission(
        self, *, start_time: str | None = None, end_time: str | None = None
    ) -> dict[str, Any]:
        """
        Get Total Commission.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-commission/classic-broker-commission#get-total-commission
        """
        return await self._native_private(
            "classic_broker_commission_get_total_commission",
            self._native_params(**{"startTime": start_time, "endTime": end_time}),
        )

    async def classic_broker_commission_get_order_commission(
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
        return await self._native_private(
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

    async def classic_broker_commission_get_rebate_info(self, *, uid: str) -> dict[str, Any]:
        """
        Get Rebate Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-commission/classic-broker-commission#get-rebate-info
        """
        return await self._native_private(
            "classic_broker_commission_get_rebate_info", self._native_params(**{"uid": uid})
        )

    async def classic_broker_commission_get_sub_affiliate_info(
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
        return await self._native_private(
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

    async def classic_broker_subaccount_get_broker_account_info(self) -> dict[str, Any]:
        """
        Get Broker Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-broker-info
        """
        return await self._native_private(
            "classic_broker_subaccount_get_broker_account_info", self._native_params(**{})
        )

    async def classic_broker_subaccount_modify_subaccount_email(
        self, *, sub_uid: str, subaccount_email: str
    ) -> dict[str, Any]:
        """
        Modify Subaccount Email.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#modify-subaccount-email
        """
        return await self._native_private(
            "classic_broker_subaccount_modify_subaccount_email",
            self._native_params(**{"subUid": sub_uid, "subaccountEmail": subaccount_email}),
        )

    async def classic_broker_subaccount_create_subaccount(
        self, *, subaccount_name: str, label: str | None = None
    ) -> dict[str, Any]:
        """
        Create Subaccount.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#create-subaccount
        """
        return await self._native_private(
            "classic_broker_subaccount_create_subaccount",
            self._native_params(**{"subaccountName": subaccount_name, "label": label}),
        )

    async def classic_broker_subaccount_get_subaccount_list(
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
        return await self._native_private(
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

    async def classic_broker_subaccount_modify_suaccount(
        self, *, sub_uid: str, perm_list: list[Any], status: str, language: str | None = None
    ) -> dict[str, Any]:
        """
        Modify Subaccount.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#modify-subaccount
        """
        return await self._native_private(
            "classic_broker_subaccount_modify_suaccount",
            self._native_params(
                **{"subUid": sub_uid, "permList": perm_list, "status": status, "language": language}
            ),
        )

    async def classic_broker_subaccount_get_subaccount_email(
        self, *, sub_uid: str
    ) -> dict[str, Any]:
        """
        Get Subaccount Email.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-subaccount-email
        """
        return await self._native_private(
            "classic_broker_subaccount_get_subaccount_email",
            self._native_params(**{"subUid": sub_uid}),
        )

    async def classic_broker_subaccount_get_subaccount_spot_assets(
        self, *, sub_uid: str, coin: str | None = None, asset_type: str | None = None
    ) -> dict[str, Any]:
        """
        Get Subaccount Spot Assets.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-subaccount-spot-assets
        """
        return await self._native_private(
            "classic_broker_subaccount_get_subaccount_spot_assets",
            self._native_params(**{"subUid": sub_uid, "coin": coin, "assetType": asset_type}),
        )

    async def classic_broker_subaccount_get_subaccount_future_assets(
        self, *, sub_uid: str, product_type: str
    ) -> dict[str, Any]:
        """
        Get Subaccount Future Assets.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-subaccount-future-assets
        """
        return await self._native_private(
            "classic_broker_subaccount_get_subaccount_future_assets",
            self._native_params(**{"subUid": sub_uid, "productType": product_type}),
        )

    async def classic_broker_subaccount_create_subaccount_deposit_address(
        self, *, sub_uid: str, coin: str, chain: str | None = None
    ) -> dict[str, Any]:
        """
        Create Subaccount Deposit Address.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#create-subaccount-deposit-address
        """
        return await self._native_private(
            "classic_broker_subaccount_create_subaccount_deposit_address",
            self._native_params(**{"subUid": sub_uid, "coin": coin, "chain": chain}),
        )

    async def classic_broker_subaccount_subaccount_withdraw(
        self,
        *,
        sub_uid: str,
        coin: str,
        dest: str,
        address: str,
        amount: str,
        chain: str | None = None,
        tag: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """
        Subaccount Withdrawal.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#subaccount-withdrawal

        API withdrawals have no second confirmation; they execute on submit.
        """
        return await self._native_private(
            "classic_broker_subaccount_subaccount_withdraw",
            self._native_params(
                **{
                    "subUid": sub_uid,
                    "coin": coin,
                    "dest": dest,
                    "address": address,
                    "amount": amount,
                    "chain": chain,
                    "tag": tag,
                    "clientOid": client_oid,
                }
            ),
        )

    async def classic_broker_subaccount_subaccount_deposit_auto_transfer(
        self, *, sub_uid: str, coin: str, to_account_type: str
    ) -> dict[str, Any]:
        """
        Sub Deposit Auto Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#sub-deposit-auto-transfer
        """
        return await self._native_private(
            "classic_broker_subaccount_subaccount_deposit_auto_transfer",
            self._native_params(
                **{"subUid": sub_uid, "coin": coin, "toAccountType": to_account_type}
            ),
        )

    async def classic_broker_subaccount_subaccount_deposit_records(
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
        return await self._native_private(
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

    async def classic_broker_subaccount_subaccount_withdrawal_records(
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
        Sub Withdrawal Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#sub-withdrawal-records
        """
        return await self._native_private(
            "classic_broker_subaccount_subaccount_withdrawal_records",
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

    async def classic_broker_subaccount_get_subaccount_all_deposit_withdrawal_records(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        id_less_than: str | None = None,
        type_: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Sub-accounts Deposit and Withdrawal Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#get-sub-accounts-deposit-and-withdrawal-records
        """
        return await self._native_private(
            "classic_broker_subaccount_get_subaccount_all_deposit_withdrawal_records",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "idLessThan": id_less_than,
                    "type": type_,
                }
            ),
        )

    async def classic_broker_subaccount_get_broker_subaccounts(
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
        return await self._native_private(
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

    async def classic_broker_subaccount_get_broker_subaccounts_commissions(
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
        return await self._native_private(
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

    async def classic_broker_subaccount_get_broker_trade_volume(
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
        return await self._native_private(
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

    async def classic_common_apidata_account_long_short(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get Futures Active Long Short Account Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-futures-active-long-short-account-data
        """
        return await self._native_public(
            "classic_common_apidata_account_long_short",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    async def classic_common_apidata_fund_net_flow(self, *, symbol: str) -> dict[str, Any]:
        """
        Get Spot 24H Net Capital Inflow Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-spot-24h-net-capital-inflow-info
        """
        return await self._native_public(
            "classic_common_apidata_fund_net_flow", self._native_params(**{"symbol": symbol})
        )

    async def classic_common_apidata_get_big_data_symbol(self) -> dict[str, Any]:
        """
        Get Trade data support symbols.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-trade-data-support-symbols
        """
        return await self._native_public(
            "classic_common_apidata_get_big_data_symbol", self._native_params(**{})
        )

    async def classic_common_apidata_get_spot_fund_flow(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get spot fund flow.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-spot-fund-flow
        """
        return await self._native_public(
            "classic_common_apidata_get_spot_fund_flow",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    async def classic_common_apidata_long_short(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get Futures Long and Short Ratio Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-futures-long-and-short-ratio-data
        """
        return await self._native_public(
            "classic_common_apidata_long_short",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    async def classic_common_apidata_margin_iso_borrow_ratio(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get Isolated margin borrowing ratio Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-isolated-margin-borrowing-ratio-data
        """
        return await self._native_public(
            "classic_common_apidata_margin_iso_borrow_ratio",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    async def classic_common_apidata_margin_loan_growth(
        self, *, symbol: str, period: str | None = None, coin: str | None = None
    ) -> dict[str, Any]:
        """
        Get Margin loan growth rate Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-margin-loan-growth-rate-data
        """
        return await self._native_public(
            "classic_common_apidata_margin_loan_growth",
            self._native_params(**{"symbol": symbol, "period": period, "coin": coin}),
        )

    async def classic_common_apidata_margin_ls_ratio(
        self, *, symbol: str, period: str | None = None, coin: str | None = None
    ) -> dict[str, Any]:
        """
        Get Leveraged long-short ratio Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-leveraged-long-short-ratio-data
        """
        return await self._native_public(
            "classic_common_apidata_margin_ls_ratio",
            self._native_params(**{"symbol": symbol, "period": period, "coin": coin}),
        )

    async def classic_common_apidata_position_long_short(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get Futures Active Long Short Position Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-futures-active-long-short-position-data
        """
        return await self._native_public(
            "classic_common_apidata_position_long_short",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    async def classic_common_apidata_taker_buy_sell(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get Futures Active Buy Sell Volume Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-futures-active-buy-sell-volume-data
        """
        return await self._native_public(
            "classic_common_apidata_taker_buy_sell",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    async def classic_common_apidata_whale_net_flow(self, *, symbol: str) -> dict[str, Any]:
        """
        Get Spot Whale Net Flow Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-spot-whale-net-flow-data
        """
        return await self._native_public(
            "classic_common_apidata_whale_net_flow", self._native_params(**{"symbol": symbol})
        )

    async def classic_common_notice_get_all_notices(
        self,
        *,
        language: str,
        ann_type: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        cursor: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Query Announcements.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-notice/classic-common-notice#query-announcements
        """
        return await self._native_public(
            "classic_common_notice_get_all_notices",
            self._native_params(
                **{
                    "language": language,
                    "annType": ann_type,
                    "startTime": start_time,
                    "endTime": end_time,
                    "cursor": cursor,
                    "limit": limit,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_copy_settings(
        self,
        *,
        trader_id: str,
        copy_amount: str,
        copy_all_postions: str | None = None,
        auto_copy: str | None = None,
        equity_guardian: str | None = None,
        equity_guardian_mode: str | None = None,
        equity: str | None = None,
        margin_mode: str | None = None,
        leverage: str | None = None,
        multiple: str | None = None,
    ) -> dict[str, Any]:
        """
        Copy settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#copy-settings
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_copy_settings",
            self._native_params(
                **{
                    "traderId": trader_id,
                    "copyAmount": copy_amount,
                    "copyAllPostions": copy_all_postions,
                    "autoCopy": auto_copy,
                    "equityGuardian": equity_guardian,
                    "equityGuardianMode": equity_guardian_mode,
                    "equity": equity,
                    "marginMode": margin_mode,
                    "leverage": leverage,
                    "multiple": multiple,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_query_current_orders(
        self,
        *,
        product_type: str,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        symbol: str | None = None,
        trader_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Current Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#get-current-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_query_current_orders",
            self._native_params(
                **{
                    "productType": product_type,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "symbol": symbol,
                    "traderId": trader_id,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_query_history_orders(
        self,
        *,
        product_type: str,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        symbol: str | None = None,
        trader_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#get-history-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_query_history_orders",
            self._native_params(
                **{
                    "productType": product_type,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "symbol": symbol,
                    "traderId": trader_id,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_setting_tpsl(
        self,
        *,
        tracking_no: str,
        product_type: str,
        symbol: str | None = None,
        stop_surplus_price: str | None = None,
        stop_loss_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Set TPSL.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#set-tpsl
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_setting_tpsl",
            self._native_params(
                **{
                    "trackingNo": tracking_no,
                    "productType": product_type,
                    "symbol": symbol,
                    "stopSurplusPrice": stop_surplus_price,
                    "stopLossPrice": stop_loss_price,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_close_positions(
        self,
        *,
        product_type: str,
        tracking_no: str | None = None,
        symbol: str | None = None,
        margin_coin: str | None = None,
        margin_mode: str | None = None,
        hold_side: str | None = None,
    ) -> dict[str, Any]:
        """
        Close Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#close-positions
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_close_positions",
            self._native_params(
                **{
                    "productType": product_type,
                    "trackingNo": tracking_no,
                    "symbol": symbol,
                    "marginCoin": margin_coin,
                    "marginMode": margin_mode,
                    "holdSide": hold_side,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_query_settings(
        self, *, trader_id: str
    ) -> dict[str, Any]:
        """
        Get Copy Trade Settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#get-copy-trade-settings
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_query_settings",
            self._native_params(**{"traderId": trader_id}),
        )

    async def classic_copytrading_future_copytrade_follower_settings(
        self,
        *,
        trader_id: str,
        settings: list[Any],
        auto_copy: str | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Set Copy Trade Settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#set-copy-trade-settings
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_settings",
            self._native_params(
                **{"traderId": trader_id, "settings": settings, "autoCopy": auto_copy, "mode": mode}
            ),
        )

    async def classic_copytrading_future_copytrade_follower_cancel_trader(
        self, *, trader_id: str
    ) -> dict[str, Any]:
        """
        Unfollow the Trader.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#unfollow-the-trader
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_cancel_trader",
            self._native_params(**{"traderId": trader_id}),
        )

    async def classic_copytrading_future_copytrade_follower_query_traders(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """
        Get My Traders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#get-my-traders
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_query_traders",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageNo": page_no,
                    "pageSize": page_size,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_query_quantity_limit(
        self, *, product_type: str, symbol: str | None = None
    ) -> dict[str, Any]:
        """
        Get Follow Limit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#get-follow-limit
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_query_quantity_limit",
            self._native_params(**{"productType": product_type, "symbol": symbol}),
        )

    async def classic_copytrading_future_copytrade_trader_create_copy_api(
        self, *, passphrase: str
    ) -> dict[str, Any]:
        """
        Create Copy ApiKey.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#create-copy-apikey
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_create_copy_api",
            self._native_params(**{"passphrase": passphrase}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_order_current_track(
        self,
        *,
        product_type: str,
        symbol: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        id_greater_than: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Current Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-current-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_order_current_track",
            self._native_params(
                **{
                    "productType": product_type,
                    "symbol": symbol,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "idGreaterThan": id_greater_than,
                    "idLessThan": id_less_than,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_trader_trader_order_history_track(
        self,
        *,
        product_type: str,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        order: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-history-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_order_history_track",
            self._native_params(
                **{
                    "productType": product_type,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "order": order,
                    "symbol": symbol,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_trader_trader_order_close_positions(
        self, *, product_type: str, tracking_no: str | None = None, symbol: str | None = None
    ) -> dict[str, Any]:
        """
        Close Tracking Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#close-tracking-order
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_order_close_positions",
            self._native_params(
                **{"productType": product_type, "trackingNo": tracking_no, "symbol": symbol}
            ),
        )

    async def classic_copytrading_future_copytrade_trader_trader_order_modify_tpsl(
        self,
        *,
        tracking_no: str,
        product_type: str,
        symbol: str | None = None,
        stop_surplus_price: str | None = None,
        stop_loss_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Modify Tracking Order TPSL.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#modify-tracking-order-tpsl
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_order_modify_tpsl",
            self._native_params(
                **{
                    "trackingNo": tracking_no,
                    "productType": product_type,
                    "symbol": symbol,
                    "stopSurplusPrice": stop_surplus_price,
                    "stopLossPrice": stop_loss_price,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_trader_trader_order_total_detail(
        self,
    ) -> dict[str, Any]:
        """
        Get Tracking Order Summary.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-tracking-order-summary
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_order_total_detail",
            self._native_params(**{}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_profit_history_summarys(
        self,
    ) -> dict[str, Any]:
        """
        Get History Profit Summary.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-history-profit-summary
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_profit_history_summarys",
            self._native_params(**{}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_profit_history_details(
        self,
        *,
        coin: str | None = None,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Profit Share Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-history-profit-share-detail
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_profit_history_details",
            self._native_params(
                **{
                    "coin": coin,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_trader_trader_profit_details(
        self, *, coin: str | None = None, page_size: str | None = None, page_no: str | None = None
    ) -> dict[str, Any]:
        """
        Get Profit Share Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-profit-share-detail
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_profit_details",
            self._native_params(**{"coin": coin, "pageSize": page_size, "pageNo": page_no}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_get_profits_group_coin_date(
        self, *, page_size: str | None = None, page_no: str | None = None
    ) -> dict[str, Any]:
        """
        Get Profit Share Group by Coin & Date.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-profit-share-group-by-coin-date
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_get_profits_group_coin_date",
            self._native_params(**{"pageSize": page_size, "pageNo": page_no}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_get_config_query_symbols(
        self, *, product_type: str
    ) -> dict[str, Any]:
        """
        Get Copy Trade Symbol Settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-copy-trade-symbol-settings
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_get_config_query_symbols",
            self._native_params(**{"productType": product_type}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_config_setting_symbols(
        self, *, setting_list: list[Any]
    ) -> dict[str, Any]:
        """
        Change Copy Trade Symbol Setting.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#change-copy-trade-symbol-setting
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_config_setting_symbols",
            self._native_params(**{"settingList": setting_list}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_config_settings_base(
        self,
        *,
        enable: str | None = None,
        show_total_equity: str | None = None,
        show_tpsl: str | None = None,
    ) -> dict[str, Any]:
        """
        Change Global Copy Trade Setting.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#change-global-copy-trade-setting
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_config_settings_base",
            self._native_params(
                **{"enable": enable, "showTotalEquity": show_total_equity, "showTpsl": show_tpsl}
            ),
        )

    async def classic_copytrading_future_copytrade_trader_config_query_followers(
        self,
        *,
        page_no: str | None = None,
        page_size: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        Get My Followers.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-my-followers
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_config_query_followers",
            self._native_params(
                **{
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_trader_config_remove_follower(
        self, *, follower_uid: str
    ) -> dict[str, Any]:
        """
        Remove Follower.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#remove-follower
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_config_remove_follower",
            self._native_params(**{"followerUid": follower_uid}),
        )

    async def classic_copytrading_spot_copytrade_follower_cancel_trader(
        self, *, trader_id: str
    ) -> dict[str, Any]:
        """
        Cancel Follow.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#cancel-follow
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_cancel_trader",
            self._native_params(**{"traderId": trader_id}),
        )

    async def classic_copytrading_spot_copytrade_follower_order_close_tracking(
        self, *, tracking_no_list: list[Any], symbol: str
    ) -> dict[str, Any]:
        """
        Sell And Sell in Batch.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#sell-and-sell-in-batch
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_order_close_tracking",
            self._native_params(**{"trackingNoList": tracking_no_list, "symbol": symbol}),
        )

    async def classic_copytrading_spot_copytrade_follower_query_current_orders(
        self,
        *,
        symbol: str | None = None,
        trader_id: str | None = None,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Current Copy Trade Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#get-current-copy-trade-orders
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_query_current_orders",
            self._native_params(
                **{
                    "symbol": symbol,
                    "traderId": trader_id,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_follower_query_history_orders(
        self,
        *,
        symbol: str | None = None,
        trader_id: str | None = None,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#get-history-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_query_history_orders",
            self._native_params(
                **{
                    "symbol": symbol,
                    "traderId": trader_id,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_follower_query_settings(
        self, *, trader_id: str
    ) -> dict[str, Any]:
        """
        Get Follow Configuration.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#get-follow-configuration
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_query_settings",
            self._native_params(**{"traderId": trader_id}),
        )

    async def classic_copytrading_spot_copytrade_follower_query_trader_symbols(
        self, *, trader_id: str
    ) -> dict[str, Any]:
        """
        Get Trader's Current Trading Pair.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#get-traders-current-trading-pair
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_query_trader_symbols",
            self._native_params(**{"traderId": trader_id}),
        )

    async def classic_copytrading_spot_copytrade_follower_query_traders(
        self,
        *,
        page_no: str | None = None,
        page_size: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        My Trader List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#my-trader-list
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_query_traders",
            self._native_params(
                **{
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_follower_setting_tpsl(
        self,
        *,
        tracking_no: str,
        stop_surplus_price: str | None = None,
        stop_loss_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Set Take Profit And Stop Loss.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#set-take-profit-and-stop-loss
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_setting_tpsl",
            self._native_params(
                **{
                    "trackingNo": tracking_no,
                    "stopSurplusPrice": stop_surplus_price,
                    "stopLossPrice": stop_loss_price,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_follower_settings(
        self,
        *,
        trader_id: str,
        settings: list[Any],
        auto_copy: str | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Add or Modify Following Configurations.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#add-or-modify-following-configurations
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_settings",
            self._native_params(
                **{"traderId": trader_id, "settings": settings, "autoCopy": auto_copy, "mode": mode}
            ),
        )

    async def classic_copytrading_spot_copytrade_follower_stop_order(
        self, *, tracking_no_list: list[Any]
    ) -> dict[str, Any]:
        """
        Stop The Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#stop-the-order
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_stop_order",
            self._native_params(**{"trackingNoList": tracking_no_list}),
        )

    async def classic_copytrading_spot_copytrade_trader_config_query_followers(
        self,
        *,
        page_no: str | None = None,
        page_size: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        My Follower List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#my-follower-list
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_config_query_followers",
            self._native_params(
                **{
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_trader_config_query_settings(
        self,
    ) -> dict[str, Any]:
        """
        Get Copytrade Configuration.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-copytrade-configuration
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_config_query_settings",
            self._native_params(**{}),
        )

    async def classic_copytrading_spot_copytrade_trader_config_remove_follower(
        self, *, follower_uid: str
    ) -> dict[str, Any]:
        """
        Remove Followers.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#remove-followers
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_config_remove_follower",
            self._native_params(**{"followerUid": follower_uid}),
        )

    async def classic_copytrading_spot_copytrade_trader_config_setting_symbols(
        self, *, symbol_list: list[Any], setting_type: str
    ) -> dict[str, Any]:
        """
        Set Copytrade Symbols.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#set-copytrade-symbols
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_config_setting_symbols",
            self._native_params(**{"symbolList": symbol_list, "settingType": setting_type}),
        )

    async def classic_copytrading_spot_copytrade_trader_order_close_tracking(
        self, *, tracking_no_list: list[Any], symbol: str
    ) -> dict[str, Any]:
        """
        Sell And Sell in Batch.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#sell-and-sell-in-batch
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_order_close_tracking",
            self._native_params(**{"trackingNoList": tracking_no_list, "symbol": symbol}),
        )

    async def classic_copytrading_spot_copytrade_trader_order_current_track(
        self,
        *,
        symbol: str | None = None,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Current Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-current-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_order_current_track",
            self._native_params(
                **{
                    "symbol": symbol,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_trader_order_history_track(
        self,
        *,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-history-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_order_history_track",
            self._native_params(
                **{
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "symbol": symbol,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_trader_order_modify_tpsl(
        self,
        *,
        tracking_no: str,
        stop_surplus_price: str | None = None,
        stop_loss_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Modify Take Profit and Stop Loss.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#modify-take-profit-and-stop-loss
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_order_modify_tpsl",
            self._native_params(
                **{
                    "trackingNo": tracking_no,
                    "stopSurplusPrice": stop_surplus_price,
                    "stopLossPrice": stop_loss_price,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_trader_order_total_detail(self) -> dict[str, Any]:
        """
        Get Data Indicator Statistics.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-data-indicator-statistics
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_order_total_detail",
            self._native_params(**{}),
        )

    async def classic_copytrading_spot_copytrade_trader_profit_details(
        self, *, coin: str | None = None, page_no: str | None = None, page_size: str | None = None
    ) -> dict[str, Any]:
        """
        Get Unrealized Profit Sharing Details.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-unrealized-profit-sharing-details
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_profit_details",
            self._native_params(**{"coin": coin, "pageNo": page_no, "pageSize": page_size}),
        )

    async def classic_copytrading_spot_copytrade_trader_profit_history_details(
        self,
        *,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Profit Sharing Details.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-history-profit-sharing-details
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_profit_history_details",
            self._native_params(
                **{
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "coin": coin,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_trader_profit_summarys(self) -> dict[str, Any]:
        """
        Get Profit Summary.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-profit-summary
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_profit_summarys", self._native_params(**{})
        )

    async def classic_instloan_account_get_ltv(
        self, *, risk_unit_id: str | None = None
    ) -> dict[str, Any]:
        """
        Get LTV.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-account/classic-instloan-account#get-ltv
        """
        return await self._native_private(
            "classic_instloan_account_get_ltv", self._native_params(**{"riskUnitId": risk_unit_id})
        )

    async def classic_instloan_account_bind_risk_unit(
        self, *, uid: str, operate: str, risk_unit_id: str | None = None
    ) -> dict[str, Any]:
        """
        Bind/Unbind Sub-account UID to Risk Unit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-account/classic-instloan-account#bind-unbind-sub-account-uid-to-risk-unit
        """
        return await self._native_private(
            "classic_instloan_account_bind_risk_unit",
            self._native_params(**{"uid": uid, "operate": operate, "riskUnitId": risk_unit_id}),
        )

    async def classic_instloan_account_get_risk_unit(self) -> dict[str, Any]:
        """
        Get Risk Unit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-account/classic-instloan-account#get-risk-unit
        """
        return await self._native_private(
            "classic_instloan_account_get_risk_unit", self._native_params(**{})
        )

    async def classic_instloan_account_get_transferred_amount_from_spot_account(
        self, *, coin: str, user_id: str | None = None
    ) -> dict[str, Any]:
        """
        Get transferable amount.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-account/classic-instloan-account#get-transferable-amount
        """
        return await self._native_private(
            "classic_instloan_account_get_transferred_amount_from_spot_account",
            self._native_params(**{"coin": coin, "userId": user_id}),
        )

    async def classic_instloan_orders_get_loan_orders(
        self,
        *,
        order_id: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Loan Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-orders/classic-instloan-orders#get-loan-orders
        """
        return await self._native_private(
            "classic_instloan_orders_get_loan_orders",
            self._native_params(
                **{"orderId": order_id, "startTime": start_time, "endTime": end_time}
            ),
        )

    async def classic_instloan_orders_get_repayment_orders(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Repayment Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-orders/classic-instloan-orders#get-repayment-orders
        """
        return await self._native_private(
            "classic_instloan_orders_get_repayment_orders",
            self._native_params(**{"startTime": start_time, "endTime": end_time, "limit": limit}),
        )

    async def classic_instloan_public_get_product_info(self, *, product_id: str) -> dict[str, Any]:
        """
        Get Product Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-public/classic-instloan-public#get-product-info
        """
        return await self._native_private(
            "classic_instloan_public_get_product_info",
            self._native_params(**{"productId": product_id}),
        )

    async def classic_instloan_public_get_margin_coin_info(
        self, *, product_id: str
    ) -> dict[str, Any]:
        """
        Get Margin Coin Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-public/classic-instloan-public#get-margin-coin-info
        """
        return await self._native_private(
            "classic_instloan_public_get_margin_coin_info",
            self._native_params(**{"productId": product_id}),
        )

    async def classic_instloan_public_get_spot_symbols(self, *, product_id: str) -> dict[str, Any]:
        """
        Get Spot Symbols.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-public/classic-instloan-public#get-spot-symbols
        """
        return await self._native_private(
            "classic_instloan_public_get_spot_symbols",
            self._native_params(**{"productId": product_id}),
        )

    async def classic_p2p_get_p2_p_merchant_list(
        self,
        *,
        online: str | None = None,
        id_less_than: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get P2P Merchant List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-p2p-p2p/classic-p2p#get-p2p-merchant-list
        """
        return await self._native_private(
            "classic_p2p_get_p2_p_merchant_list",
            self._native_params(**{"online": online, "idLessThan": id_less_than, "limit": limit}),
        )

    async def classic_p2p_get_merchant_information(self) -> dict[str, Any]:
        """
        Get Merchant Information.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-p2p-p2p/classic-p2p#get-merchant-information
        """
        return await self._native_private(
            "classic_p2p_get_merchant_information", self._native_params(**{})
        )

    async def classic_p2p_get_p2_p_adv_list(
        self,
        *,
        start_time: str,
        status: str,
        side: str,
        coin: str,
        fiat: str,
        end_time: str | None = None,
        id_less_than: str | None = None,
        limit: str | None = None,
        adv_no: str | None = None,
        language: str | None = None,
        order_by: str | None = None,
        pay_method_id: str | None = None,
        source_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Merchant Advertisement List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-p2p-p2p/classic-p2p#get-merchant-advertisement-list
        """
        return await self._native_private(
            "classic_p2p_get_p2_p_adv_list",
            self._native_params(
                **{
                    "startTime": start_time,
                    "status": status,
                    "side": side,
                    "coin": coin,
                    "fiat": fiat,
                    "endTime": end_time,
                    "idLessThan": id_less_than,
                    "limit": limit,
                    "advNo": adv_no,
                    "language": language,
                    "orderBy": order_by,
                    "payMethodId": pay_method_id,
                    "sourceType": source_type,
                }
            ),
        )

    async def classic_p2p_get_p2_p_order_list(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        id_less_than: str | None = None,
        limit: str | None = None,
        status: str | None = None,
        adv_no: str | None = None,
        side: str | None = None,
        coin: str | None = None,
        language: str | None = None,
        fiat: str | None = None,
        order_no: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Merchant P2P Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-p2p-p2p/classic-p2p#get-merchant-p2p-orders
        """
        return await self._native_private(
            "classic_p2p_get_p2_p_order_list",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "idLessThan": id_less_than,
                    "limit": limit,
                    "status": status,
                    "advNo": adv_no,
                    "side": side,
                    "coin": coin,
                    "language": language,
                    "fiat": fiat,
                    "orderNo": order_no,
                }
            ),
        )

    async def classic_spot_bgb_convert_bgb_convert(self, *, coin_list: list[Any]) -> dict[str, Any]:
        """
        Convert BGB.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-spot-bgb-convert/classic-spot-bgb-convert#convert-bgb
        """
        return await self._native_private(
            "classic_spot_bgb_convert_bgb_convert", self._native_params(**{"coinList": coin_list})
        )

    async def classic_spot_bgb_convert_get_bgb_convert_coins(self) -> dict[str, Any]:
        """
        Get BGB Convert Coins.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-spot-bgb-convert/classic-spot-bgb-convert#get-bgb-convert-coins
        """
        return await self._native_private(
            "classic_spot_bgb_convert_get_bgb_convert_coins", self._native_params(**{})
        )

    async def classic_spot_bgb_convert_get_bgb_convert_record(
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
        return await self._native_private(
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

    async def classic_tax_get_spot_account_record(
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
        return await self._native_private(
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

    async def classic_tax_get_future_account_record(
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
        return await self._native_private(
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

    async def classic_tax_get_margin_account_record(
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
        return await self._native_private(
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

    async def classic_tax_get_p2_p_account_record(
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
        return await self._native_private(
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

    async def copy_trading_follower_create_copy(
        self,
        *,
        project_id: str,
        type_: str,
        amount: str,
        account_type: str | None = None,
        trading_pair_list: str | None = None,
        margin_per_order: str | None = None,
        auto_copy: str | None = None,
        leverage: str | None = None,
        max_entry_slippage: str | None = None,
        max_margin_ratio: str | None = None,
        max_postion_value: str | None = None,
    ) -> dict[str, Any]:
        """
        Create Copy.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#create-copy
        """
        return await self._native_private(
            "copy_trading_follower_create_copy",
            self._native_params(
                **{
                    "projectId": project_id,
                    "type": type_,
                    "amount": amount,
                    "accountType": account_type,
                    "tradingPairList": trading_pair_list,
                    "marginPerOrder": margin_per_order,
                    "autoCopy": auto_copy,
                    "leverage": leverage,
                    "maxEntrySlippage": max_entry_slippage,
                    "maxMarginRatio": max_margin_ratio,
                    "maxPostionValue": max_postion_value,
                }
            ),
        )

    async def copy_trading_follower_modify_settings(
        self,
        *,
        project_id: str,
        trading_pair_list: str | None = None,
        margin_per_order: str | None = None,
        auto_copy: str | None = None,
        leverage: str | None = None,
        max_entry_slippage: str | None = None,
        max_margin_ratio: str | None = None,
        max_postion_value: str | None = None,
    ) -> dict[str, Any]:
        """
        Modify Follower Settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#modify-follower-settings
        """
        return await self._native_private(
            "copy_trading_follower_modify_settings",
            self._native_params(
                **{
                    "projectId": project_id,
                    "tradingPairList": trading_pair_list,
                    "marginPerOrder": margin_per_order,
                    "autoCopy": auto_copy,
                    "leverage": leverage,
                    "maxEntrySlippage": max_entry_slippage,
                    "maxMarginRatio": max_margin_ratio,
                    "maxPostionValue": max_postion_value,
                }
            ),
        )

    async def copy_trading_follower_unfollow(
        self, *, project_id: str, close_type: str | None = None
    ) -> dict[str, Any]:
        """
        Unfollow.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#unfollow
        """
        return await self._native_private(
            "copy_trading_follower_unfollow",
            self._native_params(**{"projectId": project_id, "closeType": close_type}),
        )

    async def copy_trading_follower_get_copy_settings(self, *, project_id: str) -> dict[str, Any]:
        """
        Get Copy Settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-copy-settings
        """
        return await self._native_private(
            "copy_trading_follower_get_copy_settings",
            self._native_params(**{"projectId": project_id}),
        )

    async def copy_trading_follower_copy_transfer(
        self,
        *,
        project_id: str,
        type_: str,
        coin: str,
        amount: str,
        in_account_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Copy Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#copy-transfer
        """
        return await self._native_private(
            "copy_trading_follower_copy_transfer",
            self._native_params(
                **{
                    "projectId": project_id,
                    "type": type_,
                    "coin": coin,
                    "amount": amount,
                    "inAccountType": in_account_type,
                }
            ),
        )

    async def copy_trading_follower_get_copy_transfer_record(
        self, *, project_id: str, limit: str | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        Get Copy Transfer Record.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-copy-transfer-record
        """
        return await self._native_private(
            "copy_trading_follower_get_copy_transfer_record",
            self._native_params(**{"projectId": project_id, "limit": limit, "cursor": cursor}),
        )

    async def copy_trading_follower_get_current_copy(self, *, project_id: str) -> dict[str, Any]:
        """
        Get Current Copy.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-current-copy
        """
        return await self._native_private(
            "copy_trading_follower_get_current_copy",
            self._native_params(**{"projectId": project_id}),
        )

    async def copy_trading_follower_get_copy_profit_details(
        self,
        *,
        project_id: str,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Copy Profit Details.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-copy-profit-details
        """
        return await self._native_private(
            "copy_trading_follower_get_copy_profit_details",
            self._native_params(
                **{
                    "projectId": project_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    async def copy_trading_follower_close_positions(
        self, *, project_id: str, symbol: str, qty: str, hold_side: str
    ) -> dict[str, Any]:
        """
        Close Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#close-positions
        """
        return await self._native_private(
            "copy_trading_follower_close_positions",
            self._native_params(
                **{"projectId": project_id, "symbol": symbol, "qty": qty, "holdSide": hold_side}
            ),
        )

    async def copy_trading_follower_close_all(
        self, *, project_id: str, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Close All.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#close-all
        """
        require_confirmation(confirm)
        return await self._native_private(
            "copy_trading_follower_close_all",
            self._native_params(**{"projectId": project_id, "confirm": confirm}),
        )

    async def copy_trading_follower_get_current_positions(
        self, *, project_id: str, symbol: str | None = None, pos_side: str | None = None
    ) -> dict[str, Any]:
        """
        Get Current Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-current-positions
        """
        return await self._native_private(
            "copy_trading_follower_get_current_positions",
            self._native_params(**{"projectId": project_id, "symbol": symbol, "posSide": pos_side}),
        )

    async def copy_trading_follower_place_tpsl(
        self,
        *,
        project_id: str,
        position_id: str,
        tp_trigger_by: str,
        sl_trigger_by: str,
        take_profit: str,
        stop_loss: str,
    ) -> dict[str, Any]:
        """
        Place TPSL.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#place-tpsl
        """
        return await self._native_private(
            "copy_trading_follower_place_tpsl",
            self._native_params(
                **{
                    "projectId": project_id,
                    "positionId": position_id,
                    "tpTriggerBy": tp_trigger_by,
                    "slTriggerBy": sl_trigger_by,
                    "takeProfit": take_profit,
                    "stopLoss": stop_loss,
                }
            ),
        )

    async def copy_trading_follower_modify_tpsl(
        self,
        *,
        project_id: str,
        strategy_id: str,
        tp_trigger_by: str,
        sl_trigger_by: str,
        take_profit: str,
        stop_loss: str,
    ) -> dict[str, Any]:
        """
        Modify TPSL.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#modify-tpsl
        """
        return await self._native_private(
            "copy_trading_follower_modify_tpsl",
            self._native_params(
                **{
                    "projectId": project_id,
                    "strategyId": strategy_id,
                    "tpTriggerBy": tp_trigger_by,
                    "slTriggerBy": sl_trigger_by,
                    "takeProfit": take_profit,
                    "stopLoss": stop_loss,
                }
            ),
        )

    async def copy_trading_follower_cancel_tpsl(
        self, *, project_id: str, strategy_id: str
    ) -> dict[str, Any]:
        """
        Cancel TPSL.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#cancel-tpsl
        """
        return await self._native_private(
            "copy_trading_follower_cancel_tpsl",
            self._native_params(**{"projectId": project_id, "strategyId": strategy_id}),
        )

    async def copy_trading_follower_get_current_tpsl_orders(
        self, *, project_id: str
    ) -> dict[str, Any]:
        """
        Get Current TPSL Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-current-tpsl-orders
        """
        return await self._native_private(
            "copy_trading_follower_get_current_tpsl_orders",
            self._native_params(**{"projectId": project_id}),
        )

    async def copy_trading_follower_get_tpsl_order_history(
        self,
        *,
        project_id: str,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get TPSL Order History.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-tpsl-order-history
        """
        return await self._native_private(
            "copy_trading_follower_get_tpsl_order_history",
            self._native_params(
                **{
                    "projectId": project_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    async def copy_trading_public_private_get_position_summary(self) -> dict[str, Any]:
        """
        Get Position Summary.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-position-summary
        """
        return await self._native_private(
            "copy_trading_public_private_get_position_summary", self._native_params(**{})
        )

    async def copy_trading_public_private_get_trading_pairs(self) -> dict[str, Any]:
        """
        Get Trading Pairs.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-trading-pairs
        """
        return await self._native_private(
            "copy_trading_public_private_get_trading_pairs", self._native_params(**{})
        )

    async def copy_trading_public_private_get_max_transferable(
        self, *, coin: str
    ) -> dict[str, Any]:
        """
        Get Max Transferable.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-max-transferable
        """
        return await self._native_private(
            "copy_trading_public_private_get_max_transferable",
            self._native_params(**{"coin": coin}),
        )

    async def copy_trading_public_private_transfer(
        self, *, type_: str, coin: str, amount: str, in_account_type: str | None = None
    ) -> dict[str, Any]:
        """
        Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#transfer
        """
        return await self._native_private(
            "copy_trading_public_private_transfer",
            self._native_params(
                **{"type": type_, "coin": coin, "amount": amount, "inAccountType": in_account_type}
            ),
        )

    async def copy_trading_public_private_get_transfer_record(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Transfer Record.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-transfer-record
        """
        return await self._native_private(
            "copy_trading_public_private_get_transfer_record",
            self._native_params(
                **{"startTime": start_time, "endTime": end_time, "limit": limit, "cursor": cursor}
            ),
        )

    async def copy_trading_public_private_get_current_followers(
        self, *, limit: str | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        Get Current Followers.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-current-followers
        """
        return await self._native_private(
            "copy_trading_public_private_get_current_followers",
            self._native_params(**{"limit": limit, "cursor": cursor}),
        )

    async def copy_trading_public_private_get_history_followers(
        self, *, limit: str | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        Get History Followers.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-history-followers
        """
        return await self._native_private(
            "copy_trading_public_private_get_history_followers",
            self._native_params(**{"limit": limit, "cursor": cursor}),
        )

    async def copy_trading_public_private_get_profit_summary(self) -> dict[str, Any]:
        """
        Get Profit Summary.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-profit-summary
        """
        return await self._native_private(
            "copy_trading_public_private_get_profit_summary", self._native_params(**{})
        )

    async def copy_trading_public_private_get_profit_details(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Profit Details.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-profit-details
        """
        return await self._native_private(
            "copy_trading_public_private_get_profit_details",
            self._native_params(
                **{"startTime": start_time, "endTime": end_time, "limit": limit, "cursor": cursor}
            ),
        )

    async def copy_trading_public_private_get_portfolio_overview(
        self, *, period: str
    ) -> dict[str, Any]:
        """
        Get Portfolio Overview.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-portfolio-overview
        """
        return await self._native_private(
            "copy_trading_public_private_get_portfolio_overview",
            self._native_params(**{"period": period}),
        )

    async def classic_earn_sharkfin_get_product(
        self, *, coin: str, limit: str | None = None, id_less_than: str | None = None
    ) -> dict[str, Any]:
        """
        Get Sharkfin Products.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#get-sharkfin-products
        """
        return await self._native_private(
            "classic_earn_sharkfin_get_product",
            self._native_params(**{"coin": coin, "limit": limit, "idLessThan": id_less_than}),
        )

    async def classic_earn_sharkfin_get_account(self) -> dict[str, Any]:
        """
        SharkFin Account.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#sharkfin-account
        """
        return await self._native_private(
            "classic_earn_sharkfin_get_account", self._native_params(**{})
        )

    async def classic_earn_sharkfin_get_assets(
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
        return await self._native_private(
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

    async def classic_earn_sharkfin_get_records(
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
        return await self._native_private(
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

    async def classic_earn_sharkfin_get_subscribe_info(self, *, product_id: str) -> dict[str, Any]:
        """
        SharkFin Subscription Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#sharkfin-subscription-detail
        """
        return await self._native_private(
            "classic_earn_sharkfin_get_subscribe_info",
            self._native_params(**{"productId": product_id}),
        )

    async def classic_earn_sharkfin_subscribe(
        self, *, product_id: str, amount: str
    ) -> dict[str, Any]:
        """
        Subscribe SharkFin.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#subscribe-sharkfin
        """
        return await self._native_private(
            "classic_earn_sharkfin_subscribe",
            self._native_params(**{"productId": product_id, "amount": amount}),
        )

    async def classic_earn_sharkfin_get_subscribe_result(self, *, order_id: str) -> dict[str, Any]:
        """
        SharkFin Subscription Result.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/earn-classic-sharkfin/classic-earn-sharkfin#sharkfin-subscription-result
        """
        return await self._native_private(
            "classic_earn_sharkfin_get_subscribe_result",
            self._native_params(**{"orderId": order_id}),
        )

    async def institutional_loan_bind_uid(
        self, *, uid: str, operate: str, risk_unit_id: str | None = None
    ) -> dict[str, Any]:
        """
        Bind/Unbind UID to Risk Unit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#bind-unbind-uid-to-risk-unit
        """
        return await self._native_private(
            "institutional_loan_bind_uid",
            self._native_params(**{"uid": uid, "operate": operate, "riskUnitId": risk_unit_id}),
        )

    async def institutional_loan_get_margin_coin_info(self, *, product_id: str) -> dict[str, Any]:
        """
        Get Margin Coin Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-margin-coin-info
        """
        return await self._native_private(
            "institutional_loan_get_margin_coin_info",
            self._native_params(**{"productId": product_id}),
        )

    async def institutional_loan_get_ltv(
        self, *, risk_unit_id: str | None = None
    ) -> dict[str, Any]:
        """
        Get LTV.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-ltv
        """
        return await self._native_private(
            "institutional_loan_get_ltv", self._native_params(**{"riskUnitId": risk_unit_id})
        )

    async def institutional_loan_get_loan_orders(
        self,
        *,
        order_id: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Loan Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-loan-orders
        """
        return await self._native_private(
            "institutional_loan_get_loan_orders",
            self._native_params(
                **{"orderId": order_id, "startTime": start_time, "endTime": end_time}
            ),
        )

    async def institutional_loan_get_product_info(self, *, product_id: str) -> dict[str, Any]:
        """
        Get Product Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-product-info
        """
        return await self._native_private(
            "institutional_loan_get_product_info", self._native_params(**{"productId": product_id})
        )

    async def institutional_loan_get_repayment_orders(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Repayment Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-repayment-orders
        """
        return await self._native_private(
            "institutional_loan_get_repayment_orders",
            self._native_params(**{"startTime": start_time, "endTime": end_time, "limit": limit}),
        )

    async def institutional_loan_get_risk_unit(self) -> dict[str, Any]:
        """
        Get Risk Unit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-risk-unit
        """
        return await self._native_private(
            "institutional_loan_get_risk_unit", self._native_params(**{})
        )

    async def institutional_loan_get_trade_symbols(self, *, product_id: str) -> dict[str, Any]:
        """
        Get Trade Symbols.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-trade-symbols
        """
        return await self._native_private(
            "institutional_loan_get_trade_symbols", self._native_params(**{"productId": product_id})
        )

    async def institutional_loan_get_transferred_quantity(
        self, *, coin: str, user_id: str | None = None
    ) -> dict[str, Any]:
        """
        Get Transferred Quantity.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-transferred-quantity
        """
        return await self._native_private(
            "institutional_loan_get_transferred_quantity",
            self._native_params(**{"coin": coin, "userId": user_id}),
        )

    async def p2p_ad_management_get_ad_list(
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
        return await self._native_private(
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

    async def p2p_ad_management_get_exchange_rate(self, *, token: str, fiat: str) -> dict[str, Any]:
        """
        Get Exchange Rate.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#get-exchange-rate
        """
        return await self._native_private(
            "p2p_ad_management_get_exchange_rate",
            self._native_params(**{"token": token, "fiat": fiat}),
        )

    async def p2p_ad_management_fee_simulate(
        self, *, token: str, fiat: str, side: str, market_type: str, amount: str
    ) -> dict[str, Any]:
        """
        Fee Simulate.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#fee-simulate
        """
        return await self._native_private(
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

    async def p2p_ad_management_get_ad_limit(
        self, *, token: str, fiat: str, side: str
    ) -> dict[str, Any]:
        """
        Get Ad Limit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#get-ad-limit
        """
        return await self._native_private(
            "p2p_ad_management_get_ad_limit",
            self._native_params(**{"token": token, "fiat": fiat, "side": side}),
        )

    async def p2p_ad_management_create_ad(
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
        return await self._native_private(
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

    async def p2p_ad_management_update_ad(
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
        return await self._native_private(
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

    async def p2p_ad_management_operate_ad(self, *, adv_id: str, operation: str) -> dict[str, Any]:
        """
        Operate Ad.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#operate-ad
        """
        return await self._native_private(
            "p2p_ad_management_operate_ad",
            self._native_params(**{"advId": adv_id, "operation": operation}),
        )

    async def p2p_ad_management_get_ad_info(self, *, adv_id: str) -> dict[str, Any]:
        """
        Get Ad Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/ad-management#get-ad-info
        """
        return await self._native_private(
            "p2p_ad_management_get_ad_info", self._native_params(**{"advId": adv_id})
        )

    async def p2p_ad_management_get_my_ads(
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
        return await self._native_private(
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

    async def get_p2p_balance(self, *, token: str) -> dict[str, Any]:
        """
        Get Balance.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/common#get-balance
        """
        return await self._native_private(
            "get_p2p_balance", self._native_params(**{"token": token})
        )

    async def p2p_order_management_get_pending_orders(
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
        return await self._native_private(
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

    async def p2p_order_management_get_all_orders(
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
        return await self._native_private(
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

    async def p2p_order_management_get_order_info(self, *, order_id: str) -> dict[str, Any]:
        """
        Get Order Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/order-management#get-order-info
        """
        return await self._native_private(
            "p2p_order_management_get_order_info", self._native_params(**{"orderId": order_id})
        )

    async def p2p_order_management_confirm_payment(
        self, *, order_id: str, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Confirm Payment.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/order-management#confirm-payment
        """
        require_confirmation(confirm)
        return await self._native_private(
            "p2p_order_management_confirm_payment",
            self._native_params(**{"orderId": order_id, "confirm": confirm}),
        )

    async def p2p_order_management_release_asset(
        self, *, order_id: str, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Release Asset.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/order-management#release-asset
        """
        require_confirmation(confirm)
        return await self._native_private(
            "p2p_order_management_release_asset",
            self._native_params(**{"orderId": order_id, "confirm": confirm}),
        )

    async def p2p_user_info_get_user_info(self) -> dict[str, Any]:
        """
        Get User Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/user-info#get-user-info
        """
        return await self._native_private("p2p_user_info_get_user_info", self._native_params(**{}))

    async def p2p_user_info_get_currencies(self) -> dict[str, Any]:
        """
        Get Currencies.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/user-info#get-currencies
        """
        return await self._native_private("p2p_user_info_get_currencies", self._native_params(**{}))

    async def p2p_user_info_get_pay_methods(self) -> dict[str, Any]:
        """
        Get Pay Methods.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/p2p/user-info#get-pay-methods
        """
        return await self._native_private(
            "p2p_user_info_get_pay_methods", self._native_params(**{})
        )

    async def stock_plus_assets_transfer(
        self, *, coin: str | None = None, amount: str | None = None, direction: str | None = None
    ) -> dict[str, Any]:
        """
        Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/assets#transfer
        """
        return await self._native_private(
            "stock_plus_assets_transfer",
            self._native_params(**{"coin": coin, "amount": amount, "direction": direction}),
        )

    async def stock_plus_assets_get_transfer_records(
        self,
        *,
        transfer_id: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Check Transfer Records.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/assets#check-transfer-records
        """
        return await self._native_private(
            "stock_plus_assets_get_transfer_records",
            self._native_params(
                **{
                    "transferId": transfer_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    async def stock_plus_assets_get_account(self, *, currency: str | None = None) -> dict[str, Any]:
        """
        Check Account.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/assets#check-account
        """
        return await self._native_private(
            "stock_plus_assets_get_account", self._native_params(**{"currency": currency})
        )

    async def stock_plus_assets_get_cash_flow(
        self,
        *,
        start_time: int | float,
        end_time: int | float,
        business_type: str | None = None,
        symbol: str | None = None,
        page: int | float | None = None,
        size: int | float | None = None,
    ) -> dict[str, Any]:
        """
        Check Cash Flow.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/assets#check-cash-flow
        """
        return await self._native_private(
            "stock_plus_assets_get_cash_flow",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "businessType": business_type,
                    "symbol": symbol,
                    "page": page,
                    "size": size,
                }
            ),
        )

    async def stock_plus_assets_get_stock_position(
        self, *, symbol: str | None = None
    ) -> dict[str, Any]:
        """
        Check Stock Position.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/assets#check-stock-position
        """
        return await self._native_private(
            "stock_plus_assets_get_stock_position", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_options_quotes_get_option_quote(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Option Real-time Quote.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/options-quotes#get-option-quote
        """
        return await self._native_private(
            "stock_plus_options_quotes_get_option_quote", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_options_quotes_get_option_chain_info(
        self, *, symbol: str, expiry_date: str
    ) -> dict[str, Any]:
        """
        Check Option Chain.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/options-quotes#get-option-chain-info
        """
        return await self._native_private(
            "stock_plus_options_quotes_get_option_chain_info",
            self._native_params(**{"symbol": symbol, "expiryDate": expiry_date}),
        )

    async def stock_plus_options_quotes_get_option_expiry_date(
        self, *, symbol: str
    ) -> dict[str, Any]:
        """
        Check Option Expiry Date List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/options-quotes#get-option-expiry-date
        """
        return await self._native_private(
            "stock_plus_options_quotes_get_option_expiry_date",
            self._native_params(**{"symbol": symbol}),
        )

    async def stock_plus_options_quotes_get_option_volume(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Option Volume.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/options-quotes#get-option-volume
        """
        return await self._native_private(
            "stock_plus_options_quotes_get_option_volume", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_orders_place_order(
        self,
        *,
        symbol: str,
        order_type: str,
        side: str,
        submitted_quantity: str,
        time_in_force: str,
        submitted_price: str | None = None,
        trigger_price: str | None = None,
        limit_offset: str | None = None,
        trailing_amount: str | None = None,
        trailing_percent: str | None = None,
        expire_date: str | None = None,
        outside_rth: str | None = None,
        limit_depth_level: int | float | None = None,
        trigger_count: int | float | None = None,
        monitor_price: str | None = None,
        remark: str | None = None,
    ) -> dict[str, Any]:
        """
        Place Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#place-order
        """
        return await self._native_private(
            "stock_plus_orders_place_order",
            self._native_params(
                **{
                    "symbol": symbol,
                    "orderType": order_type,
                    "side": side,
                    "submittedQuantity": submitted_quantity,
                    "timeInForce": time_in_force,
                    "submittedPrice": submitted_price,
                    "triggerPrice": trigger_price,
                    "limitOffset": limit_offset,
                    "trailingAmount": trailing_amount,
                    "trailingPercent": trailing_percent,
                    "expireDate": expire_date,
                    "outsideRth": outside_rth,
                    "limitDepthLevel": limit_depth_level,
                    "triggerCount": trigger_count,
                    "monitorPrice": monitor_price,
                    "remark": remark,
                }
            ),
        )

    async def stock_plus_orders_modify_order(
        self,
        *,
        order_id: str,
        quantity: str,
        price: str | None = None,
        trigger_price: str | None = None,
        limit_offset: str | None = None,
        trailing_amount: str | None = None,
        trailing_percent: str | None = None,
        limit_depth_level: int | float | None = None,
        trigger_count: int | float | None = None,
        monitor_price: str | None = None,
        remark: str | None = None,
    ) -> dict[str, Any]:
        """
        Modify Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#modify-order
        """
        return await self._native_private(
            "stock_plus_orders_modify_order",
            self._native_params(
                **{
                    "orderId": order_id,
                    "quantity": quantity,
                    "price": price,
                    "triggerPrice": trigger_price,
                    "limitOffset": limit_offset,
                    "trailingAmount": trailing_amount,
                    "trailingPercent": trailing_percent,
                    "limitDepthLevel": limit_depth_level,
                    "triggerCount": trigger_count,
                    "monitorPrice": monitor_price,
                    "remark": remark,
                }
            ),
        )

    async def stock_plus_orders_cancel_order(
        self, *, symbol: str, order_id: str | None = None, client_oid: str | None = None
    ) -> dict[str, Any]:
        """
        Cancel Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#cancel-order
        """
        return await self._native_private(
            "stock_plus_orders_cancel_order",
            self._native_params(**{"symbol": symbol, "orderId": order_id, "clientOid": client_oid}),
        )

    async def stock_plus_orders_get_today_orders(
        self,
        *,
        symbol: str | None = None,
        status: str | None = None,
        side: str | None = None,
        market: str | None = None,
        order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Check Today Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#check-today-orders
        """
        return await self._native_private(
            "stock_plus_orders_get_today_orders",
            self._native_params(
                **{
                    "symbol": symbol,
                    "status": status,
                    "side": side,
                    "market": market,
                    "orderId": order_id,
                }
            ),
        )

    async def stock_plus_orders_get_history_orders(
        self,
        *,
        symbol: str | None = None,
        status: str | None = None,
        side: str | None = None,
        market: str | None = None,
        start_at: int | float | None = None,
        end_at: int | float | None = None,
    ) -> dict[str, Any]:
        """
        Check History Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#check-history-orders
        """
        return await self._native_private(
            "stock_plus_orders_get_history_orders",
            self._native_params(
                **{
                    "symbol": symbol,
                    "status": status,
                    "side": side,
                    "market": market,
                    "startAt": start_at,
                    "endAt": end_at,
                }
            ),
        )

    async def stock_plus_orders_get_order_detail(self, *, order_id: str) -> dict[str, Any]:
        """
        Check Order Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#check-order-detail
        """
        return await self._native_private(
            "stock_plus_orders_get_order_detail", self._native_params(**{"orderId": order_id})
        )

    async def stock_plus_orders_get_today_executions(
        self, *, symbol: str | None = None, order_id: str | None = None
    ) -> dict[str, Any]:
        """
        Check Today Executions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#check-today-executions
        """
        return await self._native_private(
            "stock_plus_orders_get_today_executions",
            self._native_params(**{"symbol": symbol, "orderId": order_id}),
        )

    async def stock_plus_orders_get_history_executions(
        self,
        *,
        symbol: str | None = None,
        start_at: int | float | None = None,
        end_at: int | float | None = None,
    ) -> dict[str, Any]:
        """
        Check History Executions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/orders#check-history-executions
        """
        return await self._native_private(
            "stock_plus_orders_get_history_executions",
            self._native_params(**{"symbol": symbol, "startAt": start_at, "endAt": end_at}),
        )

    async def stock_plus_stock_quotes_get_static_info(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Basic Information.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-basic-information
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_static_info", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_stock_quotes_get_candlestick(
        self,
        *,
        symbol: str,
        period: str,
        count: int,
        adjust_type: str,
        trade_sessions: str | None = None,
    ) -> dict[str, Any]:
        """
        Check Candlestick.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-candlestick
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_candlestick",
            self._native_params(
                **{
                    "symbol": symbol,
                    "period": period,
                    "count": count,
                    "adjustType": adjust_type,
                    "tradeSessions": trade_sessions,
                }
            ),
        )

    async def stock_plus_stock_quotes_get_history_candlestick(
        self,
        *,
        symbol: str,
        period: str,
        count: int,
        adjust_type: str,
        forward: bool | None = None,
        time: str | None = None,
        trade_sessions: str | None = None,
    ) -> dict[str, Any]:
        """
        Check History Candlestick.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-history-candlestick
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_history_candlestick",
            self._native_params(
                **{
                    "symbol": symbol,
                    "period": period,
                    "count": count,
                    "adjustType": adjust_type,
                    "forward": forward,
                    "time": time,
                    "tradeSessions": trade_sessions,
                }
            ),
        )

    async def stock_plus_stock_quotes_get_depth(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Order Book.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-order-book
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_depth", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_stock_quotes_get_intraday(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Intraday Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-intraday-data
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_intraday", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_stock_quotes_get_quote(self, *, symbol: str) -> dict[str, Any]:
        """
        Check Real-time Quote.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-real-time-quote
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_quote", self._native_params(**{"symbol": symbol})
        )

    async def stock_plus_stock_quotes_get_trade_detail(
        self, *, symbol: str, count: int
    ) -> dict[str, Any]:
        """
        Check Trade Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/stock-quotes#check-trade-detail
        """
        return await self._native_private(
            "stock_plus_stock_quotes_get_trade_detail",
            self._native_params(**{"symbol": symbol, "count": count}),
        )

    async def tax_get_tax_records(
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
        return await self._native_private(
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
