from typing import Any, cast

from .._native_http import request_native_json
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp
from ._http_manager import HTTPManager
from .enums import BinanceProductType


class AccountHTTP(HTTPManager):
    """HTTP client for Binance account-related API endpoints."""

    def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Binance private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Binance native client is required for private account methods.")
        try:
            response, data = request_native_json(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"BINANCE {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if key == "self" or value is None:
                continue
            if isinstance(value, list):
                params.extend((key, str(item)) for item in value)
                continue
            if isinstance(value, bool):
                value = str(value).lower()
            params.append((key, str(value)))
        return params

    @staticmethod
    def _ensure_futures_listen_key(market_type: str) -> None:
        if str(market_type) == BinanceProductType.SPOT.value:
            raise NotImplementedError(
                "Binance Spot user data streams are subscribed through the WebSocket API."
            )

    def get_spot_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current Binance Spot maker and taker fee rates."""
        return self._native_private(
            "get_spot_fee_rates",
            self._params(product_symbol=product_symbol),
        )

    def get_futures_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current Binance Futures maker and taker fee rates."""
        return self._native_private(
            "get_futures_fee_rates",
            self._params(product_symbol=product_symbol),
        )

    def get_account_balance(
        self,
        market_type: str,
        omitZeroBalances: bool | None = None,
    ) -> dict:
        """
        Get account balance.

        Args:
            market_type: Market type ("spot" or "swap")

        Returns:
            dict: Account balance information
        """
        return self._native_private(
            "get_account_balance",
            self._params(
                market_type=str(market_type),
                omitZeroBalances=omitZeroBalances,
            ),
        )

    def get_income_history(
        self,
        product_symbol: str | None = None,
        incomeType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get futures income history.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            incomeType: Income type (TRANSFER, WELCOME_BONUS, REALIZED_PNL, FUNDING_FEE, etc.)
            startTime: Start time in milliseconds
            endTime: End time in milliseconds
            page: Page number for pagination
            limit: Number of records per page

        Returns:
            dict: Income history data
        """
        return self._native_private(
            "get_income_history",
            self._params(
                product_symbol=product_symbol,
                incomeType=incomeType,
                startTime=startTime,
                endTime=endTime,
                page=page,
                limit=limit,
            ),
        )

    def get_futures_account_info(self) -> dict:
        """
        Get futures account information, including balances and positions.

        Returns:
            dict: Futures account information.
        """
        return self._native_private("get_futures_account_info", [])

    def get_options_account_bill(
        self,
        currency: str,
        recordId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get Binance Options account funding flows."""
        return self._native_private(
            "get_options_account_bill",
            self._params(
                currency=currency,
                recordId=recordId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_options_margin_account(self) -> dict[str, Any]:
        """Get the Binance Options margin account state."""
        return self._native_private("get_options_margin_account", [])

    def create_options_listen_key(self) -> dict[str, Any]:
        """Start or renew a Binance Options user data stream."""
        return self._native_private("create_options_listen_key", [])

    def keep_alive_options_listen_key(self) -> dict[str, Any]:
        """Keep a Binance Options user data stream alive."""
        return self._native_private("keep_alive_options_listen_key", [])

    def close_options_listen_key(self) -> dict[str, Any]:
        """Close the active Binance Options user data stream."""
        return self._native_private("close_options_listen_key", [])

    def get_wallet_balance(
        self,
        quoteAsset: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get the estimated balance of every activated Binance wallet."""
        return cast(
            list[dict[str, Any]],
            self._native_private(
                "get_wallet_balance",
                self._params(quoteAsset=quoteAsset),
            ),
        )

    def get_funding_wallet(
        self,
        asset: str | None = None,
        needBtcValuation: bool | str | None = None,
    ) -> list[dict[str, Any]]:
        """Get assets held in the Binance Funding Wallet."""
        return cast(
            list[dict[str, Any]],
            self._native_private(
                "get_funding_wallet",
                self._params(asset=asset, needBtcValuation=needBtcValuation),
            ),
        )

    def create_universal_transfer(
        self,
        type_: str,
        asset: str,
        amount: str,
        fromSymbol: str | None = None,
        toSymbol: str | None = None,
    ) -> dict:
        """Transfer an asset between Binance account wallets."""
        return self._native_private(
            "create_universal_transfer",
            self._params(
                type=type_,
                asset=asset,
                amount=amount,
                fromSymbol=fromSymbol,
                toSymbol=toSymbol,
            ),
        )

    def get_universal_transfer_history(
        self,
        type_: str,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        size: int | None = None,
        fromSymbol: str | None = None,
        toSymbol: str | None = None,
    ) -> dict:
        """Get Binance universal transfer records."""
        return self._native_private(
            "get_universal_transfer_history",
            self._params(
                type=type_,
                startTime=startTime,
                endTime=endTime,
                current=current,
                size=size,
                fromSymbol=fromSymbol,
                toSymbol=toSymbol,
            ),
        )

    def get_listen_key(self, market_type: str = BinanceProductType.SWAP) -> str:
        """
        Start a futures user data stream and return its listen key.

        Args:
            market_type: Market type. Only "swap" is supported by this REST endpoint.

        Returns:
            str: User data stream listen key.
        """
        self._ensure_futures_listen_key(market_type)
        res = self._native_private("create_futures_listen_key", [])
        return res["listenKey"]

    def keep_alive_listen_key(
        self,
        listen_key: str,
        market_type: str = BinanceProductType.SWAP,
    ) -> dict:
        """
        Keep a futures user data stream alive.

        Args:
            listen_key: User data stream listen key.
            market_type: Market type. Only "swap" is supported by this REST endpoint.

        Returns:
            dict: Binance response.
        """
        self._ensure_futures_listen_key(market_type)
        return self._native_private(
            "keep_alive_futures_listen_key",
            self._params(listenKey=listen_key),
        )

    def close_listen_key(
        self,
        listen_key: str,
        market_type: str = BinanceProductType.SWAP,
    ) -> dict:
        """
        Close a futures user data stream.

        Args:
            listen_key: User data stream listen key.
            market_type: Market type. Only "swap" is supported by this REST endpoint.

        Returns:
            dict: Binance response.
        """
        self._ensure_futures_listen_key(market_type)
        return self._native_private(
            "close_futures_listen_key",
            self._params(listenKey=listen_key),
        )

    def get_all_margin_assets(self) -> list[dict[str, Any]]:
        """Return assets supported by Binance Margin."""
        return cast(list[dict[str, Any]], self._native_private("get_all_margin_assets", []))

    def get_all_cross_margin_pairs(self) -> list[dict[str, Any]]:
        """Return all cross-margin trading pairs."""
        return cast(list[dict[str, Any]], self._native_private("get_all_cross_margin_pairs", []))

    def get_all_isolated_margin_symbols(self) -> list[dict[str, Any]]:
        """Return all isolated-margin symbols."""
        return cast(
            list[dict[str, Any]],
            self._native_private("get_all_isolated_margin_symbols", []),
        )

    def get_margin_price_index(self, product_symbol: str) -> dict[str, Any]:
        """Return the margin price index for one symbol."""
        return self._native_private(
            "get_margin_price_index",
            self._params(product_symbol=product_symbol),
        )

    def get_cross_margin_account(self, recvWindow: int | None = None) -> dict[str, Any]:
        """Return cross-margin balances, liabilities, and risk levels."""
        return self._native_private(
            "get_cross_margin_account",
            self._params(recvWindow=recvWindow),
        )

    def get_isolated_margin_account(
        self,
        product_symbols: list[str] | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return isolated-margin balances and risk levels for up to five symbols."""
        return self._native_private(
            "get_isolated_margin_account",
            self._params(
                product_symbols=",".join(product_symbols) if product_symbols else None,
                recvWindow=recvWindow,
            ),
        )

    def margin_borrow_repay(
        self,
        asset: str,
        amount: str,
        type_: str,
        *,
        isIsolated: bool = False,
        product_symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Borrow or repay a cross- or isolated-margin liability."""
        return self._native_private(
            "margin_borrow_repay",
            self._params(
                asset=asset,
                amount=amount,
                type=type_,
                isIsolated=isIsolated,
                product_symbol=product_symbol,
                recvWindow=recvWindow,
            ),
        )

    def borrow_margin_asset(
        self,
        asset: str,
        amount: str,
        *,
        isIsolated: bool = False,
        product_symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Borrow an asset in a Binance Margin account."""
        return self.margin_borrow_repay(
            asset,
            amount,
            "BORROW",
            isIsolated=isIsolated,
            product_symbol=product_symbol,
            recvWindow=recvWindow,
        )

    def repay_margin_asset(
        self,
        asset: str,
        amount: str,
        *,
        isIsolated: bool = False,
        product_symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Repay an asset liability in a Binance Margin account."""
        return self.margin_borrow_repay(
            asset,
            amount,
            "REPAY",
            isIsolated=isIsolated,
            product_symbol=product_symbol,
            recvWindow=recvWindow,
        )

    def get_margin_borrow_repay_records(
        self,
        type_: str,
        *,
        asset: str | None = None,
        isolatedSymbol: str | None = None,
        txId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return Binance Margin borrow or repay records."""
        return self._native_private(
            "get_margin_borrow_repay_records",
            self._params(
                type=type_,
                asset=asset,
                isolatedSymbol=isolatedSymbol,
                txId=txId,
                startTime=startTime,
                endTime=endTime,
                current=current,
                size=size,
                recvWindow=recvWindow,
            ),
        )

    def get_margin_interest_history(
        self,
        *,
        asset: str | None = None,
        isolatedSymbol: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return accrued Binance Margin interest records."""
        return self._native_private(
            "get_margin_interest_history",
            self._params(
                asset=asset,
                isolatedSymbol=isolatedSymbol,
                startTime=startTime,
                endTime=endTime,
                current=current,
                size=size,
                recvWindow=recvWindow,
            ),
        )

    def get_margin_max_borrowable(
        self,
        asset: str,
        *,
        isolatedSymbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return the account's current maximum borrowable amount."""
        return self._native_private(
            "get_margin_max_borrowable",
            self._params(asset=asset, isolatedSymbol=isolatedSymbol, recvWindow=recvWindow),
        )

    def get_margin_max_transferable(
        self,
        asset: str,
        *,
        isolatedSymbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return the account's current maximum transferable amount."""
        return self._native_private(
            "get_margin_max_transferable",
            self._params(asset=asset, isolatedSymbol=isolatedSymbol, recvWindow=recvWindow),
        )

    def get_simple_earn_account(self, recvWindow: int | None = None) -> dict[str, Any]:
        """Return the Binance Simple Earn account summary."""
        return self._native_private(
            "get_simple_earn_account",
            self._params(recvWindow=recvWindow),
        )

    def get_flexible_earn_products(
        self,
        *,
        asset: str | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return available Simple Earn flexible products."""
        return self._native_private(
            "get_flexible_earn_products",
            self._params(asset=asset, current=current, size=size, recvWindow=recvWindow),
        )

    def get_locked_earn_products(
        self,
        *,
        asset: str | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return available Simple Earn locked products."""
        return self._native_private(
            "get_locked_earn_products",
            self._params(asset=asset, current=current, size=size, recvWindow=recvWindow),
        )

    def get_flexible_earn_positions(
        self,
        *,
        asset: str | None = None,
        productId: str | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return Simple Earn flexible positions."""
        return self._native_private(
            "get_flexible_earn_positions",
            self._params(
                asset=asset,
                productId=productId,
                current=current,
                size=size,
                recvWindow=recvWindow,
            ),
        )

    def get_locked_earn_positions(
        self,
        *,
        asset: str | None = None,
        positionId: str | None = None,
        projectId: str | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return Simple Earn locked positions."""
        return self._native_private(
            "get_locked_earn_positions",
            self._params(
                asset=asset,
                positionId=positionId,
                projectId=projectId,
                current=current,
                size=size,
                recvWindow=recvWindow,
            ),
        )

    def subscribe_flexible_earn(
        self,
        productId: str,
        amount: str,
        *,
        autoSubscribe: bool | None = None,
        sourceAccount: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Subscribe to a Simple Earn flexible product."""
        return self._native_private(
            "subscribe_flexible_earn",
            self._params(
                productId=productId,
                amount=amount,
                autoSubscribe=autoSubscribe,
                sourceAccount=sourceAccount,
                recvWindow=recvWindow,
            ),
        )

    def subscribe_locked_earn(
        self,
        projectId: str,
        amount: str,
        *,
        autoSubscribe: bool | None = None,
        sourceAccount: str | None = None,
        redeemTo: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Subscribe to a Simple Earn locked product."""
        return self._native_private(
            "subscribe_locked_earn",
            self._params(
                projectId=projectId,
                amount=amount,
                autoSubscribe=autoSubscribe,
                sourceAccount=sourceAccount,
                redeemTo=redeemTo,
                recvWindow=recvWindow,
            ),
        )

    def redeem_flexible_earn(
        self,
        productId: str,
        *,
        amount: str | None = None,
        redeemAll: bool = False,
        destAccount: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Redeem all or part of a Simple Earn flexible position."""
        return self._native_private(
            "redeem_flexible_earn",
            self._params(
                productId=productId,
                amount=amount,
                redeemAll=redeemAll,
                destAccount=destAccount,
                recvWindow=recvWindow,
            ),
        )

    def redeem_locked_earn(
        self,
        positionId: str,
        *,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Redeem one Simple Earn locked position."""
        return self._native_private(
            "redeem_locked_earn",
            self._params(positionId=positionId, recvWindow=recvWindow),
        )

    def get_flexible_earn_subscription_history(
        self,
        *,
        productId: str | None = None,
        purchaseId: str | None = None,
        asset: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return flexible-product subscription history."""
        return self._native_private(
            "get_flexible_earn_subscription_history",
            self._params(**{key: value for key, value in locals().items() if key != "self"}),
        )

    def get_locked_earn_subscription_history(
        self,
        *,
        purchaseId: str | None = None,
        asset: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return locked-product subscription history."""
        return self._native_private(
            "get_locked_earn_subscription_history",
            self._params(**{key: value for key, value in locals().items() if key != "self"}),
        )

    def get_flexible_earn_redemption_history(
        self,
        *,
        productId: str | None = None,
        redeemId: str | None = None,
        asset: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return flexible-product redemption history."""
        return self._native_private(
            "get_flexible_earn_redemption_history",
            self._params(**{key: value for key, value in locals().items() if key != "self"}),
        )

    def get_locked_earn_redemption_history(
        self,
        *,
        positionId: str | None = None,
        redeemId: str | None = None,
        asset: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return locked-product redemption history."""
        return self._native_private(
            "get_locked_earn_redemption_history",
            self._params(**{key: value for key, value in locals().items() if key != "self"}),
        )

    def get_flexible_earn_rewards_history(
        self,
        *,
        productId: str | None = None,
        asset: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        type_: str | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return flexible-product reward history."""
        params = self._params(**{key: value for key, value in locals().items() if key != "self"})
        params = [("type" if key == "type_" else key, value) for key, value in params]
        return self._native_private("get_flexible_earn_rewards_history", params)

    def get_locked_earn_rewards_history(
        self,
        *,
        positionId: str | None = None,
        asset: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return locked-product reward history."""
        return self._native_private(
            "get_locked_earn_rewards_history",
            self._params(**{key: value for key, value in locals().items() if key != "self"}),
        )

    def check_flexible_loan_collateral_repay_rate(
        self,
        loanCoin: str,
        collateralCoin: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return the collateral-to-loan conversion rate used for repayment."""
        return self._native_private(
            "check_flexible_loan_collateral_repay_rate",
            self._params(loanCoin=loanCoin, collateralCoin=collateralCoin, recvWindow=recvWindow),
        )

    def adjust_flexible_loan_ltv(
        self,
        loanCoin: str,
        collateralCoin: str,
        adjustmentAmount: str,
        direction: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Add or remove collateral from a Binance Flexible Loan."""
        return self._native_private(
            "adjust_flexible_loan_ltv",
            self._params(**{key: value for key, value in locals().items() if key != "self"}),
        )

    def borrow_flexible_loan(
        self,
        loanCoin: str,
        collateralCoin: str,
        *,
        loanAmount: str | None = None,
        collateralAmount: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Borrow a Flexible Loan using either a loan or collateral amount."""
        return self._native_private(
            "borrow_flexible_loan",
            self._params(**{key: value for key, value in locals().items() if key != "self"}),
        )

    def repay_flexible_loan(
        self,
        loanCoin: str,
        collateralCoin: str,
        repayAmount: str,
        *,
        collateralReturn: bool | None = None,
        fullRepayment: bool | None = None,
        repaymentType: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Repay a Binance Flexible Loan."""
        return self._native_private(
            "repay_flexible_loan",
            self._params(**{key: value for key, value in locals().items() if key != "self"}),
        )

    def get_flexible_loan_assets(
        self,
        loanCoin: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return Flexible Loan interest rates and borrowing limits."""
        return self._native_private(
            "get_flexible_loan_assets",
            self._params(loanCoin=loanCoin, recvWindow=recvWindow),
        )

    def get_flexible_loan_collateral_assets(
        self,
        collateralCoin: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return Flexible Loan collateral limits and LTV data."""
        return self._native_private(
            "get_flexible_loan_collateral_assets",
            self._params(collateralCoin=collateralCoin, recvWindow=recvWindow),
        )

    def get_flexible_loan_interest_rate_history(
        self,
        coin: str,
        *,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return Flexible Loan interest-rate history."""
        return self._native_private(
            "get_flexible_loan_interest_rate_history",
            self._params(**{key: value for key, value in locals().items() if key != "self"}),
        )

    def get_flexible_loan_ongoing_orders(
        self,
        *,
        loanCoin: str | None = None,
        collateralCoin: str | None = None,
        current: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return active Flexible Loan positions."""
        return self._native_private(
            "get_flexible_loan_ongoing_orders",
            self._params(**{key: value for key, value in locals().items() if key != "self"}),
        )

    def _get_flexible_loan_history(
        self,
        method_name: str,
        *,
        loanCoin: str | None = None,
        collateralCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            method_name,
            self._params(
                loanCoin=loanCoin,
                collateralCoin=collateralCoin,
                startTime=startTime,
                endTime=endTime,
                current=current,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    def get_flexible_loan_borrow_history(
        self,
        *,
        loanCoin: str | None = None,
        collateralCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return Flexible Loan borrowing history."""
        return self._get_flexible_loan_history(
            "get_flexible_loan_borrow_history",
            loanCoin=loanCoin,
            collateralCoin=collateralCoin,
            startTime=startTime,
            endTime=endTime,
            current=current,
            limit=limit,
            recvWindow=recvWindow,
        )

    def get_flexible_loan_repayment_history(
        self,
        *,
        loanCoin: str | None = None,
        collateralCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return Flexible Loan repayment history."""
        return self._get_flexible_loan_history(
            "get_flexible_loan_repayment_history",
            loanCoin=loanCoin,
            collateralCoin=collateralCoin,
            startTime=startTime,
            endTime=endTime,
            current=current,
            limit=limit,
            recvWindow=recvWindow,
        )

    def get_flexible_loan_ltv_adjustment_history(
        self,
        *,
        loanCoin: str | None = None,
        collateralCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return Flexible Loan LTV-adjustment history."""
        return self._get_flexible_loan_history(
            "get_flexible_loan_ltv_adjustment_history",
            loanCoin=loanCoin,
            collateralCoin=collateralCoin,
            startTime=startTime,
            endTime=endTime,
            current=current,
            limit=limit,
            recvWindow=recvWindow,
        )

    def get_flexible_loan_liquidation_history(
        self,
        *,
        loanCoin: str | None = None,
        collateralCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return Flexible Loan liquidation history."""
        return self._get_flexible_loan_history(
            "get_flexible_loan_liquidation_history",
            loanCoin=loanCoin,
            collateralCoin=collateralCoin,
            startTime=startTime,
            endTime=endTime,
            current=current,
            limit=limit,
            recvWindow=recvWindow,
        )

    def get_crypto_loan_income_history(
        self,
        *,
        asset: str | None = None,
        type_: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return legacy Crypto Loan income history."""
        params = self._params(**{key: value for key, value in locals().items() if key != "self"})
        params = [("type" if key == "type_" else key, value) for key, value in params]
        return self._native_private("get_crypto_loan_income_history", params)

    def _get_stable_loan_history(
        self,
        method_name: str,
        *,
        orderId: int | None = None,
        loanCoin: str | None = None,
        collateralCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            method_name,
            self._params(
                orderId=orderId,
                loanCoin=loanCoin,
                collateralCoin=collateralCoin,
                startTime=startTime,
                endTime=endTime,
                current=current,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    def get_stable_loan_borrow_history(
        self,
        *,
        orderId: int | None = None,
        loanCoin: str | None = None,
        collateralCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return legacy stable-rate loan borrowing history."""
        return self._get_stable_loan_history(
            "get_stable_loan_borrow_history",
            orderId=orderId,
            loanCoin=loanCoin,
            collateralCoin=collateralCoin,
            startTime=startTime,
            endTime=endTime,
            current=current,
            limit=limit,
            recvWindow=recvWindow,
        )

    def get_stable_loan_repayment_history(
        self,
        *,
        orderId: int | None = None,
        loanCoin: str | None = None,
        collateralCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return legacy stable-rate loan repayment history."""
        return self._get_stable_loan_history(
            "get_stable_loan_repayment_history",
            orderId=orderId,
            loanCoin=loanCoin,
            collateralCoin=collateralCoin,
            startTime=startTime,
            endTime=endTime,
            current=current,
            limit=limit,
            recvWindow=recvWindow,
        )

    def get_stable_loan_ltv_adjustment_history(
        self,
        *,
        orderId: int | None = None,
        loanCoin: str | None = None,
        collateralCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return legacy stable-rate loan LTV-adjustment history."""
        return self._get_stable_loan_history(
            "get_stable_loan_ltv_adjustment_history",
            orderId=orderId,
            loanCoin=loanCoin,
            collateralCoin=collateralCoin,
            startTime=startTime,
            endTime=endTime,
            current=current,
            limit=limit,
            recvWindow=recvWindow,
        )

    def _staking_query(self, method_name: str, **params: object) -> dict[str, Any]:
        return self._native_private(method_name, self._params(**params))

    def get_eth_staking_account(self, recvWindow: int | None = None) -> dict[str, Any]:
        """Return ETH staking balances and recent earnings."""
        return self._staking_query("get_eth_staking_account", recvWindow=recvWindow)

    def get_eth_staking_quota(self, recvWindow: int | None = None) -> dict[str, Any]:
        """Return ETH staking and redemption quota details."""
        return self._staking_query("get_eth_staking_quota", recvWindow=recvWindow)

    def get_eth_redemption_history(self, **params: object) -> dict[str, Any]:
        """Return ETH staking redemption history."""
        return self._staking_query("get_eth_redemption_history", **params)

    def get_eth_staking_history(self, **params: object) -> dict[str, Any]:
        """Return ETH staking subscription history."""
        return self._staking_query("get_eth_staking_history", **params)

    def get_wbeth_rate_history(self, **params: object) -> dict[str, Any]:
        """Return WBETH conversion-rate history."""
        return self._staking_query("get_wbeth_rate_history", **params)

    def get_wbeth_rewards_history(self, **params: object) -> dict[str, Any]:
        """Return WBETH reward history."""
        return self._staking_query("get_wbeth_rewards_history", **params)

    def get_wbeth_unwrap_history(self, **params: object) -> dict[str, Any]:
        """Return WBETH unwrap history."""
        return self._staking_query("get_wbeth_unwrap_history", **params)

    def get_wbeth_wrap_history(self, **params: object) -> dict[str, Any]:
        """Return WBETH wrap history."""
        return self._staking_query("get_wbeth_wrap_history", **params)

    def subscribe_eth_staking(self, amount: str, recvWindow: int | None = None) -> dict[str, Any]:
        """Stake ETH and receive WBETH."""
        return self._staking_query("subscribe_eth_staking", amount=amount, recvWindow=recvWindow)

    def redeem_eth_staking(
        self,
        amount: str,
        *,
        asset: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Redeem WBETH or BETH for ETH."""
        return self._staking_query(
            "redeem_eth_staking", amount=amount, asset=asset, recvWindow=recvWindow
        )

    def wrap_beth(self, amount: str, recvWindow: int | None = None) -> dict[str, Any]:
        """Wrap BETH into WBETH."""
        return self._staking_query("wrap_beth", amount=amount, recvWindow=recvWindow)

    def get_onchain_yields_personal_quota(
        self, projectId: str, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Return the remaining quota for an On-chain Yields product."""
        return self._staking_query(
            "get_onchain_yields_personal_quota",
            projectId=projectId,
            recvWindow=recvWindow,
        )

    def get_onchain_yields_products(self, **params: object) -> dict[str, Any]:
        """Return available locked On-chain Yields products."""
        return self._staking_query("get_onchain_yields_products", **params)

    def get_onchain_yields_positions(self, **params: object) -> dict[str, Any]:
        """Return locked On-chain Yields positions."""
        return self._staking_query("get_onchain_yields_positions", **params)

    def get_onchain_yields_redemption_history(self, **params: object) -> dict[str, Any]:
        """Return On-chain Yields redemption history."""
        return self._staking_query("get_onchain_yields_redemption_history", **params)

    def get_onchain_yields_rewards_history(self, **params: object) -> dict[str, Any]:
        """Return On-chain Yields reward history."""
        return self._staking_query("get_onchain_yields_rewards_history", **params)

    def preview_onchain_yields_subscription(
        self,
        projectId: str,
        amount: str,
        *,
        autoSubscribe: bool | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Preview an On-chain Yields subscription."""
        return self._staking_query(
            "preview_onchain_yields_subscription",
            projectId=projectId,
            amount=amount,
            autoSubscribe=autoSubscribe,
            recvWindow=recvWindow,
        )

    def get_onchain_yields_subscription_history(self, **params: object) -> dict[str, Any]:
        """Return On-chain Yields subscription history."""
        return self._staking_query("get_onchain_yields_subscription_history", **params)

    def get_onchain_yields_account(self, recvWindow: int | None = None) -> dict[str, Any]:
        """Return the On-chain Yields account summary."""
        return self._staking_query("get_onchain_yields_account", recvWindow=recvWindow)

    def subscribe_onchain_yields(
        self,
        projectId: str,
        amount: str,
        *,
        autoSubscribe: bool | None = None,
        sourceAccount: str | None = None,
        redeemTo: str | None = None,
        channelId: str | None = None,
        clientId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Subscribe to a locked On-chain Yields product."""
        return self._staking_query(
            "subscribe_onchain_yields",
            **{key: value for key, value in locals().items() if key != "self"},
        )

    def redeem_onchain_yields(
        self,
        positionId: str,
        *,
        channelId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Redeem a locked On-chain Yields position."""
        return self._staking_query(
            "redeem_onchain_yields",
            positionId=positionId,
            channelId=channelId,
            recvWindow=recvWindow,
        )

    def set_onchain_yields_auto_subscribe(
        self,
        positionId: str,
        autoSubscribe: bool,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Enable or disable automatic On-chain Yields resubscription."""
        return self._staking_query(
            "set_onchain_yields_auto_subscribe",
            positionId=positionId,
            autoSubscribe=autoSubscribe,
            recvWindow=recvWindow,
        )

    def set_onchain_yields_redeem_option(
        self,
        positionId: str,
        redeemTo: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Set the redemption destination for an On-chain Yields position."""
        return self._staking_query(
            "set_onchain_yields_redeem_option",
            positionId=positionId,
            redeemTo=redeemTo,
            recvWindow=recvWindow,
        )

    def get_soft_staking_products(self, **params: object) -> dict[str, Any]:
        """Return available Soft Staking products."""
        return self._staking_query("get_soft_staking_products", **params)

    def get_soft_staking_rewards_history(self, **params: object) -> dict[str, Any]:
        """Return Soft Staking reward history."""
        return self._staking_query("get_soft_staking_rewards_history", **params)

    def set_soft_staking(self, softStaking: bool, recvWindow: int | None = None) -> dict[str, Any]:
        """Enable or disable Soft Staking."""
        return self._staking_query(
            "set_soft_staking", softStaking=softStaking, recvWindow=recvWindow
        )

    def get_sol_staking_account(self, recvWindow: int | None = None) -> dict[str, Any]:
        """Return SOL staking balances and earnings."""
        return self._staking_query("get_sol_staking_account", recvWindow=recvWindow)

    def get_sol_staking_quota(self, recvWindow: int | None = None) -> dict[str, Any]:
        """Return SOL staking quota details."""
        return self._staking_query("get_sol_staking_quota", recvWindow=recvWindow)

    def get_bnsol_rate_history(self, **params: object) -> dict[str, Any]:
        """Return BNSOL conversion-rate history."""
        return self._staking_query("get_bnsol_rate_history", **params)

    def get_bnsol_rewards_history(self, **params: object) -> dict[str, Any]:
        """Return BNSOL reward history."""
        return self._staking_query("get_bnsol_rewards_history", **params)

    def get_sol_boost_rewards_history(self, **params: object) -> dict[str, Any]:
        """Return SOL staking Boost reward history."""
        return self._staking_query("get_sol_boost_rewards_history", **params)

    def get_sol_redemption_history(self, **params: object) -> dict[str, Any]:
        """Return SOL staking redemption history."""
        return self._staking_query("get_sol_redemption_history", **params)

    def get_sol_staking_history(self, **params: object) -> dict[str, Any]:
        """Return SOL staking subscription history."""
        return self._staking_query("get_sol_staking_history", **params)

    def get_sol_unclaimed_rewards(self, recvWindow: int | None = None) -> dict[str, Any]:
        """Return unclaimed SOL Boost rewards."""
        return self._staking_query("get_sol_unclaimed_rewards", recvWindow=recvWindow)

    def claim_sol_boost_rewards(self, recvWindow: int | None = None) -> dict[str, Any]:
        """Claim SOL Boost rewards."""
        return self._staking_query("claim_sol_boost_rewards", recvWindow=recvWindow)

    def subscribe_sol_staking(self, amount: str, recvWindow: int | None = None) -> dict[str, Any]:
        """Stake SOL and receive BNSOL."""
        return self._staking_query("subscribe_sol_staking", amount=amount, recvWindow=recvWindow)

    def redeem_sol_staking(self, amount: str, recvWindow: int | None = None) -> dict[str, Any]:
        """Redeem BNSOL for SOL."""
        return self._staking_query("redeem_sol_staking", amount=amount, recvWindow=recvWindow)

    def _subaccount_query(self, method_name: str, **params: object) -> dict[str, Any]:
        return self._native_private(method_name, self._params(**params))

    def get_subaccounts(
        self,
        *,
        email: str | None = None,
        isFreeze: bool | None = None,
        page: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return the master account's standard sub-accounts."""
        return self._subaccount_query(
            "get_subaccounts",
            email=email,
            isFreeze=isFreeze,
            page=page,
            limit=limit,
            recvWindow=recvWindow,
        )

    def get_subaccount_status(
        self, email: str | None = None, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Return margin and futures status for sub-accounts."""
        return self._subaccount_query("get_subaccount_status", email=email, recvWindow=recvWindow)

    def get_subaccount_transaction_statistics(
        self, email: str, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Return transaction statistics for one sub-account."""
        return self._subaccount_query(
            "get_subaccount_transaction_statistics", email=email, recvWindow=recvWindow
        )

    def get_subaccount_futures_position_risk(
        self,
        email: str,
        futuresType: int = 1,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return futures position risk for one sub-account."""
        return self._subaccount_query(
            "get_subaccount_futures_position_risk",
            email=email,
            futuresType=futuresType,
            recvWindow=recvWindow,
        )

    def get_subaccount_futures_account(
        self,
        email: str,
        futuresType: int = 1,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return futures account details for one sub-account."""
        return self._subaccount_query(
            "get_subaccount_futures_account",
            email=email,
            futuresType=futuresType,
            recvWindow=recvWindow,
        )

    def get_subaccount_margin_account(
        self, email: str, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Return margin account details for one sub-account."""
        return self._subaccount_query(
            "get_subaccount_margin_account", email=email, recvWindow=recvWindow
        )

    def get_subaccount_futures_summary(
        self,
        futuresType: int = 1,
        *,
        page: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return the master account's sub-account futures summary."""
        return self._subaccount_query(
            "get_subaccount_futures_summary",
            futuresType=futuresType,
            page=page,
            limit=limit,
            recvWindow=recvWindow,
        )

    def get_subaccount_margin_summary(self, recvWindow: int | None = None) -> dict[str, Any]:
        """Return the master account's sub-account margin summary."""
        return self._subaccount_query("get_subaccount_margin_summary", recvWindow=recvWindow)

    def get_subaccount_assets(self, email: str, recvWindow: int | None = None) -> dict[str, Any]:
        """Return all assets for one sub-account."""
        return self._subaccount_query("get_subaccount_assets", email=email, recvWindow=recvWindow)

    def get_subaccount_spot_summary(
        self,
        *,
        email: str | None = None,
        page: int | None = None,
        size: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Return BTC-valued spot assets for sub-accounts."""
        return self._subaccount_query(
            "get_subaccount_spot_summary",
            email=email,
            page=page,
            size=size,
            recvWindow=recvWindow,
        )

    def transfer_subaccount_futures(
        self,
        email: str,
        asset: str,
        amount: str,
        type_: int,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Transfer between a sub-account's spot and futures wallets."""
        return self._native_private(
            "transfer_subaccount_futures",
            self._params(
                email=email,
                asset=asset,
                amount=amount,
                type=type_,
                recvWindow=recvWindow,
            ),
        )

    def transfer_subaccount_margin(
        self,
        email: str,
        asset: str,
        amount: str,
        type_: int,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Transfer between a sub-account's spot and margin wallets."""
        return self._native_private(
            "transfer_subaccount_margin",
            self._params(
                email=email,
                asset=asset,
                amount=amount,
                type=type_,
                recvWindow=recvWindow,
            ),
        )

    def get_subaccount_futures_transfer_history(
        self,
        email: str,
        futuresType: int = 1,
        **params: object,
    ) -> dict[str, Any]:
        """Return transfers between sub-account futures wallets."""
        return self._subaccount_query(
            "get_subaccount_futures_transfer_history",
            email=email,
            futuresType=futuresType,
            **params,
        )

    def transfer_between_subaccount_futures(
        self,
        fromEmail: str,
        toEmail: str,
        futuresType: int,
        asset: str,
        amount: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Transfer futures assets between accounts under the same master."""
        return self._subaccount_query(
            "transfer_between_subaccount_futures",
            fromEmail=fromEmail,
            toEmail=toEmail,
            futuresType=futuresType,
            asset=asset,
            amount=amount,
            recvWindow=recvWindow,
        )

    def get_subaccount_spot_transfer_history(self, **params: object) -> dict[str, Any]:
        """Return spot transfers between accounts under the same master."""
        return self._subaccount_query("get_subaccount_spot_transfer_history", **params)

    def get_subaccount_universal_transfer_history(self, **params: object) -> dict[str, Any]:
        """Return universal transfers between accounts under the same master."""
        return self._subaccount_query("get_subaccount_universal_transfer_history", **params)

    def transfer_between_subaccounts(
        self,
        fromAccountType: str,
        toAccountType: str,
        asset: str,
        amount: str,
        *,
        fromEmail: str | None = None,
        toEmail: str | None = None,
        clientTranId: str | None = None,
        symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Universally transfer assets within one Binance master-account tree."""
        return self._subaccount_query(
            "transfer_between_subaccounts",
            **{key: value for key, value in locals().items() if key != "self"},
        )

    def get_subaccount_transfer_history(self, **params: object) -> dict[str, Any]:
        """Return transfer history when authenticated as a sub-account."""
        return self._subaccount_query("get_subaccount_transfer_history", **params)

    def transfer_subaccount_to_master(
        self, asset: str, amount: str, recvWindow: int | None = None
    ) -> dict[str, Any]:
        """Transfer assets from a sub-account to its master account."""
        return self._subaccount_query(
            "transfer_subaccount_to_master",
            asset=asset,
            amount=amount,
            recvWindow=recvWindow,
        )

    def transfer_subaccount_to_subaccount(
        self,
        toEmail: str,
        asset: str,
        amount: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Transfer assets to a sibling sub-account under the same master."""
        return self._subaccount_query(
            "transfer_subaccount_to_subaccount",
            toEmail=toEmail,
            asset=asset,
            amount=amount,
            recvWindow=recvWindow,
        )
