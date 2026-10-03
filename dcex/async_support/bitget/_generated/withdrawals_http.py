"""Generated bitget withdrawals HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedWithdrawalsHTTP(MarketHTTP):
    """Withdrawals API methods."""

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
