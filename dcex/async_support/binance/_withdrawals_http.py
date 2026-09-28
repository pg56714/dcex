"""Fund movement and batch endpoint mixins."""

from json import dumps
from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from TradeHTTP."""

    _native_private: Any

    _params: Any

    async def fetch_withdraw_address_list(self) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/capital/withdraw/address/list.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#fetch-withdraw-address-list
        """
        return await self._native_private("fetch_withdraw_address_list", self._params())

    async def fetch_withdraw_quota(self) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/capital/withdraw/quota.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#fetch-withdraw-quota
        """
        return await self._native_private("fetch_withdraw_quota", self._params())

    async def get_withdrawal_history(
        self,
        *,
        coin: str | None = None,
        withdraw_order_id: str | None = None,
        status: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        id_list: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/capital/withdraw/history.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#withdraw-history
        """
        return await self._native_private(
            "get_withdrawal_history",
            self._params(
                coin=coin,
                withdrawOrderId=withdraw_order_id,
                status=status,
                offset=offset,
                limit=limit,
                idList=id_list,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    async def get_travel_rule_withdrawal_history(
        self,
        *,
        tr_id: str | None = None,
        tx_id: str | None = None,
        withdraw_order_id: str | None = None,
        network: str | None = None,
        coin: str | None = None,
        travel_rule_status: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/localentity/withdraw/history.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#withdraw-history-v1
        """
        return await self._native_private(
            "get_travel_rule_withdrawal_history",
            self._params(
                trId=tr_id,
                txId=tx_id,
                withdrawOrderId=withdraw_order_id,
                network=network,
                coin=coin,
                travelRuleStatus=travel_rule_status,
                offset=offset,
                limit=limit,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    async def get_travel_rule_withdrawal_history_v2(
        self,
        *,
        tr_id: str | None = None,
        tx_id: str | None = None,
        withdraw_order_id: str | None = None,
        network: str | None = None,
        coin: str | None = None,
        travel_rule_status: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v2/localentity/withdraw/history.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#withdraw-history-v2
        """
        return await self._native_private(
            "get_travel_rule_withdrawal_history_v2",
            self._params(
                trId=tr_id,
                txId=tx_id,
                withdrawOrderId=withdraw_order_id,
                network=network,
                coin=coin,
                travelRuleStatus=travel_rule_status,
                offset=offset,
                limit=limit,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    async def withdraw_managed_sub_account(
        self,
        *,
        from_email: str,
        asset: str,
        amount: str,
        transfer_date: int | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """
        POST /sapi/v1/managed-subaccount/withdraw.

        API withdrawals have no second confirmation; they execute on submit.
        transfer_date schedules execution at the specified UTC date.

        https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#withdrawl-assets-from-the-managed-sub-account
        """
        return await self._native_private(
            "withdraw_managed_sub_account",
            self._params(
                fromEmail=from_email,
                asset=asset,
                amount=amount,
                transferDate=transfer_date,
                recvWindow=recv_window,
            ),
        )

    async def disable_fast_withdraw_switch(
        self,
        *,
        recv_window: int | None = None,
    ) -> dict:
        """
        POST /sapi/v1/account/disableFastWithdrawSwitch.

        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#disable-fast-withdraw-switch
        """
        return await self._native_private(
            "disable_fast_withdraw_switch",
            self._params(
                recvWindow=recv_window,
            ),
        )

    async def enable_fast_withdraw_switch(
        self,
        *,
        recv_window: int | None = None,
    ) -> dict:
        """
        POST /sapi/v1/account/enableFastWithdrawSwitch.

        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#enable-fast-withdraw-switch
        """
        return await self._native_private(
            "enable_fast_withdraw_switch",
            self._params(
                recvWindow=recv_window,
            ),
        )

    async def create_withdrawal(
        self,
        *,
        coin: str,
        address: str,
        amount: str,
        withdraw_order_id: str | None = None,
        network: str | None = None,
        address_tag: str | None = None,
        transaction_fee_flag: bool | None = None,
        name: str | None = None,
        wallet_type: int | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """
        POST /sapi/v1/capital/withdraw/apply.

        API withdrawals have no second confirmation; they execute on submit.

        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#withdraw
        """
        return await self._native_private(
            "create_withdrawal",
            self._params(
                coin=coin,
                address=address,
                amount=amount,
                withdrawOrderId=withdraw_order_id,
                network=network,
                addressTag=address_tag,
                transactionFeeFlag=transaction_fee_flag,
                name=name,
                walletType=wallet_type,
                recvWindow=recv_window,
            ),
        )

    async def create_broker_withdrawal(
        self,
        *,
        address: str,
        coin: str,
        amount: str,
        withdraw_order_id: str,
        questionnaire: dict[str, Any],
        originator_pii: dict[str, Any],
        address_tag: str | None = None,
        network: str | None = None,
        address_name: str | None = None,
        transaction_fee_flag: bool | None = None,
        wallet_type: int | None = None,
    ) -> dict:
        """
        POST /sapi/v1/localentity/broker/withdraw/apply.

        API withdrawals have no second confirmation; they execute on submit.
        Pass JSON objects; URL encoding is applied exactly once by the transport.

        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#broker-withdraw
        """
        return await self._native_private(
            "create_broker_withdrawal",
            self._params(
                address=address,
                coin=coin,
                amount=amount,
                withdrawOrderId=withdraw_order_id,
                questionnaire=dumps(questionnaire, separators=(",", ":"), allow_nan=False),
                originatorPii=dumps(originator_pii, separators=(",", ":"), allow_nan=False),
                addressTag=address_tag,
                network=network,
                addressName=address_name,
                transactionFeeFlag=transaction_fee_flag,
                walletType=wallet_type,
            ),
        )

    async def create_travel_rule_withdrawal(
        self,
        *,
        coin: str,
        address: str,
        amount: str,
        questionnaire: dict[str, Any],
        withdraw_order_id: str | None = None,
        network: str | None = None,
        address_tag: str | None = None,
        transaction_fee_flag: bool | None = None,
        name: str | None = None,
        wallet_type: int | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """
        POST /sapi/v1/localentity/withdraw/apply.

        API withdrawals have no second confirmation; they execute on submit.
        Pass JSON objects; URL encoding is applied exactly once by the transport.

        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#withdraw-travel-rule
        """
        return await self._native_private(
            "create_travel_rule_withdrawal",
            self._params(
                coin=coin,
                address=address,
                amount=amount,
                questionnaire=dumps(questionnaire, separators=(",", ":"), allow_nan=False),
                withdrawOrderId=withdraw_order_id,
                network=network,
                addressTag=address_tag,
                transactionFeeFlag=transaction_fee_flag,
                name=name,
                walletType=wallet_type,
                recvWindow=recv_window,
            ),
        )
