"""
Bybit Asset HTTP client.

This module provides HTTP client functionality for asset-related operations
on the Bybit exchange, including deposits, withdrawals, transfers,
and coin information queries.
"""

import time
import uuid
from typing import Any

from ._http_manager import HTTPManager
from .endpoints.asset import Asset


class AssetHTTP(HTTPManager):
    """
    HTTP client for Bybit asset operations.

    This class handles all asset-related API requests including:
    - Coin information queries
    - Deposit and withdrawal operations
    - Internal and universal transfers
    - Sub-account management
    - Asset balance queries
    """

    def get_coin_info(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Get coin information.

        Args:
            coin: Currency symbol to get information for

        Returns:
            dict[str, Any]: API response containing coin information
        """
        payload = {}
        if coin is not None:
            payload["coin"] = coin

        res = self._request(
            method="GET",
            path=Asset.GET_COIN_INFO,
            query=payload,
        )
        return res

    def get_sub_uid(self) -> dict[str, Any]:
        """
        Get sub-account UID list.

        Returns:
            dict[str, Any]: API response containing sub-account UIDs
        """
        res = self._request(
            method="GET",
            path=Asset.GET_SUB_UID,
            query={},
        )
        return res

    def get_spot_asset_info(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot asset information.

        Retrieves spot account asset information. Default account type is SPOT.

        Args:
            coin: Currency symbol to get asset info for

        Returns:
            dict[str, Any]: API response containing spot asset information
        """
        payload = {
            "accountType": "SPOT",
        }
        if coin is not None:
            payload["coin"] = coin

        res = self._request(
            method="GET",
            path=Asset.GET_SPOT_ASSET_INFO,
            query=payload,
        )
        return res

    def get_coins_balance(
        self,
        accountType: str,
        coin: str | None = None,
        memberId: str | None = None,
    ) -> dict[str, Any]:
        """
        Get coins balance for account.

        Args:
            accountType: Account type (e.g., SPOT, UNIFIED)
            coin: Currency symbol to get balance for
            memberId: Member ID for sub-account queries

        Returns:
            dict[str, Any]: API response containing coins balance
        """
        payload = {
            "accountType": accountType,
        }
        if coin is not None:
            payload["coin"] = coin
        if memberId is not None:
            payload["memberId"] = memberId

        res = self._request(
            method="GET",
            path=Asset.GET_ALL_COINS_BALANCE,
            query=payload,
        )
        return res

    def get_coin_balance(
        self,
        accountType: str,
        coin: str,
        memberId: str | None = None,
        toAccountType: str | None = None,
    ) -> dict[str, Any]:
        """
        Get single coin balance.

        Args:
            accountType: Source account type
            coin: Currency symbol
            memberId: Member ID for sub-account queries
            toAccountType: Target account type for transfer queries

        Returns:
            dict[str, Any]: API response containing coin balance
        """
        payload = {
            "accountType": accountType,
            "coin": coin,
        }
        if memberId is not None:
            payload["memberId"] = memberId
        if toAccountType is not None:
            payload["toAccountType"] = toAccountType

        res = self._request(
            method="GET",
            path=Asset.GET_SINGLE_COIN_BALANCE,
            query=payload,
        )
        return res

    def get_withdrawable_amount(
        self,
        coin: str,
    ) -> dict[str, Any]:
        """
        Get withdrawable amount for a coin.

        Args:
            coin: Currency symbol

        Returns:
            dict[str, Any]: API response containing withdrawable amount
        """
        payload = {
            "coin": coin,
        }

        res = self._request(
            method="GET",
            path=Asset.GET_WITHDRAWABLE_AMOUNT,
            query=payload,
        )
        return res

    def get_internal_transfer_records(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get internal transfer records.

        Args:
            coin: Currency symbol to filter by
            startTime: Start timestamp in milliseconds
            limit: Maximum number of records to return (default: 20)

        Returns:
            dict[str, Any]: API response containing transfer records
        """
        payload: dict[str, Any] = {
            "limit": limit,
        }
        if coin is not None:
            payload["coin"] = coin
        if startTime is not None:
            payload["startTime"] = startTime

        res = self._request(
            method="GET",
            path=Asset.GET_INTERNAL_TRANSFER_RECORDS,
            query=payload,
        )
        return res

    def get_transferable_coin(
        self,
        fromAccountType: str,
        toAccountType: str,
    ) -> dict[str, Any]:
        """
        Get transferable coins between account types.

        Args:
            fromAccountType: Source account type
            toAccountType: Target account type

        Returns:
            dict[str, Any]: API response containing transferable coins
        """
        payload = {
            "fromAccountType": fromAccountType,
            "toAccountType": toAccountType,
        }

        res = self._request(
            method="GET",
            path=Asset.GET_TRANSFERABLE_COIN,
            query=payload,
        )
        return res

    def create_internal_transfer(
        self,
        coin: str,
        amount: str,
        fromAccountType: str,
        toAccountType: str,
    ) -> dict[str, Any]:
        """
        Create internal transfer between account types.

        Args:
            coin: Currency symbol to transfer
            amount: Amount to transfer
            fromAccountType: Source account type
            toAccountType: Target account type

        Returns:
            dict[str, Any]: API response confirming the transfer
        """
        transfer_id = str(uuid.uuid4())
        payload = {
            "transferId": transfer_id,
            "coin": coin,
            "amount": amount,
            "fromAccountType": fromAccountType,
            "toAccountType": toAccountType,
        }

        res = self._request(
            method="POST",
            path=Asset.CREATE_INTERNAL_TRANSFER,
            query=payload,
        )
        return res

    def create_universal_transfer(
        self,
        coin: str,
        amount: str,
        fromMemberId: str,
        toMemberId: str,
        fromAccountType: str,
        toAccountType: str,
    ) -> dict[str, Any]:
        """
        Create universal transfer between members.

        Args:
            coin: Currency symbol to transfer
            amount: Amount to transfer
            fromMemberId: Source member ID
            toMemberId: Target member ID
            fromAccountType: Source account type
            toAccountType: Target account type

        Returns:
            dict[str, Any]: API response confirming the transfer
        """
        transfer_id = str(uuid.uuid4())
        payload = {
            "transferId": transfer_id,
            "coin": coin,
            "amount": amount,
            "fromMemberId": fromMemberId,
            "toMemberId": toMemberId,
            "fromAccountType": fromAccountType,
            "toAccountType": toAccountType,
        }

        res = self._request(
            method="POST",
            path=Asset.CREATE_UNIVERSAL_TRANSFER,
            query=payload,
        )
        return res

    def get_universal_transfer_records(
        self,
        coin: str | None = None,
        status: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get universal transfer records.

        Args:
            coin: Currency symbol to filter by
            status: Transfer status to filter by
            startTime: Start timestamp in milliseconds
            limit: Maximum number of records to return (default: 20)

        Returns:
            dict[str, Any]: API response containing transfer records
        """
        payload: dict[str, Any] = {
            "limit": limit,
        }
        if coin is not None:
            payload["coin"] = coin
        if status is not None:
            payload["status"] = status
        if startTime is not None:
            payload["startTime"] = startTime

        res = self._request(
            method="GET",
            path=Asset.GET_UNIVERSAL_TRANSFER_RECORDS,
            query=payload,
        )
        return res

    def set_deposit_account(
        self,
        accountType: str,
    ) -> dict[str, Any]:
        """
        Set deposit account type.

        Args:
            accountType: Account type to set for deposits

        Returns:
            dict[str, Any]: API response confirming the setting
        """
        payload = {
            "accountType": accountType,
        }

        res = self._request(
            method="POST",
            path=Asset.SET_DEPOSIT_ACCOUNT,
            query=payload,
        )
        return res

    def get_deposit_records(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get deposit records.

        Args:
            coin: Currency symbol to filter by
            startTime: Start timestamp in milliseconds
            limit: Maximum number of records to return (default: 20)

        Returns:
            dict[str, Any]: API response containing deposit records
        """
        payload: dict[str, Any] = {
            "limit": limit,
        }
        if coin is not None:
            payload["coin"] = coin
        if startTime is not None:
            payload["startTime"] = startTime

        res = self._request(
            method="GET",
            path=Asset.GET_DEPOSIT_RECORDS,
            query=payload,
        )
        return res

    def get_sub_deposit_records(
        self,
        subMemberId: str,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get sub-account deposit records.

        Args:
            subMemberId: Sub-member ID
            coin: Currency symbol to filter by
            startTime: Start timestamp in milliseconds
            limit: Maximum number of records to return (default: 20)

        Returns:
            dict[str, Any]: API response containing deposit records
        """
        payload: dict[str, Any] = {
            "subMemberId": subMemberId,
            "limit": limit,
        }
        if coin is not None:
            payload["coin"] = coin
        if startTime is not None:
            payload["startTime"] = startTime

        res = self._request(
            method="GET",
            path=Asset.GET_SUB_ACCOUNT_DEPOSIT_RECORDS,
            query=payload,
        )
        return res

    def get_internal_deposit_records(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get internal deposit records.

        Args:
            coin: Currency symbol to filter by
            startTime: Start timestamp in milliseconds
            limit: Maximum number of records to return (default: 20)

        Returns:
            dict[str, Any]: API response containing deposit records
        """
        payload: dict[str, Any] = {
            "limit": limit,
        }
        if coin is not None:
            payload["coin"] = coin
        if startTime is not None:
            payload["startTime"] = startTime

        res = self._request(
            method="GET",
            path=Asset.GET_INTERNAL_DEPOSIT_RECORDS,
            query=payload,
        )
        return res

    def get_master_deposit_address(
        self,
        coin: str,
    ) -> dict[str, Any]:
        """
        Get master deposit address for a coin.

        Args:
            coin: Currency symbol

        Returns:
            dict[str, Any]: API response containing deposit address
        """
        payload = {
            "coin": coin,
        }

        res = self._request(
            method="GET",
            path=Asset.GET_MASTER_DEPOSIT_ADDRESS,
            query=payload,
        )
        return res

    def get_withdrawal_records(
        self,
        coin: str | None = None,
        withdrawType: int | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get withdrawal records.

        Args:
            coin: Currency symbol to filter by
            withdrawType: Withdrawal type to filter by
            startTime: Start timestamp in milliseconds
            limit: Maximum number of records to return (default: 20)

        Returns:
            dict[str, Any]: API response containing withdrawal records
        """
        payload: dict[str, Any] = {
            "limit": limit,
        }
        if coin is not None:
            payload["coin"] = coin
        if withdrawType is not None:
            payload["withdrawType"] = withdrawType
        if startTime is not None:
            payload["startTime"] = startTime

        res = self._request(
            method="GET",
            path=Asset.GET_WITHDRAWAL_RECORDS,
            query=payload,
        )
        return res

    def withdraw(
        self,
        coin: str,
        chain: str,
        address: str,
        amount: str,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """
        Create withdrawal request.

        Args:
            coin: Currency symbol to withdraw
            chain: Blockchain network
            address: Withdrawal address
            amount: Amount to withdraw
            tag: Memo/tag for withdrawal (if required)

        Returns:
            dict[str, Any]: API response confirming the withdrawal
        """
        payload = {
            "coin": coin,
            "chain": chain,
            "address": address,
            "amount": amount,
            "timestamp": int(time.time() * 1000),
            "accountType": "FUND",
            "feeType": 1,
        }
        if chain is not None:
            payload["chain"] = chain
        if tag is not None:
            payload["tag"] = tag

        res = self._request(
            method="POST",
            path=Asset.WITHDRAW,
            query=payload,
        )
        return res

    def cancel_withdrawal(
        self,
        id: str,
    ) -> dict[str, Any]:
        """
        Cancel withdrawal request.

        Args:
            id: Withdrawal ID to cancel

        Returns:
            dict[str, Any]: API response confirming the cancellation
        """
        payload = {
            "id": id,
        }

        res = self._request(
            method="POST",
            path=Asset.CANCEL_WITHDRAWAL,
            query=payload,
        )
        return res
