"""
Bybit asset management HTTP client module.

This module provides the AssetHTTP class for interacting with Bybit's
asset management API endpoints, including coin information, balances,
transfers, deposits, and withdrawals.
"""

import time
import uuid
from typing import Any

from ._http_manager import HTTPManager
from .endpoints.asset import Asset


class AssetHTTP(HTTPManager):
    """
    Bybit asset management HTTP client.

    This class provides methods for interacting with Bybit's asset management
    API endpoints, including:
    - Coin information and balances
    - Internal and universal transfers
    - Deposit and withdrawal operations
    - Sub-account management

    Inherits from HTTPManager for HTTP request handling and authentication.
    """

    async def get_coin_info(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Get coin information from Bybit.

        Args:
            coin: Optional coin symbol to filter results

        Returns:
            Dict containing coin information
        """
        payload = {}
        if coin is not None:
            payload["coin"] = coin

        res = await self._request(
            method="GET",
            path=Asset.GET_COIN_INFO,
            query=payload,
        )
        return res

    async def get_sub_uid(self) -> dict[str, Any]:
        """
        Get sub-account UID list.

        Returns:
            Dict containing sub-account UID information
        """
        res = await self._request(
            method="GET",
            path=Asset.GET_SUB_UID,
            query=None,
        )
        return res

    async def get_spot_asset_info(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot asset information.

        Args:
            coin: Optional coin symbol to filter results

        Returns:
            Dict containing spot asset information
        """
        payload = {
            "accountType": "SPOT",
        }
        if coin is not None:
            payload["coin"] = coin

        res = await self._request(
            method="GET",
            path=Asset.GET_SPOT_ASSET_INFO,
            query=payload,
        )
        return res

    async def get_coins_balance(
        self,
        accountType: str,
        coin: str | None = None,
        memberId: str | None = None,
    ) -> dict[str, Any]:
        """
        Get coins balance for specified account type.

        Args:
            accountType: Account type (e.g., "SPOT", "FUND")
            coin: Optional coin symbol to filter results
            memberId: Optional member ID for sub-account

        Returns:
            Dict containing coins balance information
        """
        payload = {
            "accountType": accountType,
        }
        if coin is not None:
            payload["coin"] = coin
        if memberId is not None:
            payload["memberId"] = memberId

        res = await self._request(
            method="GET",
            path=Asset.GET_ALL_COINS_BALANCE,
            query=payload,
        )
        return res

    async def get_coin_balance(
        self,
        accountType: str,
        coin: str,
        memberId: str | None = None,
        toAccountType: str | None = None,
    ) -> dict[str, Any]:
        """
        Get single coin balance for specified account type.

        Args:
            accountType: Account type (e.g., "SPOT", "FUND")
            coin: Coin symbol
            memberId: Optional member ID for sub-account
            toAccountType: Optional target account type

        Returns:
            Dict containing coin balance information
        """
        payload = {
            "accountType": accountType,
            "coin": coin,
        }
        if memberId is not None:
            payload["memberId"] = memberId
        if toAccountType is not None:
            payload["toAccountType"] = toAccountType

        res = await self._request(
            method="GET",
            path=Asset.GET_SINGLE_COIN_BALANCE,
            query=payload,
        )
        return res

    async def get_withdrawable_amount(
        self,
        coin: str,
    ) -> dict[str, Any]:
        """
        Get withdrawable amount for a specific coin.

        Args:
            coin: Coin symbol

        Returns:
            Dict containing withdrawable amount information
        """
        payload = {
            "coin": coin,
        }

        res = await self._request(
            method="GET",
            path=Asset.GET_WITHDRAWABLE_AMOUNT,
            query=payload,
        )
        return res

    async def get_internal_transfer_records(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get internal transfer records.

        Args:
            coin: Optional coin symbol to filter results
            startTime: Optional start time timestamp
            limit: Maximum number of records to return (default: 20)

        Returns:
            Dict containing internal transfer records
        """
        payload: dict[str, Any] = {
            "limit": limit,
        }
        if coin is not None:
            payload["coin"] = coin
        if startTime is not None:
            payload["startTime"] = startTime

        res = await self._request(
            method="GET",
            path=Asset.GET_INTERNAL_TRANSFER_RECORDS,
            query=payload,
        )
        return res

    async def get_transferable_coin(
        self,
        fromAccountType: str,
        toAccountType: str,
    ) -> dict[str, Any]:
        """
        Get list of transferable coins between account types.

        Args:
            fromAccountType: Source account type
            toAccountType: Target account type

        Returns:
            Dict containing transferable coins information
        """
        payload = {
            "fromAccountType": fromAccountType,
            "toAccountType": toAccountType,
        }

        res = await self._request(
            method="GET",
            path=Asset.GET_TRANSFERABLE_COIN,
            query=payload,
        )
        return res

    async def create_internal_transfer(
        self,
        coin: str,
        amount: str,
        fromAccountType: str,
        toAccountType: str,
    ) -> dict[str, Any]:
        """
        Create internal transfer between account types.

        Args:
            coin: Coin symbol to transfer
            amount: Amount to transfer
            fromAccountType: Source account type
            toAccountType: Target account type

        Returns:
            Dict containing transfer result
        """
        transfer_id = str(uuid.uuid4())
        payload = {
            "transferId": transfer_id,
            "coin": coin,
            "amount": amount,
            "fromAccountType": fromAccountType,
            "toAccountType": toAccountType,
        }

        res = await self._request(
            method="POST",
            path=Asset.CREATE_INTERNAL_TRANSFER,
            query=payload,
        )
        return res

    async def create_universal_transfer(
        self,
        coin: str,
        amount: str,
        fromMemberId: int,
        toMemberId: int,
        fromAccountType: str,
        toAccountType: str,
    ) -> dict[str, Any]:
        """
        Create universal transfer between members.

        Args:
            coin: Coin symbol to transfer
            amount: Amount to transfer
            fromMemberId: Source member ID
            toMemberId: Target member ID
            fromAccountType: Source account type
            toAccountType: Target account type

        Returns:
            Dict containing transfer result
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

        res = await self._request(
            method="POST",
            path=Asset.CREATE_UNIVERSAL_TRANSFER,
            query=payload,
        )
        return res

    async def get_universal_transfer_records(
        self,
        coin: str | None = None,
        status: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get universal transfer records.

        Args:
            coin: Optional coin symbol to filter results
            status: Optional transfer status to filter results
            startTime: Optional start time timestamp
            limit: Maximum number of records to return (default: 20)

        Returns:
            Dict containing universal transfer records
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

        res = await self._request(
            method="GET",
            path=Asset.GET_UNIVERSAL_TRANSFER_RECORDS,
            query=payload,
        )
        return res

    async def set_deposit_account(
        self,
        accountType: str,
    ) -> dict[str, Any]:
        """
        Set deposit account type.

        Args:
            accountType: Account type to set for deposits

        Returns:
            Dict containing operation result
        """
        payload = {
            "accountType": accountType,
        }

        res = await self._request(
            method="POST",
            path=Asset.SET_DEPOSIT_ACCOUNT,
            query=payload,
        )
        return res

    async def get_deposit_records(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get deposit records.

        Args:
            coin: Optional coin symbol to filter results
            startTime: Optional start time timestamp
            limit: Maximum number of records to return (default: 20)

        Returns:
            Dict containing deposit records
        """
        payload: dict[str, Any] = {
            "limit": limit,
        }
        if coin is not None:
            payload["coin"] = coin
        if startTime is not None:
            payload["startTime"] = startTime

        res = await self._request(
            method="GET",
            path=Asset.GET_DEPOSIT_RECORDS,
            query=payload,
        )
        return res

    async def get_sub_deposit_records(
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
            coin: Optional coin symbol to filter results
            startTime: Optional start time timestamp
            limit: Maximum number of records to return (default: 20)

        Returns:
            Dict containing sub-account deposit records
        """
        payload: dict[str, Any] = {
            "subMemberId": subMemberId,
            "limit": limit,
        }
        if coin is not None:
            payload["coin"] = coin
        if startTime is not None:
            payload["startTime"] = startTime

        res = await self._request(
            method="GET",
            path=Asset.GET_SUB_ACCOUNT_DEPOSIT_RECORDS,
            query=payload,
        )
        return res

    async def get_internal_deposit_records(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get internal deposit records.

        Args:
            coin: Optional coin symbol to filter results
            startTime: Optional start time timestamp
            limit: Maximum number of records to return (default: 20)

        Returns:
            Dict containing internal deposit records
        """
        payload: dict[str, Any] = {
            "limit": limit,
        }
        if coin is not None:
            payload["coin"] = coin
        if startTime is not None:
            payload["startTime"] = startTime

        res = await self._request(
            method="GET",
            path=Asset.GET_INTERNAL_DEPOSIT_RECORDS,
            query=payload,
        )
        return res

    async def get_master_deposit_address(
        self,
        coin: str,
    ) -> dict[str, Any]:
        """
        Get master deposit address for a specific coin.

        Args:
            coin: Coin symbol

        Returns:
            Dict containing master deposit address information
        """
        payload = {
            "coin": coin,
        }

        res = await self._request(
            method="GET",
            path=Asset.GET_MASTER_DEPOSIT_ADDRESS,
            query=payload,
        )
        return res

    async def get_withdrawal_records(
        self,
        coin: str | None = None,
        withdrawType: int | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get withdrawal records.

        Args:
            coin: Optional coin symbol to filter results
            withdrawType: Optional withdrawal type
            startTime: Optional start time timestamp
            limit: Maximum number of records to return (default: 20)

        Returns:
            Dict containing withdrawal records
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

        res = await self._request(
            method="GET",
            path=Asset.GET_WITHDRAWAL_RECORDS,
            query=payload,
        )
        return res

    async def withdraw(
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
            coin: Coin symbol to withdraw
            chain: Blockchain network
            address: Withdrawal address
            amount: Amount to withdraw
            tag: Optional memo/tag for withdrawal

        Returns:
            Dict containing withdrawal result
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

        res = await self._request(
            method="POST",
            path=Asset.WITHDRAW,
            query=payload,
        )
        return res

    async def cancel_withdrawal(
        self,
        id: str,
    ) -> dict[str, Any]:
        """
        Cancel withdrawal request.

        Args:
            id: Withdrawal ID to cancel

        Returns:
            Dict containing cancellation result
        """
        payload = {
            "id": id,
        }

        res = await self._request(
            method="POST",
            path=Asset.CANCEL_WITHDRAWAL,
            query=payload,
        )
        return res
