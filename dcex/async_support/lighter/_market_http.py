"""Lighter async public market-data HTTP client."""

from typing import Any, Literal

from ..._native_http import NativeResponse
from ._http_manager import HTTPManager
from .endpoints.market import Public


def _auth_header(authorization: str | None) -> dict[str, str] | None:
    return {"Authorization": authorization} if authorization is not None else None


class MarketHTTP(HTTPManager):
    """Async HTTP client for Lighter public REST APIs."""

    @staticmethod
    def _native_params(query: dict[str, Any] | None) -> list[tuple[str, str]]:
        params: list[tuple[str, str]] = []
        for key, value in (query or {}).items():
            if value is None:
                continue
            if isinstance(value, bool):
                value = str(value).lower()
            params.append((key, str(value)))
        return params

    async def _request(
        self,
        method: Literal["GET", "POST"],
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        signed: bool = False,
        headers: dict[str, str] | None = None,
        content_type: Literal["json", "form"] = "json",
    ) -> dict[str, Any] | list[Any]:
        if (
            method.upper() == "GET"
            and not signed
            and body is None
            and content_type == "json"
            and self._native_client is not None
        ):
            native_headers = {key: value for key, value in (headers or {}).items() if value}
            (
                status,
                response_headers,
                response_body,
            ) = await self._native_client.public_request_async(
                str(path),
                self._native_params(query),
                native_headers,
            )
            response = NativeResponse(status, dict(response_headers), bytes(response_body))
            self._store_response_headers(response)
            return response.json()
        return await super()._request(method, path, query, body, signed, headers, content_type)

    async def get_info(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter API service info."""
        return await self._request("GET", Public.INFO)

    async def get_status(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter API service status."""
        return await self._request("GET", Public.STATUS)

    async def get_announcement(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter announcements."""
        return await self._request("GET", Public.ANNOUNCEMENT)

    async def get_order_book_details(
        self,
        market_id: int | None = None,
        filter: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter order book metadata."""
        return await self._request(
            "GET",
            Public.ORDER_BOOK_DETAILS,
            {"market_id": market_id, "filter": filter},
        )

    async def get_order_books(
        self,
        market_id: int | None = None,
        filter: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter order books."""
        return await self._request(
            "GET",
            Public.ORDER_BOOKS,
            {"market_id": market_id, "filter": filter},
        )

    async def get_order_book_orders(
        self,
        market_id: int,
        limit: int,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter order book orders."""
        return await self._request(
            "GET",
            Public.ORDER_BOOK_ORDERS,
            {"market_id": market_id, "limit": limit},
        )

    async def get_recent_trades(
        self,
        market_id: int,
        limit: int,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve recent Lighter trades."""
        return await self._request(
            "GET",
            Public.RECENT_TRADES,
            {"market_id": market_id, "limit": limit},
        )

    async def get_trades(
        self,
        sort_by: str,
        limit: int,
        market_id: int | None = None,
        market_type: str | None = None,
        account_index: int | None = None,
        order_index: int | None = None,
        sort_dir: str | None = None,
        cursor: str | None = None,
        from_: int | None = None,
        ask_filter: int | None = None,
        role: str | None = None,
        type_: str | None = None,
        aggregate: bool | None = None,
        skip_ask_order_id: str | None = None,
        skip_bid_order_id: str | None = None,
        auth: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve auth-gated Lighter trades."""
        if authorization is None and auth is None and self.api_private_key is not None:
            authorization = self._auth_token()
        return await self._request(
            "GET",
            Public.TRADES,
            {
                "market_id": market_id,
                "market_type": market_type,
                "account_index": account_index,
                "order_index": order_index,
                "sort_by": sort_by,
                "sort_dir": sort_dir,
                "cursor": cursor,
                "from": from_,
                "ask_filter": ask_filter,
                "role": role,
                "type": type_,
                "limit": limit,
                "aggregate": aggregate,
                "skip_ask_order_id": skip_ask_order_id,
                "skip_bid_order_id": skip_bid_order_id,
                "auth": auth,
            },
            headers=_auth_header(authorization),
        )

    async def get_candles(
        self,
        market_id: int,
        resolution: str,
        start_timestamp: int,
        end_timestamp: int,
        count_back: int,
        set_timestamp_to_end: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter candlesticks."""
        return await self._request(
            "GET",
            Public.CANDLES,
            {
                "market_id": market_id,
                "resolution": resolution,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "count_back": count_back,
                "set_timestamp_to_end": set_timestamp_to_end,
            },
        )

    async def get_funding_rates(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter funding rates."""
        return await self._request("GET", Public.FUNDING_RATES)

    async def get_fundings(
        self,
        market_id: int,
        resolution: str,
        start_timestamp: int,
        end_timestamp: int,
        count_back: int,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter historical fundings."""
        return await self._request(
            "GET",
            Public.FUNDINGS,
            {
                "market_id": market_id,
                "resolution": resolution,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "count_back": count_back,
            },
        )

    async def get_exchange_stats(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter exchange statistics."""
        return await self._request("GET", Public.EXCHANGE_STATS)

    async def get_execute_stats(self, period: str) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter execution statistics."""
        return await self._request("GET", Public.EXECUTE_STATS, {"period": period})

    async def get_exchange_metrics(
        self,
        period: str,
        kind: str,
        filter: str | None = None,
        value: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter exchange metrics."""
        return await self._request(
            "GET",
            Public.EXCHANGE_METRICS,
            {"period": period, "kind": kind, "filter": filter, "value": value},
        )

    async def get_deposit_networks(self) -> dict[str, Any] | list[Any]:
        """Retrieve supported Lighter deposit networks."""
        return await self._request("GET", Public.DEPOSIT_NETWORKS)

    async def get_fastbridge_info(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter fast bridge information."""
        return await self._request("GET", Public.FASTBRIDGE_INFO)

    async def get_layer1_basic_info(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter layer-1 basic information."""
        return await self._request("GET", Public.LAYER1_BASIC_INFO)

    async def get_lease_options(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter account lease options."""
        return await self._request("GET", Public.LEASE_OPTIONS)

    async def get_withdrawal_delay(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter withdrawal delay information."""
        return await self._request("GET", Public.WITHDRAWAL_DELAY)

    async def get_account(
        self,
        by: str,
        value: str,
        active_only: bool | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve public Lighter account data."""
        return await self._request(
            "GET",
            Public.ACCOUNT,
            {"by": by, "value": value, "active_only": active_only, "cursor": cursor},
        )

    async def get_accounts_by_l1_address(
        self,
        l1_address: str,
        cursor: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter accounts tied to an L1 address."""
        return await self._request(
            "GET",
            Public.ACCOUNTS_BY_L1_ADDRESS,
            {"l1_address": l1_address, "cursor": cursor},
        )

    async def get_account_metadata(
        self,
        by: str,
        value: str,
        cursor: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter account metadata."""
        if authorization is None and self.api_private_key is not None:
            authorization = self._auth_token()
        return await self._request(
            "GET",
            Public.ACCOUNT_METADATA,
            {"by": by, "value": value, "cursor": cursor},
            headers=_auth_header(authorization),
        )

    async def get_api_keys(
        self,
        account_index: int,
        api_key_index: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter API key metadata."""
        return await self._request(
            "GET",
            Public.API_KEYS,
            {"account_index": account_index, "api_key_index": api_key_index},
        )

    async def get_public_pools_metadata(
        self,
        index: int,
        limit: int,
        filter: str | None = None,
        account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter public pool metadata."""
        if authorization is None and self.api_private_key is not None:
            authorization = self._auth_token()
        return await self._request(
            "GET",
            Public.PUBLIC_POOLS_METADATA,
            {
                "filter": filter,
                "index": index,
                "limit": limit,
                "account_index": account_index,
            },
            headers=_auth_header(authorization),
        )

    async def get_pnl(
        self,
        by: str,
        value: str,
        resolution: str,
        start_timestamp: int,
        end_timestamp: int,
        count_back: int,
        ignore_transfers: bool | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter PnL data."""
        if authorization is None and self.api_private_key is not None:
            authorization = self._auth_token()
        return await self._request(
            "GET",
            Public.PNL,
            {
                "by": by,
                "value": value,
                "resolution": resolution,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "count_back": count_back,
                "ignore_transfers": ignore_transfers,
            },
            headers=_auth_header(authorization),
        )

    async def get_asset_details(self, asset_id: int | None = None) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter asset metadata."""
        return await self._request("GET", Public.ASSET_DETAILS, {"asset_id": asset_id})

    async def get_system_config(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter system configuration."""
        return await self._request("GET", Public.SYSTEM_CONFIG)

    async def get_tokens(
        self,
        account_index: int,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter account tokens."""
        if authorization is None and self.api_private_key is not None:
            authorization = self._auth_token()
        return await self._request(
            "GET",
            Public.TOKENS,
            {"account_index": account_index},
            headers=_auth_header(authorization),
        )

    async def get_token_list(self) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter token list."""
        return await self._request("GET", Public.TOKENLIST)
