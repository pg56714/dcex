# ruff: noqa: ANN401
"""Arcus HTTP implementation mixins."""

from typing import Any

from ...arcus.client import _params
from ._http_manager import HTTPManager, SpotHTTPManager


class MarketHTTP(HTTPManager):
    """Arcus perpetual market methods."""

    async def get_markets(self) -> Any:  # noqa: ANN401
        """Get all perpetual markets."""
        return await self.public_request("get_markets")

    async def get_spot_assets(self) -> Any:  # noqa: ANN401
        """Get lending collateral assets; these are not RFQ spot pairs."""
        return await self.public_request("get_spot_assets")

    async def get_fee_tiers(self) -> Any:  # noqa: ANN401
        """Get exchange-wide perpetual fee tiers."""
        return await self.public_request("get_fee_tiers")

    async def get_bbo(self, market: str) -> Any:  # noqa: ANN401
        """Get the best bid and offer for a market such as BTC-USD."""
        return await self.public_request("get_bbo", market=market)

    async def get_l2_orderbook(self, market: str, depth: int | None = None) -> Any:  # noqa: ANN401
        """Get an L2 orderbook snapshot."""
        return await self.public_request("get_l2_orderbook", market=market, nLevels=depth)

    async def get_trade(self, *, trade_id: str, market: str) -> Any:  # noqa: ANN401
        """
        GET /v1/trade/{tradeId}; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-a-single-trade-by-id.md
        """
        return await self.public_request("get_trade", **{"trade_id": trade_id, "market": market})

    async def get_mid_prices(self, *, market: str | None = None) -> Any:  # noqa: ANN401
        """
        GET /v1/mids; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-all-mid-prices.md
        """
        return await self.public_request("get_mid_prices", **{"market": market})

    async def get_time(self) -> Any:  # noqa: ANN401
        """
        GET /v1/time; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-current-server-time.md
        """
        return await self.public_request("get_time", **{})

    async def get_funding(
        self,
        *,
        address: str | None = None,
        account_index: int | None = None,
        market: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/funding; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-funding-payments.md
        """
        return await self.public_request(
            "get_funding",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
                "market": market,
                "from": start_time,
                "to": end_time,
                "limit": limit,
            },
        )

    async def get_interest(
        self,
        *,
        address: str | None = None,
        account_index: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/interest; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-interest-payments.md
        """
        return await self.public_request(
            "get_interest",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
                "from": start_time,
                "to": end_time,
                "limit": limit,
            },
        )

    async def get_live_prices(self, *, market: str | None = None) -> Any:  # noqa: ANN401
        """
        GET /v1/prices; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-live-prices-for-all-markets.md
        """
        return await self.public_request("get_live_prices", **{"market": market})

    async def get_funding_rates(
        self,
        *,
        market: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/fundingRates; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-market-funding-rates.md
        """
        return await self.public_request(
            "get_funding_rates",
            **{"market": market, "from": start_time, "to": end_time, "limit": limit},
        )

    async def get_candles(
        self,
        *,
        market: str,
        timeframe: str,
        end_time: int,
        start_time: int | None = None,
        countback: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/candles; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-ohlcv-candles.md
        """
        return await self.public_request(
            "get_candles",
            **{
                "market": market,
                "timeframe": timeframe,
                "to": end_time,
                "from": start_time,
                "countback": countback,
            },
        )

    async def get_trades(
        self,
        *,
        market: str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/trades; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-recent-public-trades.md
        """
        return await self.public_request(
            "get_trades", **{"market": market, "limit": limit, "from": start_time, "to": end_time}
        )

    async def health(self) -> Any:  # noqa: ANN401
        """
        GET /health; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/health-check.md
        """
        return await self.public_request("health", **{})

    async def get_service_info(self) -> Any:  # noqa: ANN401
        """
        GET /; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/service-info.md
        """
        return await self.public_request("get_service_info", **{})

    async def get_market_metadata(self, *, market: str | None = None) -> Any:  # noqa: ANN401
        """Public market metadata."""
        return await self.public_request("get_market_metadata", market=market)

    async def get_market_overview(self) -> Any:  # noqa: ANN401
        """Public consolidated market overview."""
        return await self.public_request("get_market_overview")

    async def get_spot_market_overview(self) -> Any:  # noqa: ANN401
        """Public spot universe and reference data."""
        return await self.public_request("get_spot_market_overview")

    async def get_metadata_candles(
        self,
        *,
        market: str,
        timeframe: str,
        to: int,
        from_: int | None = None,
        countback: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Metadata candles: timestamps use seconds; from_ or countback is required."""
        return await self.public_request(
            "get_metadata_candles",
            **{
                "market": market,
                "timeframe": timeframe,
                "to": to,
                "from": from_,
                "countback": countback,
            },
        )

    async def get_leaderboard(
        self,
        *,
        window: str | None = None,
        sort_by: str | None = None,
        address: str | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Query trader rankings; PnL is realized and the hourly rollup can lag."""
        return await self.public_request(
            "get_leaderboard",
            **{
                k: v
                for k, v in {
                    "window": window,
                    "sortBy": sort_by,
                    "address": address,
                    "limit": limit,
                }.items()
                if v is not None
            },
        )

    async def get_commission_rates(self) -> Any:  # noqa: ANN401
        """
        GET /v1/commissionrates.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/public/get-referral-commission-rate-schedule
        """
        return await self.public_request("get_commission_rates", **{})

    async def check_referral_code(self, *, code: str) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/codeAvailable.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/referral/check-whether-a-referral-code-is-available
        """
        return await self.public_request("check_referral_code", **{"code": code})

    async def claim_affiliate_commission(
        self, *, address: str, cutoff_fill_id: int | None = None, amount_quantums: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/claim.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/claim-accrued-commission
        """
        return await self.private_request(
            "claim_affiliate_commission",
            **{
                "address": address,
                "cutoffFillId": cutoff_fill_id,
                "amountQuantums": amount_quantums,
            },
        )

    async def create_referral_code(self, *, address: str, code: str, kickback_bps: int) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/createCode.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/create-referral-code
        """
        return await self.private_request(
            "create_referral_code",
            **{"address": address, "code": code, "kickbackBps": kickback_bps},
        )

    async def get_affiliate_claims(
        self,
        *,
        address: str,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/claims.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/referral/get-affiliate-claim-history
        """
        return await self.public_request(
            "get_affiliate_claims", **{"address": address, "from": from_, "to": to, "limit": limit}
        )

    async def get_affiliate_commissions(
        self,
        *,
        address: str,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/commissions.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/get-affiliate-commission-history
        """
        return await self.private_request(
            "get_affiliate_commissions",
            **{"address": address, "from": from_, "to": to, "limit": limit, "cursor": cursor},
        )

    async def get_affiliate_info(self, *, address: str) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/info.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/get-affiliate-info
        """
        return await self.private_request("get_affiliate_info", **{"address": address})

    async def get_affiliate_leaderboard(self, *, limit: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/leaderboard.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/referral/get-affiliate-leaderboard
        """
        return await self.public_request("get_affiliate_leaderboard", **{"limit": limit})

    async def get_referrer(self, *, address: str) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/myReferrer.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/referral/get-my-referrer
        """
        return await self.public_request("get_referrer", **{"address": address})

    async def get_referees(
        self,
        *,
        address: str,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/referees.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/get-referees
        """
        return await self.private_request(
            "get_referees",
            **{"address": address, "from": from_, "to": to, "limit": limit, "cursor": cursor},
        )

    async def get_referral_code(self, *, address: str) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/code.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/get-the-callers-referral-code
        """
        return await self.private_request("get_referral_code", **{"address": address})

    async def get_invite_codes(
        self,
        *,
        address: str,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/inviteCodes.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/list-the-callers-invite-codes
        """
        return await self.private_request(
            "get_invite_codes",
            **{"address": address, "status": status, "limit": limit, "offset": offset},
        )

    async def get_affiliate_claim(self, *, address: str, id: str) -> Any:  # noqa: ANN401
        """
        GET /v1/affiliate/claimStatus.

        Public affiliate metadata query.
        Source: https://docs.arcus.xyz/api-reference/referral/look-up-a-single-claim
        """
        return await self.public_request("get_affiliate_claim", **{"address": address, "id": id})

    async def redeem_invite_code(self, *, address: str, invite_code: str) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/redeemInvite.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/redeem-an-invite-code
        """
        return await self.private_request(
            "redeem_invite_code", **{"address": address, "inviteCode": invite_code}
        )

    async def register_referral(self, *, address: str, code: str) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/registerAffiliate.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/register-as-referee
        """
        return await self.private_request("register_referral", **{"address": address, "code": code})

    async def rename_referral_code(self, *, address: str, code: str) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/modifyCode.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/rename-referral-code
        """
        return await self.private_request(
            "rename_referral_code", **{"address": address, "code": code}
        )

    async def revoke_referral_code(self, *, address: str) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/revokeCode.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/revoke-referral-code
        """
        return await self.private_request("revoke_referral_code", **{"address": address})

    async def update_referral_kickback(self, *, address: str, kickback_bps: int) -> Any:  # noqa: ANN401
        """
        POST /v1/affiliate/kickback.

        Signed affiliate access is scoped to the configured master address.
        Source: https://docs.arcus.xyz/api-reference/referral/update-kickback-rate
        """
        return await self.private_request(
            "update_referral_kickback", **{"address": address, "kickbackBps": kickback_bps}
        )


class SpotMarketHTTP(SpotHTTPManager):
    """Arcus spot market methods."""

    async def health(self) -> Any:  # noqa: ANN401
        """Get the router's unversioned health status."""
        return await self._call("public_request", "health", [])

    async def get_tokens(self) -> Any:  # noqa: ANN401
        """Get supported spot tokens and their on-chain addresses."""
        return await self._call("public_request", "get_tokens", [])

    async def get_price(
        self,
        sell_token: str,
        buy_token: str,
        sell_amount: str,
        *,
        builder_fee_bps: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Get indicative prices. Amount is in sell-token atomic units."""
        return await self._call(
            "public_request",
            "get_price",
            _params(
                sellToken=sell_token,
                buyToken=buy_token,
                sellAmount=sell_amount,
                builderFeeBps=builder_fee_bps,
            ),
        )

    async def get_quote(
        self,
        sell_token: str,
        buy_token: str,
        sell_amount: str,
        taker: str,
        *,
        slippage_bps: int | None = None,
        allow_wrapped: bool | None = None,
        builder_fee_bps: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Get firm quotes for wallet signing; this does not place a trade."""
        return await self._call(
            "public_request",
            "get_quote",
            _params(
                sellToken=sell_token,
                buyToken=buy_token,
                sellAmount=sell_amount,
                taker=taker,
                slippageBps=slippage_bps,
                allowWrapped=allow_wrapped,
                builderFeeBps=builder_fee_bps,
            ),
        )

    async def get_block_number(self) -> Any:  # noqa: ANN401
        """Read the current Robinhood Chain block number for history paging."""
        return await self._call("public_request", "get_block_number", [])

    async def get_transaction_receipt(self, tx_hash: str) -> Any:  # noqa: ANN401
        """Read a transaction receipt; returns None while still pending."""
        return await self._call(
            "public_request", "get_transaction_receipt", _params(tx_hash=tx_hash)
        )

    async def get_status(self, tx_hash: str) -> Any:  # noqa: ANN401
        """Get normalized execution status for a submitted Arcus spot trade."""
        return await self._call("public_request", "get_status", _params(venue="arcus", id=tx_hash))
