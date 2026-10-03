"""Bitget private account async HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager
from ._transfers_http import AccountHTTPTransfersHTTP


class AccountHTTP(AccountHTTPTransfersHTTP, HTTPManager):
    """Async HTTP client for Bitget private account operations."""

    async def get_spot_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current Bitget Spot maker and taker fee rates."""
        return await self._native_private(
            "get_spot_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_futures_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current Bitget Futures maker and taker fee rates."""
        return await self._native_private(
            "get_futures_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_all_account_balance(self) -> dict[str, Any]:
        """Retrieve Bitget all-account balance overview."""
        return await self._native_private("get_all_account_balance", [])

    async def get_funding_assets(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget funding account assets."""
        return await self._native_private("get_funding_assets", self._native_params(coin=coin))

    async def get_deposit_records(
        self,
        start_time: int | str,
        end_time: int | str,
        coin: str | None = None,
        order_id: str | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget deposit records."""
        return await self._native_private(
            "get_deposit_records",
            self._native_params(
                coin=coin,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                idLessThan=id_less_than,
                limit=limit,
            ),
        )

    async def get_uta_account_assets(self) -> dict[str, Any]:
        """Retrieve Bitget UTA account assets."""
        return await self._native_private("get_uta_account_assets", [])

    async def get_reality_orderbook(self, product_symbol: str) -> dict[str, Any]:
        """Return Reality raw-depth snapshot (requires Bitget whitelist)."""
        return await self._native_private(
            "get_reality_orderbook", self._native_params(product_symbol=product_symbol)
        )

    async def get_reality_fills(
        self, product_symbol: str, limit: int | None = None
    ) -> dict[str, Any]:
        """Return recent Reality platform fills (requires Bitget whitelist)."""
        return await self._native_private(
            "get_reality_fills", self._native_params(product_symbol=product_symbol, limit=limit)
        )

    async def get_uta_account_info(self) -> dict[str, Any]:
        """Retrieve Bitget UTA API account information."""
        return await self._native_private("get_uta_account_info", [])

    async def set_uta_leverage(
        self,
        category: str,
        leverage: str | int,
        product_symbol: str | None = None,
        symbol: str | None = None,
        coin: str | None = None,
        pos_side: str | None = None,
        margin_mode: str | None = None,
        long_leverage: str | int | None = None,
        short_leverage: str | int | None = None,
    ) -> dict[str, Any]:
        """Set Bitget UTA leverage."""
        return await self._native_private(
            "set_uta_leverage",
            self._native_params(
                category=category,
                leverage=leverage,
                product_symbol=product_symbol,
                symbol=symbol,
                coin=coin,
                posSide=pos_side,
                marginMode=margin_mode,
                longLeverage=long_leverage,
                shortLeverage=short_leverage,
            ),
        )

    async def set_uta_hold_mode(self, hold_mode: str) -> dict[str, Any]:
        """Set Bitget UTA holding mode."""
        return await self._native_private(
            "set_uta_hold_mode",
            self._native_params(holdMode=hold_mode),
        )

    async def set_futures_margin_mode(
        self,
        product_symbol: str,
        margin_mode: str,
        margin_coin: str = "USDT",
        product_type: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Set Bitget futures margin mode."""
        return await self._native_private(
            "set_futures_margin_mode",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
                marginMode=margin_mode,
            ),
        )

    async def get_uta_all_fee_rates(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve UTA fee rates for every pair in one product category."""
        return await self._native_private(
            "get_uta_all_fee_rates",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
            ),
        )

    async def get_uta_loan_data(self) -> dict[str, Any]:
        """Retrieve current UTA borrowing and interest data."""
        return await self._native_private("get_uta_loan_data", [])

    async def get_crypto_loan_coins(self, coin: str | None = None) -> dict[str, Any]:
        """Get supported Crypto Loan assets, limits, rates, and collateral ratios."""
        return await self._native_private("get_crypto_loan_coins", self._native_params(coin=coin))

    async def get_crypto_loan_interest(
        self,
        loan_coin: str,
        pledge_coin: str,
        daily: str,
        pledge_amount: str,
    ) -> dict[str, Any]:
        """Estimate Crypto Loan interest and borrowable amount."""
        return await self._native_private(
            "get_crypto_loan_interest",
            self._native_params(
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                daily=daily,
                pledgeAmount=pledge_amount,
            ),
        )

    async def borrow_crypto_loan(
        self,
        loan_coin: str,
        pledge_coin: str,
        daily: str,
        pledge_amount: str | None = None,
        loan_amount: str | None = None,
    ) -> dict[str, Any]:
        """Borrow using exactly one of collateral amount or desired loan amount."""
        if (pledge_amount is None) == (loan_amount is None):
            raise ValueError("Specify exactly one of pledgeAmount or loanAmount.")
        return await self._native_private(
            "borrow_crypto_loan",
            self._native_params(
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                daily=daily,
                pledgeAmount=pledge_amount,
                loanAmount=loan_amount,
            ),
        )

    async def get_crypto_loan_ongoing(
        self,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
    ) -> dict[str, Any]:
        """Get current Crypto Loan orders and accrued interest."""
        return await self._native_private(
            "get_crypto_loan_ongoing",
            self._native_params(orderId=order_id, loanCoin=loan_coin, pledgeCoin=pledge_coin),
        )

    async def get_crypto_loan_borrow_history(
        self,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
        status: str | None = None,
        page_num: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """Get Crypto Loan borrow history from the last three months."""
        return await self._native_private(
            "get_crypto_loan_borrow_history",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                status=status,
                pageNum=page_num,
                pageSize=page_size,
            ),
        )

    async def repay_crypto_loan(
        self,
        order_id: str,
        repay_all: str,
        amount: str | None = None,
        repay_unlock: str | None = None,
    ) -> dict[str, Any]:
        """Repay part or all of a Crypto Loan."""
        return await self._native_private(
            "repay_crypto_loan",
            self._native_params(
                orderId=order_id,
                repayAll=repay_all,
                amount=amount,
                repayUnlock=repay_unlock,
            ),
        )

    async def get_crypto_loan_repay_history(
        self,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
        page_num: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """Get Crypto Loan repayment history from the last three months."""
        return await self._native_private(
            "get_crypto_loan_repay_history",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                pageNum=page_num,
                pageSize=page_size,
            ),
        )

    async def revise_crypto_loan_pledge(
        self, order_id: str, amount: str, pledge_coin: str, revise_type: str
    ) -> dict[str, Any]:
        """Add or withdraw collateral for a Crypto Loan."""
        return await self._native_private(
            "revise_crypto_loan_pledge",
            self._native_params(
                orderId=order_id,
                amount=amount,
                pledgeCoin=pledge_coin,
                reviseType=revise_type,
            ),
        )

    async def get_crypto_loan_pledge_history(
        self,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        revise_side: str | None = None,
        pledge_coin: str | None = None,
        page_num: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """Get Crypto Loan collateral-ratio adjustment history."""
        return await self._native_private(
            "get_crypto_loan_pledge_history",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                reviseSide=revise_side,
                pledgeCoin=pledge_coin,
                pageNum=page_num,
                pageSize=page_size,
            ),
        )

    async def get_crypto_loan_liquidations(
        self,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
        status: str | None = None,
        page_num: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """Get Crypto Loan liquidation records."""
        return await self._native_private(
            "get_crypto_loan_liquidations",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                status=status,
                pageNum=page_num,
                pageSize=page_size,
            ),
        )

    async def get_crypto_loan_debts(self) -> dict[str, Any]:
        """Get Crypto Loan liabilities and collateral assets."""
        return await self._native_private("get_crypto_loan_debts", [])

    async def repay_uta_liability(
        self, repayable_coin_list: list[str], payment_coin_list: list[str]
    ) -> dict[str, Any]:
        """Repay UTA liabilities with selected repayment and payment assets."""
        return await self._native_private(
            "repay_uta_liability",
            self._native_params(
                repayableCoinList=repayable_coin_list,
                paymentCoinList=payment_coin_list,
            ),
        )

    async def get_uta_collateral_type(self) -> dict[str, Any]:
        """Retrieve the UTA collateral-type configuration."""
        return await self._native_private("get_uta_collateral_type", [])

    async def get_uta_custom_collateral_coins(self) -> dict[str, Any]:
        """Retrieve coins supported as custom UTA collateral."""
        return await self._native_private("get_uta_custom_collateral_coins", [])

    async def get_uta_pre_set_leverage(
        self,
        category: str,
        margin_mode: str,
        product_symbol: str | None = None,
        coin: str | None = None,
        leverage: str | int | None = None,
        long_leverage: str | int | None = None,
        short_leverage: str | int | None = None,
    ) -> dict[str, Any]:
        """Preview UTA margin and maximum tradable size after a leverage change."""
        return await self._native_private(
            "get_uta_pre_set_leverage",
            self._native_params(
                category=category,
                marginMode=margin_mode,
                product_symbol=product_symbol,
                coin=coin,
                leverage=leverage,
                longLeverage=long_leverage,
                shortLeverage=short_leverage,
            ),
        )
