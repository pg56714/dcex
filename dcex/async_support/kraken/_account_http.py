"""Kraken private account async HTTP client."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """Async HTTP client for Kraken private account operations."""

    async def get_spot_account_balance(
        self,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot account balances."""
        return await self._native_private(
            "get_spot_account_balance",
            self._native_params(rebase_multiplier=rebase_multiplier),
        )

    async def get_spot_trade_balance(
        self,
        asset: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot trade balance."""
        return await self._native_private(
            "get_spot_trade_balance",
            self._native_params(asset=asset),
        )

    async def get_spot_open_positions(
        self,
        txid: str | None = None,
        docalcs: bool | None = None,
        consolidation: str | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot margin open positions."""
        return await self._native_private(
            "get_spot_open_positions",
            self._native_params(
                txid=txid,
                docalcs=docalcs,
                consolidation=consolidation,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    async def get_spot_ledgers(
        self,
        asset: str | None = None,
        aclass: str | None = None,
        type_: str | None = None,
        start: int | str | None = None,
        end: int | str | None = None,
        ofs: int | None = None,
        without_count: bool | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot ledger entries."""
        return await self._native_private(
            "get_spot_ledgers",
            self._native_params(
                asset=asset,
                aclass=aclass,
                type_=type_,
                start=start,
                end=end,
                ofs=ofs,
                without_count=without_count,
            ),
        )

    async def get_spot_trade_volume(
        self,
        pair: str | None = None,
        fee_info: bool | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot trade volume and optional fee info."""
        return await self._native_private(
            "get_spot_trade_volume",
            self._native_params(pair=pair, fee_info=fee_info),
        )

    async def wallet_transfer_to_futures(
        self,
        asset: str,
        amount: str,
        from_: str = "Spot Wallet",
        to: str = "Futures Wallet",
    ) -> dict[str, Any]:
        """Transfer funds from Kraken spot wallet to Futures wallet."""
        return await self._native_private(
            "wallet_transfer_to_futures",
            self._native_params(asset=asset, amount=amount, from_=from_, to=to),
        )

    async def get_futures_accounts(self) -> dict[str, Any]:
        """Retrieve Kraken Futures wallets/accounts."""
        return await self._native_private("get_futures_accounts", [])

    async def get_futures_open_positions(self) -> dict[str, Any]:
        """Retrieve Kraken Futures open positions."""
        return await self._native_private("get_futures_open_positions", [])

    async def get_futures_fills(
        self,
        lastFillTime: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures account fills."""
        return await self._native_private(
            "get_futures_fills",
            self._native_params(lastFillTime=lastFillTime),
        )

    async def futures_wallet_transfer(
        self,
        amount: str,
        fromAccount: str,
        toAccount: str,
        unit: str,
    ) -> dict[str, Any]:
        """Transfer funds between Kraken Futures cash and margin accounts."""
        return await self._native_private(
            "futures_wallet_transfer",
            self._native_params(
                amount=amount,
                fromAccount=fromAccount,
                toAccount=toAccount,
                unit=unit,
            ),
        )

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
