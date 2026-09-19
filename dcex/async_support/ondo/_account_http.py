"""Asynchronous authenticated Ondo account methods."""

# ruff: noqa: ANN401

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    async def get_account(self) -> Any:
        return await self._native_private("get_account")

    async def get_balance(self) -> Any:
        return await self._native_private("get_balance")

    async def get_positions(self) -> Any:
        return await self._native_private("get_positions")

    async def get_deposits(self) -> Any:
        return await self._native_private("get_deposits")

    async def get_withdrawals(self) -> Any:
        return await self._native_private("get_withdrawals")

    async def get_klines(
        self,
        market: str,
        resolution: str,
        from_time: int,
        to_time: int,
    ) -> Any:
        return await self._native_private(
            "get_klines",
            market=market,
            resolution=resolution,
            from_time=from_time,
            to_time=to_time,
        )

    async def get_leverage(self, market: str | None = None) -> Any:
        return await self._native_private("get_leverage", market=market)

    async def set_leverage(self, market: str, leverage: str) -> Any:
        return await self._native_private(
            "set_leverage",
            market=market,
            leverage=leverage,
        )

    async def get_portfolio_summary(self) -> Any:
        return await self._native_private("get_portfolio_summary")

    async def get_max_order_size(self, market: str, buffer: str | None = None) -> Any:
        return await self._native_private(
            "get_max_order_size",
            market=market,
            buffer=buffer,
        )

    async def get_open_order_counts(self) -> Any:
        return await self._native_private("get_open_order_counts")

    async def get_deposit(self, depositID: str) -> Any:
        return await self._native_private("get_deposit", depositID=depositID)

    async def get_withdrawal(self, withdrawalID: str) -> Any:
        return await self._native_private("get_withdrawal", withdrawalID=withdrawalID)

    async def get_withdrawal_limits(self) -> Any:
        return await self._native_private("get_withdrawal_limits")

    async def get_deposit_addresses(
        self,
        coins: list[str],
        network: str | None = None,
        depositDestination: dict[str, object] | None = None,
    ) -> Any:
        return await self._native_private(
            "get_deposit_addresses",
            coins=coins,
            network=network,
            depositDestination=depositDestination,
        )

    async def export_deposits_csv(
        self,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:
        return await self._native_private(
            "export_deposits_csv",
            start_time=start_time,
            end_time=end_time,
        )

    async def export_withdrawals_csv(
        self,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:
        return await self._native_private(
            "export_withdrawals_csv",
            start_time=start_time,
            end_time=end_time,
        )

    async def get_address_book(self) -> Any:
        return await self._native_private("get_address_book")

    async def list_api_keys(self) -> Any:
        return await self._native_private("list_api_keys")

    async def get_address_book_challenge(
        self,
        walletAddress: str,
        chainId: str,
        withdrawalAddress: str,
    ) -> Any:
        return await self._native_private(
            "get_address_book_challenge",
            walletAddress=walletAddress,
            chainId=chainId,
            withdrawalAddress=withdrawalAddress,
        )

    async def complete_address_book_challenge(
        self,
        id: str,
        signature: str,
        addressLabel: str | None = None,
    ) -> Any:
        return await self._native_private(
            "complete_address_book_challenge",
            id=id,
            signature=signature,
            addressLabel=addressLabel,
        )

    async def sandbox_deposit(
        self,
        amount: str,
        symbol: str,
        deposit_destination: dict[str, object],
        chain_id: str,
    ) -> Any:
        return await self._native_private(
            "sandbox_deposit",
            amount=amount,
            symbol=symbol,
            deposit_destination=deposit_destination,
            chain_id=chain_id,
        )

    async def provision_deposit_address(
        self,
        network: str,
        symbol: str,
        deposit_destination: dict[str, object],
    ) -> Any:
        return await self._native_private(
            "provision_deposit_address",
            network=network,
            symbol=symbol,
            deposit_destination=deposit_destination,
        )

    async def get_withdrawal_status(
        self,
        withdrawal_id: str | None = None,
        customer_withdrawal_id: str | None = None,
    ) -> Any:
        return await self._native_private(
            "get_withdrawal_status",
            withdrawal_id=withdrawal_id,
            customer_withdrawal_id=customer_withdrawal_id,
        )

    async def edit_address_book_entry(
        self,
        withdrawalAddress: str,
        addressLabel: str | None = None,
    ) -> Any:
        return await self._native_private(
            "edit_address_book_entry",
            withdrawalAddress=withdrawalAddress,
            addressLabel=addressLabel,
        )

    async def remove_address_book_entry(self, withdrawalAddress: str) -> Any:
        return await self._native_private(
            "remove_address_book_entry",
            withdrawalAddress=withdrawalAddress,
        )

    async def create_api_key(self, name: str, scopes: list[str]) -> Any:
        return await self._native_private("create_api_key", name=name, scopes=scopes)

    async def delete_api_key(self, apiKeyID: str) -> Any:
        return await self._native_private("delete_api_key", apiKeyID=apiKeyID)

    async def set_api_key_ip_whitelist(self, apiKeyID: str, ip: str) -> Any:
        return await self._native_private(
            "set_api_key_ip_whitelist",
            apiKeyID=apiKeyID,
            ip=ip,
        )

    async def remove_api_key_ip_whitelist(self, apiKeyID: str, ip: str) -> Any:
        return await self._native_private(
            "remove_api_key_ip_whitelist",
            apiKeyID=apiKeyID,
            ip=ip,
        )

    async def get_candles(
        self,
        market: str,
        resolution: str,
        from_time: int,
        to_time: int,
    ) -> Any:
        return await self._native_private(
            "get_candles",
            market=market,
            resolution=resolution,
            from_time=from_time,
            to_time=to_time,
        )

    async def get_funding_fee_payments(
        self,
        market: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return await self._native_private(
            "get_funding_fee_payments",
            market=market,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )

    async def get_order_summaries(self) -> Any:
        return await self._native_private("get_order_summaries")

    async def get_liquidation_history(
        self,
        market: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return await self._native_private(
            "get_liquidation_history",
            market=market,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )

    async def get_portfolio_summary_graph(self, range_: str | None = None) -> Any:
        return await self._native_private("get_portfolio_summary_graph", range_=range_)
