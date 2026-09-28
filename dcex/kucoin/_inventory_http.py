"""Official KuCoin affiliate, broker and copy-trading methods."""

from typing import Any

from ._trade_http import TradeHTTP


class InventoryHTTP(TradeHTTP):
    """Preserve native symbols and documented wire field types."""

    def get_v1_accounts_account_id(self, *, account_id: str) -> Any:  # noqa: ANN401
        """
        Get Account Detail - Spot.

        Source: https://www.kucoin.com/docs-new/rest/account-info/account-funding/get-account-detail-spot
        """
        return self._native_private(
            "get_v1_accounts_account_id", self._native_params(accountId=account_id)
        )

    def get_ua_v2_affiliate_query_invitees(
        self,
        *,
        user_type: str | None = None,
        referral_code: str | None = None,
        uid: str | None = None,
        registration_end_at: int | None = None,
        registration_start_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Invited.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/invited
        """
        return self._native_private(
            "get_ua_v2_affiliate_query_invitees",
            self._native_params(
                userType=user_type,
                referralCode=referral_code,
                uid=uid,
                registrationEndAt=registration_end_at,
                registrationStartAt=registration_start_at,
                page=page,
                pageSize=page_size,
            ),
        )

    def get_ua_v2_affiliate_query_my_commission(
        self,
        *,
        site_type: str | None = None,
        rebate_type: int | None = None,
        rebate_start_at: int | None = None,
        rebate_end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        data_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Commission.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/commission
        """
        return self._native_private(
            "get_ua_v2_affiliate_query_my_commission",
            self._native_params(
                siteType=site_type,
                rebateType=rebate_type,
                rebateStartAt=rebate_start_at,
                rebateEndAt=rebate_end_at,
                page=page,
                pageSize=page_size,
                dataType=data_type,
            ),
        )

    def get_ua_v2_affiliate_query_transaction_by_uid(
        self,
        *,
        uid: str,
        trade_type: str | None = None,
        trade_start_at: int | None = None,
        trade_end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Trade History.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/trade-history
        """
        return self._native_private(
            "get_ua_v2_affiliate_query_transaction_by_uid",
            self._native_params(
                uid=uid,
                tradeType=trade_type,
                tradeStartAt=trade_start_at,
                tradeEndAt=trade_end_at,
                page=page,
                pageSize=page_size,
            ),
        )

    def get_ua_v2_affiliate_query_transaction_by_time(
        self,
        *,
        uid: str | None = None,
        trade_type: str | None = None,
        trade_start_at: int,
        trade_end_at: int,
        last_id: int | None = None,
        direction: str | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Transaction.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/transaction
        """
        return self._native_private(
            "get_ua_v2_affiliate_query_transaction_by_time",
            self._native_params(
                uid=uid,
                tradeType=trade_type,
                tradeStartAt=trade_start_at,
                tradeEndAt=trade_end_at,
                lastId=last_id,
                direction=direction,
                pageSize=page_size,
            ),
        )

    def get_ua_v2_affiliate_query_kumining(
        self,
        *,
        uid: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: str | None = None,
        direction: str | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Kumining.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/kumining
        """
        return self._native_private(
            "get_ua_v2_affiliate_query_kumining",
            self._native_params(
                uid=uid,
                startAt=start_at,
                endAt=end_at,
                lastId=last_id,
                direction=direction,
                pageSize=page_size,
            ),
        )

    def get_v2_affiliate_query_invitees(
        self,
        *,
        user_type: str | None = None,
        referral_code: str | None = None,
        uid: str | None = None,
        registration_start_at: int | None = None,
        registration_end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Invited.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/get-invited
        """
        return self._native_private(
            "get_v2_affiliate_query_invitees",
            self._native_params(
                userType=user_type,
                referralCode=referral_code,
                uid=uid,
                registrationStartAt=registration_start_at,
                registrationEndAt=registration_end_at,
                page=page,
                pageSize=page_size,
            ),
        )

    def get_v2_affiliate_query_my_commission(
        self,
        *,
        site_type: str | None = None,
        rebate_type: int | None = None,
        rebate_start_at: int | None = None,
        rebate_end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        user_id: str | None = None,
        data_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Commission.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/get-commission
        """
        return self._native_private(
            "get_v2_affiliate_query_my_commission",
            self._native_params(
                siteType=site_type,
                rebateType=rebate_type,
                rebateStartAt=rebate_start_at,
                rebateEndAt=rebate_end_at,
                page=page,
                pageSize=page_size,
                userId=user_id,
                dataType=data_type,
            ),
        )

    def get_v2_affiliate_query_transaction_by_uid(
        self,
        *,
        uid: str,
        trade_type: str | None = None,
        trade_start_at: int | None = None,
        trade_end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Trade History.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/get-trade-history
        """
        return self._native_private(
            "get_v2_affiliate_query_transaction_by_uid",
            self._native_params(
                uid=uid,
                tradeType=trade_type,
                tradeStartAt=trade_start_at,
                tradeEndAt=trade_end_at,
                page=page,
                pageSize=page_size,
            ),
        )

    def get_v2_affiliate_query_transaction_by_time(
        self,
        *,
        uid: str | None = None,
        trade_type: str | None = None,
        trade_start_at: int,
        trade_end_at: int,
        last_id: int | None = None,
        direction: str | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Transaction.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/get-transaction
        """
        return self._native_private(
            "get_v2_affiliate_query_transaction_by_time",
            self._native_params(
                uid=uid,
                tradeType=trade_type,
                tradeStartAt=trade_start_at,
                tradeEndAt=trade_end_at,
                lastId=last_id,
                direction=direction,
                pageSize=page_size,
            ),
        )

    def get_v2_affiliate_query_kumining(
        self,
        *,
        uid: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: str | None = None,
        direction: str | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Kumining.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/get-kumining
        """
        return self._native_private(
            "get_v2_affiliate_query_kumining",
            self._native_params(
                uid=uid,
                startAt=start_at,
                endAt=end_at,
                lastId=last_id,
                direction=direction,
                pageSize=page_size,
            ),
        )

    def post_v2_broker_withdrawal(self, *, body: dict[str, Any]) -> Any:  # noqa: ANN401
        """
        Apply for Fast Withdrawal.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/apply-for-fast-withdrawal
        API withdrawals have no second confirmation; they execute on submit.
        This Fast API may return validation factors; submit them only if required
        by the exchange. The incomplete official schema is forwarded as a body object.
        """
        return self._native_private("post_v2_broker_withdrawal", self._native_params(body=body))

    def get_v2_broker_api_rebate_download(self, *, begin: str, end: str, trade_type: str) -> Any:  # noqa: ANN401
        """
        Get Broker Rebate.

        Source: https://www.kucoin.com/docs-new/rest/broker/api-broker/get-broker-rebate
        """
        return self._native_private(
            "get_v2_broker_api_rebate_download",
            self._native_params(begin=begin, end=end, tradeType=trade_type),
        )

    def get_v2_broker_query_my_commission(
        self,
        *,
        site_type: str | None = None,
        trade_type: str | None = None,
        rebate_type: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Commission.

        Source: https://www.kucoin.com/docs-new/rest/broker/api-broker/get-commission
        """
        return self._native_private(
            "get_v2_broker_query_my_commission",
            self._native_params(
                siteType=site_type,
                tradeType=trade_type,
                rebateType=rebate_type,
                startAt=start_at,
                endAt=end_at,
                page=page,
                pageSize=page_size,
            ),
        )

    def get_v2_broker_query_user(
        self,
        *,
        trade_type: str | None = None,
        uid: str | None = None,
        rcode: str | None = None,
        tag: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get User List.

        Source: https://www.kucoin.com/docs-new/rest/broker/api-broker/get-user-list
        """
        return self._native_private(
            "get_v2_broker_query_user",
            self._native_params(
                tradeType=trade_type,
                uid=uid,
                rcode=rcode,
                tag=tag,
                startAt=start_at,
                endAt=end_at,
                page=page,
                pageSize=page_size,
            ),
        )

    def get_v2_broker_query_detail_by_uid(
        self,
        *,
        trade_type: str | None = None,
        uid: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: str | None = None,
        direction: str | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get User Transactions.

        Source: https://www.kucoin.com/docs-new/rest/broker/api-broker/get-user-transactions
        """
        return self._native_private(
            "get_v2_broker_query_detail_by_uid",
            self._native_params(
                tradeType=trade_type,
                uid=uid,
                startAt=start_at,
                endAt=end_at,
                lastId=last_id,
                direction=direction,
                pageSize=page_size,
            ),
        )

    def get_v1_broker_nd_rebate_download(self, *, begin: str, end: str, trade_type: str) -> Any:  # noqa: ANN401
        """
        Get Broker Rebate.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-broker-rebate
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_v1_broker_nd_rebate_download",
            self._native_params(begin=begin, end=end, tradeType=trade_type),
        )

    def get_v3_broker_nd_rebate_download(self, *, begin: str, end: str, trade_type: str) -> Any:  # noqa: ANN401
        """
        Get Broker RebateV3.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-broker-rebatev3
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_v3_broker_nd_rebate_download",
            self._native_params(begin=begin, end=end, tradeType=trade_type),
        )

    def post_kyc_nd_broker_proxy_client_submit(
        self,
        *,
        client_uid: str,
        first_name: str,
        last_name: str,
        issue_country: str,
        birth_date: str,
        identity_type: str,
        identity_number: str,
        expire_date: str,
        front_photo: str | None = None,
        backend_photo: str | None = None,
        face_photo: str,
    ) -> Any:  # noqa: ANN401
        """
        Submit KYC.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/submit-kyc
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "post_kyc_nd_broker_proxy_client_submit",
            self._native_params(
                clientUid=client_uid,
                firstName=first_name,
                lastName=last_name,
                issueCountry=issue_country,
                birthDate=birth_date,
                identityType=identity_type,
                identityNumber=identity_number,
                expireDate=expire_date,
                frontPhoto=front_photo,
                backendPhoto=backend_photo,
                facePhoto=face_photo,
            ),
        )

    def get_kyc_nd_broker_proxy_client_status_list(self, *, client_uids: str) -> Any:  # noqa: ANN401
        """
        Get KYC Status.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-kyc-status
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_kyc_nd_broker_proxy_client_status_list",
            self._native_params(clientUids=client_uids),
        )

    def get_kyc_nd_broker_proxy_client_status_page(
        self, *, page_number: int | None = None, page_size: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get KYC Status List.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-kyc-status-list
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_kyc_nd_broker_proxy_client_status_page",
            self._native_params(pageNumber=page_number, pageSize=page_size),
        )

    def get_v1_broker_nd_info(self, *, begin: str, end: str, trade_type: str) -> Any:  # noqa: ANN401
        """
        Get Broker Info.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-broker-info
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_v1_broker_nd_info", self._native_params(begin=begin, end=end, tradeType=trade_type)
        )

    def post_v1_broker_nd_account(self, *, account_name: str) -> Any:  # noqa: ANN401
        """
        Add sub-account.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/add-subaccount
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "post_v1_broker_nd_account", self._native_params(accountName=account_name)
        )

    def get_v1_broker_nd_account(
        self,
        *,
        uid: str | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get sub-account.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-subaccount
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_v1_broker_nd_account",
            self._native_params(uid=uid, currentPage=current_page, pageSize=page_size),
        )

    def post_v1_broker_nd_account_apikey(
        self,
        *,
        uid: str,
        passphrase: str,
        ip_whitelist: list[Any] | None = None,
        permissions: list[Any] | None = None,
        label: str,
    ) -> Any:  # noqa: ANN401
        """
        Add sub-account API.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/add-subaccount-api
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "post_v1_broker_nd_account_apikey",
            self._native_params(
                uid=uid,
                passphrase=passphrase,
                ipWhitelist=ip_whitelist,
                permissions=permissions,
                label=label,
            ),
        )

    def get_v1_broker_nd_account_apikey(self, *, uid: str, api_key: str | None = None) -> Any:  # noqa: ANN401
        """
        Get sub-account API.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-subaccount-api
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_v1_broker_nd_account_apikey", self._native_params(uid=uid, apiKey=api_key)
        )

    def post_v1_broker_nd_account_update_apikey(
        self,
        *,
        uid: str,
        ip_whitelist: list[Any] | None = None,
        permissions: list[Any] | None = None,
        label: str,
        api_key: str,
    ) -> Any:  # noqa: ANN401
        """
        Modify sub-account API.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/modify-subaccount-api
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "post_v1_broker_nd_account_update_apikey",
            self._native_params(
                uid=uid,
                ipWhitelist=ip_whitelist,
                permissions=permissions,
                label=label,
                apiKey=api_key,
            ),
        )

    def delete_v1_broker_nd_account_apikey(
        self, *, uid: str, api_key: str, confirm: bool = False
    ) -> Any:  # noqa: ANN401
        """
        Delete sub-account API.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/delete-subaccount-api
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "delete_v1_broker_nd_account_apikey",
            self._native_params(uid=uid, apiKey=api_key, confirm=confirm),
        )

    def post_v1_broker_nd_transfer(
        self,
        *,
        currency: str,
        amount: str,
        direction: str,
        account_type: str,
        special_uid: str,
        special_account_type: str,
        client_oid: str,
    ) -> Any:  # noqa: ANN401
        """
        Transfer.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/transfer
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "post_v1_broker_nd_transfer",
            self._native_params(
                currency=currency,
                amount=amount,
                direction=direction,
                accountType=account_type,
                specialUid=special_uid,
                specialAccountType=special_account_type,
                clientOid=client_oid,
            ),
        )

    def get_v3_broker_nd_transfer_detail(self, *, order_id: str) -> Any:  # noqa: ANN401
        """
        Get Transfer History.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-transfer-history
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_v3_broker_nd_transfer_detail", self._native_params(orderId=order_id)
        )

    def get_v1_asset_ndbroker_deposit_list(
        self,
        *,
        currency: str | None = None,
        status: str | None = None,
        hash: str | None = None,
        start_timestamp: int | None = None,
        end_timestamp: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Deposit List.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-deposit-list
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_v1_asset_ndbroker_deposit_list",
            self._native_params(
                currency=currency,
                status=status,
                hash=hash,
                startTimestamp=start_timestamp,
                endTimestamp=end_timestamp,
                limit=limit,
            ),
        )

    def get_v3_broker_nd_deposit_detail(self, *, currency: str, hash: str) -> Any:  # noqa: ANN401
        """
        Get Deposit Detail.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-deposit-detail
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_v3_broker_nd_deposit_detail", self._native_params(currency=currency, hash=hash)
        )

    def get_v3_broker_nd_withdraw_detail(self, *, withdrawal_id: str) -> Any:  # noqa: ANN401
        """
        Get Withdraw Detail.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-withdraw-detail
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_v3_broker_nd_withdraw_detail", self._native_params(withdrawalId=withdrawal_id)
        )

    def post_v1_broker_nd_mark_up(
        self,
        *,
        sub_uids: list[Any] | None = None,
        effect_at: int | None = None,
        trade_type: str,
        maker_mark_up: str,
        taker_mark_up: str,
        effective_type: str,
    ) -> Any:  # noqa: ANN401
        """
        Set Markup Fee.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/setmarkup
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "post_v1_broker_nd_mark_up",
            self._native_params(
                subUids=sub_uids,
                effectAt=effect_at,
                tradeType=trade_type,
                makerMarkUp=maker_mark_up,
                takerMarkUp=taker_mark_up,
                effectiveType=effective_type,
            ),
        )

    def get_v1_broker_nd_mark_up(self, *, sub_uids: int | None = None) -> Any:  # noqa: ANN401
        """
        Get Markup Fee.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/getmarkup
        Uses the Broker host and the configured ND management API key.
        """
        return self._native_private(
            "get_v1_broker_nd_mark_up", self._native_params(subUids=sub_uids)
        )

    def post_v1_copy_trade_futures_orders(
        self,
        *,
        client_oid: str,
        side: str,
        symbol: str,
        leverage: int | None = None,
        type_: str,
        stop: str | None = None,
        stop_price_type: str | None = None,
        stop_price: str | None = None,
        reduce_only: bool | None = None,
        close_order: bool | None = None,
        margin_mode: str | None = None,
        price: str | None = None,
        size: int,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        position_side: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Add Order.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/add-order
        """
        return self._native_private(
            "post_v1_copy_trade_futures_orders",
            self._native_params(
                clientOid=client_oid,
                side=side,
                symbol=symbol,
                leverage=leverage,
                type=type_,
                stop=stop,
                stopPriceType=stop_price_type,
                stopPrice=stop_price,
                reduceOnly=reduce_only,
                closeOrder=close_order,
                marginMode=margin_mode,
                price=price,
                size=size,
                timeInForce=time_in_force,
                postOnly=post_only,
                positionSide=position_side,
            ),
        )

    def post_v1_copy_trade_futures_orders_test(
        self,
        *,
        client_oid: str,
        side: str,
        symbol: str,
        leverage: int,
        type_: str,
        stop: str | None = None,
        stop_price_type: str | None = None,
        stop_price: str | None = None,
        reduce_only: bool | None = None,
        close_order: bool | None = None,
        margin_mode: str | None = None,
        price: str | None = None,
        size: int,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        position_side: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Add Order Test.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/add-order-test
        """
        return self._native_private(
            "post_v1_copy_trade_futures_orders_test",
            self._native_params(
                clientOid=client_oid,
                side=side,
                symbol=symbol,
                leverage=leverage,
                type=type_,
                stop=stop,
                stopPriceType=stop_price_type,
                stopPrice=stop_price,
                reduceOnly=reduce_only,
                closeOrder=close_order,
                marginMode=margin_mode,
                price=price,
                size=size,
                timeInForce=time_in_force,
                postOnly=post_only,
                positionSide=position_side,
            ),
        )

    def post_v1_copy_trade_futures_st_orders(
        self,
        *,
        client_oid: str,
        side: str,
        symbol: str,
        leverage: int,
        type_: str,
        stop_price_type: str | None = None,
        reduce_only: bool | None = None,
        close_order: bool | None = None,
        margin_mode: str | None = None,
        price: str | None = None,
        size: int,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        trigger_stop_up_price: str | None = None,
        trigger_stop_down_price: str | None = None,
        position_side: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Add Take Profit And Stop Loss Order.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/add-take-profit-and-stop-loss-order
        """
        return self._native_private(
            "post_v1_copy_trade_futures_st_orders",
            self._native_params(
                clientOid=client_oid,
                side=side,
                symbol=symbol,
                leverage=leverage,
                type=type_,
                stopPriceType=stop_price_type,
                reduceOnly=reduce_only,
                closeOrder=close_order,
                marginMode=margin_mode,
                price=price,
                size=size,
                timeInForce=time_in_force,
                postOnly=post_only,
                triggerStopUpPrice=trigger_stop_up_price,
                triggerStopDownPrice=trigger_stop_down_price,
                positionSide=position_side,
            ),
        )

    def delete_v1_copy_trade_futures_orders(self, *, order_id: str | None = None) -> Any:  # noqa: ANN401
        """
        Cancel Order By OrderId.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/cancel-order-by-orderid
        """
        return self._native_private(
            "delete_v1_copy_trade_futures_orders", self._native_params(orderId=order_id)
        )

    def delete_v1_copy_trade_futures_orders_client_order(
        self, *, symbol: str, client_oid: str
    ) -> Any:  # noqa: ANN401
        """
        Cancel Order By ClientOid.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/cancel-order-by-clientoid
        """
        return self._native_private(
            "delete_v1_copy_trade_futures_orders_client_order",
            self._native_params(symbol=symbol, clientOid=client_oid),
        )

    def get_v1_copy_trade_futures_get_max_open_size(
        self, *, symbol: str, price: str, leverage: int
    ) -> Any:  # noqa: ANN401
        """
        Get Max Open Size.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/get-max-open-size
        """
        return self._native_private(
            "get_v1_copy_trade_futures_get_max_open_size",
            self._native_params(symbol=symbol, price=price, leverage=leverage),
        )

    def get_v1_copy_trade_futures_position_margin_max_withdraw_margin(
        self, *, symbol: str, position_side: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Max Withdraw Margin.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/get-max-withdraw-margin
        """
        return self._native_private(
            "get_v1_copy_trade_futures_position_margin_max_withdraw_margin",
            self._native_params(symbol=symbol, positionSide=position_side),
        )

    def post_v1_copy_trade_futures_position_margin_deposit_margin(
        self, *, symbol: str, margin: str, biz_no: str, position_side: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Add Isolated Margin.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/add-isolated-margin
        """
        return self._native_private(
            "post_v1_copy_trade_futures_position_margin_deposit_margin",
            self._native_params(
                symbol=symbol, margin=margin, bizNo=biz_no, positionSide=position_side
            ),
        )

    def post_v1_copy_trade_futures_position_margin_withdraw_margin(
        self, *, symbol: str, withdraw_amount: str, position_side: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Remove Isolated Margin.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/remove-isolated-margin
        """
        return self._native_private(
            "post_v1_copy_trade_futures_position_margin_withdraw_margin",
            self._native_params(
                symbol=symbol, withdrawAmount=withdraw_amount, positionSide=position_side
            ),
        )

    def post_v1_copy_trade_futures_position_risk_limit_level_change(
        self, *, symbol: str, level: int
    ) -> Any:  # noqa: ANN401
        """
        Modify Isolated Margin Risk Limit.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/modify-isolated-margin-risk-limit
        """
        return self._native_private(
            "post_v1_copy_trade_futures_position_risk_limit_level_change",
            self._native_params(symbol=symbol, level=level),
        )

    def post_v1_copy_trade_futures_position_margin_auto_deposit_status(
        self, *, symbol: str, status: bool, position_side: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Modify Isolated Margin Auto-Deposit Status.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/modify-isolated-margin-auto-deposit-status
        """
        return self._native_private(
            "post_v1_copy_trade_futures_position_margin_auto_deposit_status",
            self._native_params(symbol=symbol, status=status, positionSide=position_side),
        )

    def post_v1_copy_trade_futures_position_change_margin_mode(
        self, *, symbol: str, margin_mode: str
    ) -> Any:  # noqa: ANN401
        """
        Switch Margin Mode.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/switch-margin-mode
        """
        return self._native_private(
            "post_v1_copy_trade_futures_position_change_margin_mode",
            self._native_params(symbol=symbol, marginMode=margin_mode),
        )

    def post_v2_copy_trade_futures_change_cross_user_leverage(
        self, *, symbol: str, leverage: str
    ) -> Any:  # noqa: ANN401
        """
        Modify Cross Margin Leverage.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/modify-cross-margin-leverage
        """
        return self._native_private(
            "post_v2_copy_trade_futures_change_cross_user_leverage",
            self._native_params(symbol=symbol, leverage=leverage),
        )

    def post_v2_copy_trade_get_cross_mode_margin_requirement(
        self, *, symbol: str, leverage: str, position_value: str
    ) -> Any:  # noqa: ANN401
        """
        Get Cross Margin Requirement.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/get-cross-margin-requirement
        """
        return self._native_private(
            "post_v2_copy_trade_get_cross_mode_margin_requirement",
            self._native_params(symbol=symbol, leverage=leverage, positionValue=position_value),
        )

    def post_v2_copy_trade_position_switch_position_mode(self, *, position_mode: str) -> Any:  # noqa: ANN401
        """
        Switch Position Mode.

        Source: https://www.kucoin.com/docs-new/rest/copy-trading/switch-position-mode
        """
        return self._native_private(
            "post_v2_copy_trade_position_switch_position_mode",
            self._native_params(positionMode=position_mode),
        )
