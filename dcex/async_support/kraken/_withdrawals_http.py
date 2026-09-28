"""Fund movement and batch endpoint mixins."""

from json import dumps
from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from AccountHTTP."""

    async def withdraw_futures_to_spot_wallet(
        self,
        amount: str,
        currency: str,
        sourceWallet: str | None = None,
    ) -> dict[str, Any]:
        """Withdraw funds from Kraken Futures to the Spot wallet."""
        return await self._native_private(
            "withdraw_futures_to_spot_wallet",
            self._native_params(
                amount=amount,
                currency=currency,
                sourceWallet=sourceWallet,
            ),
        )


class TradeHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from TradeHTTP."""

    async def get_withdrawal_addresses(
        self,
        *,
        asset: str | None = None,
        aclass: str | None = None,
        method: str | None = None,
        key: str | None = None,
        verified: bool | None = None,
    ) -> dict[str, Any]:
        """
        Read-only POST /0/private/WithdrawAddresses.

        Source: https://docs.kraken.com/api-reference/funding/get-withdrawal-addresses.md
        """
        return await self._native_private(
            "get_withdrawal_addresses",
            self._native_params(
                asset=asset, aclass=aclass, method=method, key=key, verified=verified
            ),
        )

    async def get_withdrawal_information(
        self, *, asset: str, key: str, amount: str
    ) -> dict[str, Any]:
        """
        Read-only POST /0/private/WithdrawInfo.

        Source: https://docs.kraken.com/api-reference/funding/get-withdrawal-information.md
        """
        return await self._native_private(
            "get_withdrawal_information", self._native_params(asset=asset, key=key, amount=amount)
        )

    async def get_withdrawal_methods(
        self,
        *,
        asset: str | None = None,
        aclass: str | None = None,
        network: str | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """
        Read-only POST /0/private/WithdrawMethods.

        Source: https://docs.kraken.com/api-reference/funding/get-withdrawal-methods.md
        """
        return await self._native_private(
            "get_withdrawal_methods",
            self._native_params(
                asset=asset, aclass=aclass, network=network, rebase_multiplier=rebase_multiplier
            ),
        )

    async def get_withdrawal_status(
        self,
        *,
        asset: str | None = None,
        aclass: str | None = None,
        method: str | None = None,
        start: str | None = None,
        end: str | None = None,
        cursor: str | bool | None = None,
        limit: int | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """
        Read-only POST /0/private/WithdrawStatus.

        Source: https://docs.kraken.com/api-reference/funding/get-status-of-recent-withdrawals.md
        """
        return await self._native_private(
            "get_withdrawal_status",
            self._native_params(
                asset=asset,
                aclass=aclass,
                method=method,
                start=start,
                end=end,
                cursor=cursor,
                limit=limit,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    async def create_funding_withdrawal(
        self, *, body: dict[str, Any], account_id: str | None = None, otp: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /funding/v1/withdrawals.

        API withdrawals have no second confirmation; they execute on submit. Uses the documented
        API-Nonce header and signs the complete path including its query.
        Source: https://docs.kraken.com/api-reference/funding-beta/create-funding-withdrawal
        """
        return await self._native_private(
            "create_funding_withdrawal",
            self._native_params(
                account_id=account_id,
                body=dumps(body, separators=(",", ":"), allow_nan=False),
                otp=otp,
            ),
        )

    async def get_funding_withdrawal_limits(
        self,
        *,
        asset_class: str,
        asset: str,
        preferred_asset: dict[str, Any] | None = None,
        account_id: str | None = None,
        otp: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /funding/v1/limits/withdrawal/{asset_class}/{asset}.

        Requires the corresponding account permission. Uses the documented API-Nonce header and
        signs the complete path including its query.
        Source: https://docs.kraken.com/api-reference/funding-beta/list-funding-withdrawal-limits
        """
        return await self._native_private(
            "get_funding_withdrawal_limits",
            self._native_params(
                asset_class=asset_class,
                asset=asset,
                preferred_asset=dumps(preferred_asset, separators=(",", ":"), allow_nan=False)
                if preferred_asset is not None
                else None,
                account_id=account_id,
                otp=otp,
            ),
        )

    async def get_funding_withdrawals(
        self,
        *,
        asset: dict[str, Any] | None = None,
        scope: dict[str, Any] | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        rebase_multiplier: str | None = None,
        account_id: str | None = None,
        otp: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /funding/v1/withdrawals.

        Requires the corresponding account permission. Uses the documented API-Nonce header and
        signs the complete path including its query.
        Source: https://docs.kraken.com/api-reference/funding-beta/list-funding-withdrawals
        """
        return await self._native_private(
            "get_funding_withdrawals",
            self._native_params(
                asset=dumps(asset, separators=(",", ":"), allow_nan=False)
                if asset is not None
                else None,
                scope=dumps(scope, separators=(",", ":"), allow_nan=False)
                if scope is not None
                else None,
                status=status,
                cursor=cursor,
                limit=limit,
                start_time=start_time,
                end_time=end_time,
                rebase_multiplier=rebase_multiplier,
                account_id=account_id,
                otp=otp,
            ),
        )

    async def cancel_spot_withdrawal(self, *, asset: str, refid: str) -> Any:  # noqa: ANN401
        """
        POST /0/private/WithdrawCancel.

        Requires the corresponding account permission.
        Source: https://docs.kraken.com/api-reference/funding/request-withdrawal-cancellation
        """
        return await self._native_private(
            "cancel_spot_withdrawal", self._native_params(asset=asset, refid=refid)
        )

    async def create_spot_withdrawal(
        self,
        *,
        asset: str,
        key: str,
        amount: str,
        aclass: str | None = None,
        address: str | None = None,
        max_fee: str | None = None,
        rebase_multiplier: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /0/private/Withdraw.

        API withdrawals have no second confirmation; they execute on submit.
        Source: https://docs.kraken.com/api-reference/funding/withdraw-funds
        """
        return await self._native_private(
            "create_spot_withdrawal",
            self._native_params(
                asset=asset,
                aclass=aclass,
                key=key,
                address=address,
                amount=amount,
                max_fee=max_fee,
                rebase_multiplier=rebase_multiplier,
            ),
        )
