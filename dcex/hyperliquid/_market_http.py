# ruff: noqa: ANN401
# Exchange responses retain their native, heterogeneous JSON schemas.
"""Market-related HTTP API client for Hyperliquid exchange backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """HTTP client for market-related operations on Hyperliquid exchange."""

    def get_spot_fee_rates(self, user: str) -> dict[str, Any]:
        """Retrieve effective Hyperliquid Spot maker and taker fee rates."""
        return self._native_public(
            "get_spot_fee_rates",
            self._native_params(user=user),
        )

    def get_futures_fee_rates(self, user: str) -> dict[str, Any]:
        """Retrieve effective Hyperliquid Futures maker and taker fee rates."""
        return self._native_public(
            "get_futures_fee_rates",
            self._native_params(user=user),
        )

    def get_meta(self, dex: str | None = None) -> dict[str, Any]:
        """Get market metadata."""
        return self._native_public("get_meta", self._native_params(dex=dex))

    def get_perp_dexs(self) -> list[dict[str, Any] | None]:
        """Get the available perpetual DEXs."""
        return self._native_public("get_perp_dexs", [])

    def get_spot_meta(self) -> dict[str, Any]:
        """Get spot market metadata."""
        return self._native_public("get_spot_meta", [])

    def get_meta_and_asset_ctxs(self, dex: str | None = None) -> dict[str, Any]:
        """Get market metadata and asset contexts."""
        return self._native_public("get_meta_and_asset_ctxs", self._native_params(dex=dex))

    def get_spot_meta_and_asset_ctxs(self) -> dict[str, Any]:
        """Get spot market metadata and asset contexts."""
        return self._native_public("get_spot_meta_and_asset_ctxs", [])

    def get_l2book(
        self,
        product_symbol: str,
        nSigFigs: int | None = None,
        mantissa: int | None = None,
    ) -> dict[str, Any]:
        """Get L2 order book for a product."""
        return self._native_public(
            "get_l2book",
            self._native_params(
                product_symbol=product_symbol,
                nSigFigs=nSigFigs,
                mantissa=mantissa,
            ),
        )

    def get_candle_snapshot(
        self,
        product_symbol: str,
        interval: str,
        startTime: int,
        endTime: int,
    ) -> dict[str, Any]:
        """Get candlestick data for a product."""
        return self._native_public(
            "get_candle_snapshot",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_funding_rate_history(
        self,
        product_symbol: str,
        startTime: int,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get funding rate history for a product."""
        return self._native_public(
            "get_funding_rate_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_predicted_fundings(self) -> dict[str, Any] | list[Any]:
        """Get predicted funding rates across venues for the first perpetual DEX."""
        return self._native_public("get_predicted_fundings", [])

    def get_perps_at_open_interest_cap(self, *, dex: str | None = None) -> Any:
        """Query perpsAtOpenInterestCap using POST /info."""
        return self._native_public("get_perps_at_open_interest_cap", self._native_params(dex=dex))

    def get_perp_dex_limits(self, *, dex: str) -> Any:
        """Query perpDexLimits using POST /info."""
        return self._native_public("get_perp_dex_limits", self._native_params(dex=dex))

    def get_perp_dex_status(self, *, dex: str) -> Any:
        """Query perpDexStatus using POST /info. An empty dex selects the first perpetual DEX."""
        return self._native_public("get_perp_dex_status", self._native_params(dex=dex))

    def get_all_perp_metas(self) -> Any:
        """Query allPerpMetas using POST /info."""
        return self._native_public("get_all_perp_metas", self._native_params())

    def get_perp_annotation(self, *, product_symbol: str) -> Any:
        """Query perpAnnotation using POST /info."""
        return self._native_public(
            "get_perp_annotation", self._native_params(product_symbol=product_symbol)
        )

    def get_perp_categories(self) -> Any:
        """Query perpCategories using POST /info."""
        return self._native_public("get_perp_categories", self._native_params())

    def get_perp_concise_annotations(self) -> Any:
        """Query perpConciseAnnotations using POST /info."""
        return self._native_public("get_perp_concise_annotations", self._native_params())

    def get_token_details(self, *, token_id: str) -> Any:
        """Query tokenDetails using POST /info."""
        return self._native_public("get_token_details", self._native_params(tokenId=token_id))

    def get_borrow_lend_reserve_state(self, *, token: int) -> Any:
        """Query borrowLendReserveState using POST /info."""
        return self._native_public(
            "get_borrow_lend_reserve_state", self._native_params(token=token)
        )

    def get_all_borrow_lend_reserve_states(self) -> Any:
        """Query allBorrowLendReserveStates using POST /info."""
        return self._native_public("get_all_borrow_lend_reserve_states", self._native_params())
