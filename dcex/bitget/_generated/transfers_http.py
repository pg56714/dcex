"""Generated bitget transfers HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedTransfersHTTP(MarketHTTP):
    """Transfers API methods."""

    def cfd_account_transfer(
        self, *, coin: str, amount: str, account_type: str, direction: str
    ) -> dict[str, Any]:
        """
        Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/cfd-account/cfd-account#cfd-transfer
        """
        return self._native_private(
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

    def cfd_account_get_transfer_records(
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
        return self._native_private(
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

    def classic_broker_subaccount_subaccount_deposit_auto_transfer(
        self, *, sub_uid: str, coin: str, to_account_type: str
    ) -> dict[str, Any]:
        """
        Sub Deposit Auto Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-broker-subaccount/classic-broker-subaccount#sub-deposit-auto-transfer
        """
        return self._native_private(
            "classic_broker_subaccount_subaccount_deposit_auto_transfer",
            self._native_params(
                **{"subUid": sub_uid, "coin": coin, "toAccountType": to_account_type}
            ),
        )

    def classic_instloan_account_get_transferred_amount_from_spot_account(
        self, *, coin: str, user_id: str | None = None
    ) -> dict[str, Any]:
        """
        Get transferable amount.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-account/classic-instloan-account#get-transferable-amount
        """
        return self._native_private(
            "classic_instloan_account_get_transferred_amount_from_spot_account",
            self._native_params(**{"coin": coin, "userId": user_id}),
        )

    def copy_trading_follower_copy_transfer(
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
        return self._native_private(
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

    def copy_trading_follower_get_copy_transfer_record(
        self, *, project_id: str, limit: str | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        Get Copy Transfer Record.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-copy-transfer-record
        """
        return self._native_private(
            "copy_trading_follower_get_copy_transfer_record",
            self._native_params(**{"projectId": project_id, "limit": limit, "cursor": cursor}),
        )

    def copy_trading_public_private_get_max_transferable(self, *, coin: str) -> dict[str, Any]:
        """
        Get Max Transferable.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-max-transferable
        """
        return self._native_private(
            "copy_trading_public_private_get_max_transferable",
            self._native_params(**{"coin": coin}),
        )

    def copy_trading_public_private_transfer(
        self, *, type_: str, coin: str, amount: str, in_account_type: str | None = None
    ) -> dict[str, Any]:
        """
        Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#transfer
        """
        return self._native_private(
            "copy_trading_public_private_transfer",
            self._native_params(
                **{"type": type_, "coin": coin, "amount": amount, "inAccountType": in_account_type}
            ),
        )

    def copy_trading_public_private_get_transfer_record(
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
        return self._native_private(
            "copy_trading_public_private_get_transfer_record",
            self._native_params(
                **{"startTime": start_time, "endTime": end_time, "limit": limit, "cursor": cursor}
            ),
        )

    def institutional_loan_get_transferred_quantity(
        self, *, coin: str, user_id: str | None = None
    ) -> dict[str, Any]:
        """
        Get Transferred Quantity.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-transferred-quantity
        """
        return self._native_private(
            "institutional_loan_get_transferred_quantity",
            self._native_params(**{"coin": coin, "userId": user_id}),
        )

    def stock_plus_assets_transfer(
        self, *, coin: str | None = None, amount: str | None = None, direction: str | None = None
    ) -> dict[str, Any]:
        """
        Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/stock-plus/assets#transfer
        """
        return self._native_private(
            "stock_plus_assets_transfer",
            self._native_params(**{"coin": coin, "amount": amount, "direction": direction}),
        )

    def stock_plus_assets_get_transfer_records(
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
        return self._native_private(
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
