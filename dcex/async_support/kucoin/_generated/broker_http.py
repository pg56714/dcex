"""Generated kucoin broker HTTP methods."""

from typing import Any

from .._trade_http import TradeHTTP


class GeneratedBrokerHTTP(TradeHTTP):
    """Broker API methods."""

    async def post_v2_broker_withdrawal(self, *, body: dict[str, Any]) -> Any:  # noqa: ANN401
        """
        Apply for Fast Withdrawal.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/apply-for-fast-withdrawal
        API withdrawals have no second confirmation; they execute on submit.
        This Fast API may return validation factors; submit them only if required
        by the exchange. The incomplete official schema is forwarded as a body object.
        """
        return await self._native_private(
            "post_v2_broker_withdrawal", self._native_params(body=body)
        )

    async def get_v2_broker_api_rebate_download(
        self, *, begin: str, end: str, trade_type: str
    ) -> Any:  # noqa: ANN401
        """
        Get Broker Rebate.

        Source: https://www.kucoin.com/docs-new/rest/broker/api-broker/get-broker-rebate
        """
        return await self._native_private(
            "get_v2_broker_api_rebate_download",
            self._native_params(begin=begin, end=end, tradeType=trade_type),
        )

    async def get_v2_broker_query_my_commission(
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
        return await self._native_private(
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

    async def get_v2_broker_query_user(
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
        return await self._native_private(
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

    async def get_v2_broker_query_detail_by_uid(
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
        return await self._native_private(
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

    async def get_v1_broker_nd_rebate_download(
        self, *, begin: str, end: str, trade_type: str
    ) -> Any:  # noqa: ANN401
        """
        Get Broker Rebate.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-broker-rebate
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_v1_broker_nd_rebate_download",
            self._native_params(begin=begin, end=end, tradeType=trade_type),
        )

    async def get_v3_broker_nd_rebate_download(
        self, *, begin: str, end: str, trade_type: str
    ) -> Any:  # noqa: ANN401
        """
        Get Broker RebateV3.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-broker-rebatev3
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_v3_broker_nd_rebate_download",
            self._native_params(begin=begin, end=end, tradeType=trade_type),
        )

    async def post_kyc_nd_broker_proxy_client_submit(
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
        return await self._native_private(
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

    async def get_kyc_nd_broker_proxy_client_status_list(self, *, client_uids: str) -> Any:  # noqa: ANN401
        """
        Get KYC Status.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-kyc-status
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_kyc_nd_broker_proxy_client_status_list",
            self._native_params(clientUids=client_uids),
        )

    async def get_kyc_nd_broker_proxy_client_status_page(
        self, *, page_number: int | None = None, page_size: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get KYC Status List.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-kyc-status-list
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_kyc_nd_broker_proxy_client_status_page",
            self._native_params(pageNumber=page_number, pageSize=page_size),
        )

    async def get_v1_broker_nd_info(self, *, begin: str, end: str, trade_type: str) -> Any:  # noqa: ANN401
        """
        Get Broker Info.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-broker-info
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_v1_broker_nd_info", self._native_params(begin=begin, end=end, tradeType=trade_type)
        )

    async def post_v1_broker_nd_account(self, *, account_name: str) -> Any:  # noqa: ANN401
        """
        Add sub-account.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/add-subaccount
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "post_v1_broker_nd_account", self._native_params(accountName=account_name)
        )

    async def get_v1_broker_nd_account(
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
        return await self._native_private(
            "get_v1_broker_nd_account",
            self._native_params(uid=uid, currentPage=current_page, pageSize=page_size),
        )

    async def post_v1_broker_nd_account_apikey(
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
        return await self._native_private(
            "post_v1_broker_nd_account_apikey",
            self._native_params(
                uid=uid,
                passphrase=passphrase,
                ipWhitelist=ip_whitelist,
                permissions=permissions,
                label=label,
            ),
        )

    async def get_v1_broker_nd_account_apikey(self, *, uid: str, api_key: str | None = None) -> Any:  # noqa: ANN401
        """
        Get sub-account API.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-subaccount-api
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_v1_broker_nd_account_apikey", self._native_params(uid=uid, apiKey=api_key)
        )

    async def post_v1_broker_nd_account_update_apikey(
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
        return await self._native_private(
            "post_v1_broker_nd_account_update_apikey",
            self._native_params(
                uid=uid,
                ipWhitelist=ip_whitelist,
                permissions=permissions,
                label=label,
                apiKey=api_key,
            ),
        )

    async def delete_v1_broker_nd_account_apikey(
        self, *, uid: str, api_key: str, confirm: bool = False
    ) -> Any:  # noqa: ANN401
        """
        Delete sub-account API.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/delete-subaccount-api
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "delete_v1_broker_nd_account_apikey",
            self._native_params(uid=uid, apiKey=api_key, confirm=confirm),
        )

    async def post_v1_broker_nd_transfer(
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
        return await self._native_private(
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

    async def get_v3_broker_nd_transfer_detail(self, *, order_id: str) -> Any:  # noqa: ANN401
        """
        Get Transfer History.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-transfer-history
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_v3_broker_nd_transfer_detail", self._native_params(orderId=order_id)
        )

    async def get_v1_asset_ndbroker_deposit_list(
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
        return await self._native_private(
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

    async def get_v3_broker_nd_deposit_detail(self, *, currency: str, hash: str) -> Any:  # noqa: ANN401
        """
        Get Deposit Detail.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-deposit-detail
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_v3_broker_nd_deposit_detail", self._native_params(currency=currency, hash=hash)
        )

    async def get_v3_broker_nd_withdraw_detail(self, *, withdrawal_id: str) -> Any:  # noqa: ANN401
        """
        Get Withdraw Detail.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/get-withdraw-detail
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_v3_broker_nd_withdraw_detail", self._native_params(withdrawalId=withdrawal_id)
        )

    async def post_v1_broker_nd_mark_up(
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
        return await self._native_private(
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

    async def get_v1_broker_nd_mark_up(self, *, sub_uids: int | None = None) -> Any:  # noqa: ANN401
        """
        Get Markup Fee.

        Source: https://www.kucoin.com/docs-new/rest/broker/exchange-broker/getmarkup
        Uses the Broker host and the configured ND management API key.
        """
        return await self._native_private(
            "get_v1_broker_nd_mark_up", self._native_params(subUids=sub_uids)
        )
