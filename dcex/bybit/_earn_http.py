"""Bybit Earn HTTP client backed by Rust."""

from typing import Any

from .._native_http import request_native_json
from ._http_manager import HTTPManager


class EarnHTTP(HTTPManager):
    """HTTP client for Bybit Easy, On-chain, and Advanced Earn workflows."""

    def _earn_native_public(self, method_name: str, params: list[tuple[str, str]]) -> Any:  # noqa: ANN401
        if self._native_client is None:
            raise RuntimeError("Bybit native client is required for public Earn methods.")
        response, data = request_native_json(
            self._native_client, "public_request", method_name, params
        )
        self._store_response_headers(response)
        return data

    def get_earn_products(self, category: str, coin: str | None = None) -> dict[str, Any]:
        """List public Bybit Earn products."""
        return self._earn_native_public(
            "get_earn_products",
            self._native_params(category=category, coin=coin),
        )

    def place_earn_order(
        self,
        category: str,
        orderType: str,
        accountType: str,
        amount: str,
        coin: str,
        productId: str,
        orderLinkId: str,
        *,
        redeemPositionId: str | None = None,
        toAccountType: str | None = None,
        interestCard: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        """Stake into or redeem from a Bybit Earn product."""
        return self._native_private(
            "place_earn_order",
            self._native_params(
                category=category,
                orderType=orderType,
                accountType=accountType,
                amount=amount,
                coin=coin,
                productId=productId,
                orderLinkId=orderLinkId,
                redeemPositionId=redeemPositionId,
                toAccountType=toAccountType,
                interestCard=interestCard,
            ),
        )

    def get_earn_order_history(
        self,
        category: str,
        *,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        productId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return Bybit Earn stake and redemption history."""
        return self._native_private(
            "get_earn_order_history",
            self._native_params(
                category=category,
                orderId=orderId,
                orderLinkId=orderLinkId,
                productId=productId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_earn_positions(
        self,
        category: str,
        *,
        productId: str | None = None,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """Return Bybit Earn positions."""
        return self._native_private(
            "get_earn_positions",
            self._native_params(category=category, productId=productId, coin=coin),
        )

    def get_earn_yield_history(
        self,
        category: str,
        *,
        productId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return daily Bybit Earn yield history."""
        return self._earn_yield_query(
            "get_earn_yield_history",
            category,
            productId,
            startTime,
            endTime,
            limit,
            cursor,
        )

    def get_earn_hourly_yield_history(
        self,
        category: str = "FlexibleSaving",
        *,
        productId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return hourly Flexible Saving yield history."""
        return self._earn_yield_query(
            "get_earn_hourly_yield_history",
            category,
            productId,
            startTime,
            endTime,
            limit,
            cursor,
        )

    def _earn_yield_query(
        self,
        method_name: str,
        category: str,
        product_id: str | None,
        start_time: int | None,
        end_time: int | None,
        limit: int | None,
        cursor: str | None,
    ) -> dict[str, Any]:
        return self._native_private(
            method_name,
            self._native_params(
                category=category,
                productId=product_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_advanced_earn_products(
        self,
        category: str,
        *,
        coin: str | None = None,
        duration: str | None = None,
    ) -> dict[str, Any]:
        """List Dual Assets, Smart Leverage, Double Win, or Discount Buy products."""
        return self._earn_native_public(
            "get_advanced_earn_products",
            self._native_params(category=category, coin=coin, duration=duration),
        )

    def get_advanced_earn_product_quote(self, category: str, productId: str) -> dict[str, Any]:
        """Return the current quote for an Advanced Earn product."""
        return self._earn_native_public(
            "get_advanced_earn_product_quote",
            self._native_params(category=category, productId=productId),
        )

    def place_advanced_earn_order(
        self,
        category: str,
        productId: str,
        orderType: str,
        accountType: str,
        orderLinkId: str,
        *,
        amount: str | None = None,
        coin: str | None = None,
        dualAssetsExtra: dict[str, object] | None = None,
        smartLeverageStakeExtra: dict[str, object] | None = None,
        smartLeverageRedeemExtra: dict[str, object] | None = None,
        doubleWinStakeExtra: dict[str, object] | None = None,
        doubleWinRedeemExtra: dict[str, object] | None = None,
        discountBuyExtra: dict[str, object] | None = None,
        interestCard: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        """Place an Advanced Earn stake or supported early-redemption order."""
        return self._native_private(
            "place_advanced_earn_order",
            self._native_params(
                category=category,
                productId=productId,
                orderType=orderType,
                accountType=accountType,
                orderLinkId=orderLinkId,
                amount=amount,
                coin=coin,
                dualAssetsExtra=dualAssetsExtra,
                smartLeverageStakeExtra=smartLeverageStakeExtra,
                smartLeverageRedeemExtra=smartLeverageRedeemExtra,
                doubleWinStakeExtra=doubleWinStakeExtra,
                doubleWinRedeemExtra=doubleWinRedeemExtra,
                discountBuyExtra=discountBuyExtra,
                interestCard=interestCard,
            ),
        )

    def get_advanced_earn_positions(
        self,
        category: str,
        *,
        productId: str | None = None,
        coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return active Advanced Earn positions."""
        return self._native_private(
            "get_advanced_earn_positions",
            self._native_params(
                category=category,
                productId=productId,
                coin=coin,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_advanced_earn_orders(
        self,
        category: str,
        *,
        productId: str | None = None,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return Advanced Earn order history."""
        return self._native_private(
            "get_advanced_earn_orders",
            self._native_params(
                category=category,
                productId=productId,
                orderId=orderId,
                orderLinkId=orderLinkId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_advanced_earn_redeem_estimates(self, category: str, positionIds: str) -> dict[str, Any]:
        """Estimate early-redemption proceeds for up to five positions."""
        return self._native_private(
            "get_advanced_earn_redeem_estimates",
            self._native_params(category=category, positionIds=positionIds),
        )

    def get_double_win_leverage(
        self,
        productId: str,
        initialPrice: str,
        lowerPrice: str,
        upperPrice: str,
    ) -> dict[str, Any]:
        """Calculate leverage for a custom Double Win price range."""
        return self._native_private(
            "get_double_win_leverage",
            self._native_params(
                productId=productId,
                initialPrice=initialPrice,
                lowerPrice=lowerPrice,
                upperPrice=upperPrice,
            ),
        )

    def get_liquidity_mining_products(
        self, *, baseCoin: str | None = None, quoteCoin: str | None = None
    ) -> dict[str, Any]:
        """List public Liquidity Mining pools."""
        return self._earn_native_public(
            "get_liquidity_mining_products",
            self._native_params(baseCoin=baseCoin, quoteCoin=quoteCoin),
        )

    def get_liquidity_mining_positions(
        self, *, productId: str | None = None, baseCoin: str | None = None
    ) -> dict[str, Any]:
        """List active Liquidity Mining positions."""
        return self._native_private(
            "get_liquidity_mining_positions",
            self._native_params(productId=productId, baseCoin=baseCoin),
        )

    def get_liquidity_mining_orders(
        self,
        *,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        productId: str | None = None,
        orderType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List Liquidity Mining orders or query one order by ID."""
        return self._native_private(
            "get_liquidity_mining_orders",
            self._native_params(
                orderId=orderId,
                orderLinkId=orderLinkId,
                productId=productId,
                orderType=orderType,
                startTime=startTime,
                endTime=endTime,
                status=status,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_liquidity_mining_yield_records(
        self,
        *,
        baseCoin: str | None = None,
        quoteCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List Liquidity Mining yield claim records."""
        return self._native_private(
            "get_liquidity_mining_yield_records",
            self._native_params(
                baseCoin=baseCoin,
                quoteCoin=quoteCoin,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_liquidity_mining_liquidation_records(
        self,
        *,
        baseCoin: str | None = None,
        quoteCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List Liquidity Mining liquidation history."""
        return self._native_private(
            "get_liquidity_mining_liquidation_records",
            self._native_params(
                baseCoin=baseCoin,
                quoteCoin=quoteCoin,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def add_liquidity_mining(
        self,
        productId: str,
        orderLinkId: str,
        *,
        quoteAmount: str | None = None,
        baseAmount: str | None = None,
        quoteAccountType: str | None = None,
        baseAccountType: str | None = None,
        leverage: str | None = None,
    ) -> dict[str, Any]:
        """Submit a Liquidity Mining deposit."""
        return self._native_private(
            "add_liquidity_mining",
            self._native_params(
                productId=productId,
                orderLinkId=orderLinkId,
                quoteAmount=quoteAmount,
                baseAmount=baseAmount,
                quoteAccountType=quoteAccountType,
                baseAccountType=baseAccountType,
                leverage=leverage,
            ),
        )

    def remove_liquidity_mining(
        self,
        productId: str,
        orderLinkId: str,
        positionId: str,
        *,
        removeRate: int | None = None,
        removeType: str | None = None,
    ) -> dict[str, Any]:
        """Submit a Liquidity Mining withdrawal."""
        return self._native_private(
            "remove_liquidity_mining",
            self._native_params(
                productId=productId,
                orderLinkId=orderLinkId,
                positionId=positionId,
                removeRate=removeRate,
                removeType=removeType,
            ),
        )

    def reinvest_liquidity_mining(
        self,
        productId: str,
        orderLinkId: str,
        positionId: str,
        *,
        leverage: str | None = None,
    ) -> dict[str, Any]:
        """Reinvest claimable Liquidity Mining yield."""
        return self._native_private(
            "reinvest_liquidity_mining",
            self._native_params(
                productId=productId,
                orderLinkId=orderLinkId,
                positionId=positionId,
                leverage=leverage,
            ),
        )

    def add_liquidity_mining_margin(
        self,
        productId: str,
        orderLinkId: str,
        positionId: str,
        amount: str,
        quoteAccountType: str,
    ) -> dict[str, Any]:
        """Add margin to a leveraged Liquidity Mining position."""
        return self._native_private(
            "add_liquidity_mining_margin",
            self._native_params(
                productId=productId,
                orderLinkId=orderLinkId,
                positionId=positionId,
                amount=amount,
                quoteAccountType=quoteAccountType,
            ),
        )

    def claim_liquidity_mining_interest(self, productId: str) -> dict[str, Any]:
        """Claim available Liquidity Mining interest for a product or all pools."""
        return self._native_private(
            "claim_liquidity_mining_interest",
            self._native_params(productId=productId),
        )

    def get_fixed_earn_products(self, *, coin: str | None = None) -> dict[str, Any]:
        """List Bybit Fixed Saving products."""
        return self._earn_native_public("get_fixed_earn_products", self._native_params(coin=coin))

    def get_fixed_earn_positions(
        self,
        *,
        productId: str | None = None,
        category: str | None = None,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """List active Fixed Saving positions."""
        return self._native_private(
            "get_fixed_earn_positions",
            self._native_params(productId=productId, category=category, coin=coin),
        )

    def get_fixed_earn_orders(
        self,
        *,
        orderType: str | None = None,
        productId: str | None = None,
        category: str | None = None,
        orderId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List Fixed Saving orders or query one order."""
        return self._native_private(
            "get_fixed_earn_orders",
            self._native_params(
                orderType=orderType,
                productId=productId,
                category=category,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def place_fixed_earn_order(
        self,
        productId: str,
        category: str,
        coin: str,
        amount: str,
        accountType: str,
        orderLinkId: str,
        *,
        autoInvest: bool | None = None,
    ) -> dict[str, Any]:
        """Subscribe to a Fixed Saving product."""
        return self._native_private(
            "place_fixed_earn_order",
            self._native_params(
                productId=productId,
                category=category,
                coin=coin,
                amount=amount,
                accountType=accountType,
                orderLinkId=orderLinkId,
                autoInvest=autoInvest,
            ),
        )

    def redeem_fixed_earn(self, productId: str, category: str, positionId: str) -> dict[str, Any]:
        """Request an eligible FundPool early redemption."""
        return self._native_private(
            "redeem_fixed_earn",
            self._native_params(productId=productId, category=category, positionId=positionId),
        )

    def set_fixed_earn_auto_invest(
        self, productId: str, category: str, positionId: str, status: str
    ) -> dict[str, Any]:
        """Enable or disable Fixed Saving automatic reinvestment."""
        return self._native_private(
            "set_fixed_earn_auto_invest",
            self._native_params(
                productId=productId,
                category=category,
                positionId=positionId,
                status=status,
            ),
        )

    def get_hold_to_earn_products(self) -> dict[str, Any]:
        """List available Hold-to-Earn airdrop products."""
        return self._earn_native_public("get_hold_to_earn_products", [])

    def get_hold_to_earn_yield_history(
        self,
        limit: int = 20,
        *,
        timeStart: int | None = None,
        timeEnd: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List distributed Hold-to-Earn yield records."""
        return self._native_private(
            "get_hold_to_earn_yield_history",
            self._native_params(timeStart=timeStart, timeEnd=timeEnd, limit=limit, cursor=cursor),
        )

    def get_byusdt_product(self) -> dict[str, Any]:
        """Get the public BYUSDT Earn product details."""
        return self._earn_native_public("get_byusdt_product", [])

    def get_byusdt_apr_history(self, range: int) -> dict[str, Any]:
        """Get BYUSDT APR history for 7, 30, or 180 days."""
        return self._earn_native_public("get_byusdt_apr_history", self._native_params(range=range))

    def get_byusdt_orders(
        self,
        *,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        orderType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List BYUSDT mint and redeem orders; times are Unix seconds."""
        return self._native_private(
            "get_byusdt_orders",
            self._native_params(
                orderId=orderId,
                orderLinkId=orderLinkId,
                orderType=orderType,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_byusdt_position(self) -> dict[str, Any]:
        """Get current BYUSDT holdings and accrued yield."""
        return self._native_private("get_byusdt_position", [])

    def get_byusdt_daily_yield(
        self,
        *,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get BYUSDT daily yield; times are Unix seconds."""
        return self._native_private(
            "get_byusdt_daily_yield",
            self._native_params(startTime=startTime, endTime=endTime, limit=limit, cursor=cursor),
        )

    def get_byusdt_hourly_yield(
        self,
        *,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get BYUSDT hourly yield; times are Unix seconds."""
        return self._native_private(
            "get_byusdt_hourly_yield",
            self._native_params(startTime=startTime, endTime=endTime, limit=limit, cursor=cursor),
        )

    def place_byusdt_order(
        self, orderType: str, amount: str, accountType: str, orderLinkId: str
    ) -> dict[str, Any]:
        """Mint from Flexible Saving or redeem to the Unified account."""
        return self._native_private(
            "place_byusdt_order",
            self._native_params(
                orderType=orderType,
                amount=amount,
                accountType=accountType,
                orderLinkId=orderLinkId,
            ),
        )

    def get_rwa_earn_products(self, coin: str | None = None) -> dict[str, Any]:
        """List public Bybit RWA Earn products."""
        return self._earn_native_public("get_rwa_earn_products", self._native_params(coin=coin))

    def get_rwa_earn_nav_chart(
        self,
        productId: int,
        *,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get a product's NAV history; times are Unix seconds."""
        return self._earn_native_public(
            "get_rwa_earn_nav_chart",
            self._native_params(productId=productId, startTime=startTime, endTime=endTime),
        )

    def get_rwa_earn_positions(self) -> dict[str, Any]:
        """List owned RWA Earn positions."""
        return self._native_private("get_rwa_earn_positions", [])

    def get_rwa_earn_orders(
        self,
        *,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        orderType: str | None = None,
        productId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List RWA Earn stake and redemption orders; times are Unix seconds."""
        return self._native_private(
            "get_rwa_earn_orders",
            self._native_params(
                orderId=orderId,
                orderLinkId=orderLinkId,
                orderType=orderType,
                productId=productId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def place_rwa_earn_order(
        self,
        productId: int,
        orderType: str,
        coin: str,
        orderLinkId: str,
        *,
        stakeAmount: str | None = None,
        redeemShares: str | None = None,
        accountType: str = "FUND",
    ) -> dict[str, Any]:
        """Stake or redeem RWA Earn shares; settlement is asynchronous."""
        return self._native_private(
            "place_rwa_earn_order",
            self._native_params(
                productId=productId,
                orderType=orderType,
                coin=coin,
                orderLinkId=orderLinkId,
                stakeAmount=stakeAmount,
                redeemShares=redeemShares,
                accountType=accountType,
            ),
        )

    def get_earn_apr_history(
        self,
        category: str,
        productId: str,
        *,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get Easy or On-Chain Earn APR history; times are Unix milliseconds."""
        return self._earn_native_public(
            "get_earn_apr_history",
            self._native_params(
                category=category,
                productId=productId,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_earn_coupons(self, category: str) -> dict[str, Any]:
        """List Flexible Saving interest coupons or Dual Assets reward cards."""
        return self._native_private("get_earn_coupons", self._native_params(category=category))

    def set_earn_auto_reinvest(
        self, productId: int, positionId: int, autoReinvest: int
    ) -> dict[str, Any]:
        """Toggle auto-reinvestment on an eligible fixed On-Chain position."""
        return self._native_private(
            "set_earn_auto_reinvest",
            self._native_params(
                category="OnChain",
                productId=productId,
                positionId=positionId,
                autoReinvest=autoReinvest,
            ),
        )
