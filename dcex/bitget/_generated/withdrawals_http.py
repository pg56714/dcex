"""Generated bitget withdrawals HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedWithdrawalsHTTP(MarketHTTP):
    """Withdrawals API methods."""

    def broker_get_all_subaccount_deposit_withdrawal(
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
        return self._native_private(
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

    def broker_subaccount_withdrawal(
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
        return self._native_private(
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

    def classic_broker_subaccount_subaccount_withdraw(
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
        return self._native_private(
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

    def classic_broker_subaccount_subaccount_withdrawal_records(
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
        return self._native_private(
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

    def classic_broker_subaccount_get_subaccount_all_deposit_withdrawal_records(
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
        return self._native_private(
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
