"""Bitget private account HTTP client backed by Rust."""

from typing import Any

from dcex._keyword_aliases import legacy_keywords

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for Bitget private account operations."""

    def get_spot_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current Bitget Spot maker and taker fee rates."""
        return self._native_private(
            "get_spot_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    def get_futures_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current Bitget Futures maker and taker fee rates."""
        return self._native_private(
            "get_futures_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    def get_all_account_balance(self) -> dict[str, Any]:
        """Retrieve Bitget all-account balance overview."""
        return self._native_private("get_all_account_balance", [])

    def get_funding_assets(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget funding account assets."""
        return self._native_private("get_funding_assets", self._native_params(coin=coin))

    def get_spot_account_info(self) -> dict[str, Any]:
        """Retrieve Bitget spot account information."""
        return self._native_private("get_spot_account_info", [])

    @legacy_keywords({"assetType": "asset_type"})
    def get_spot_account_assets(
        self,
        coin: str | None = None,
        asset_type: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot account assets."""
        return self._native_private(
            "get_spot_account_assets",
            self._native_params(coin=coin, assetType=asset_type),
        )

    @legacy_keywords(
        {
            "groupType": "group_type",
            "businessType": "business_type",
            "startTime": "start_time",
            "endTime": "end_time",
            "idLessThan": "id_less_than",
        }
    )
    def get_spot_account_bills(
        self,
        coin: str | None = None,
        group_type: str | None = None,
        business_type: str | None = None,
        start_time: int | str | None = None,
        end_time: int | str | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot account bills."""
        return self._native_private(
            "get_spot_account_bills",
            self._native_params(
                coin=coin,
                groupType=group_type,
                businessType=business_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    @legacy_keywords({"fromType": "from_type", "toType": "to_type", "clientOid": "client_oid"})
    def transfer(
        self,
        coin: str,
        amount: str,
        from_type: str,
        to_type: str,
        symbol: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Transfer assets between Bitget account types."""
        return self._native_private(
            "transfer",
            self._native_params(
                coin=coin,
                amount=amount,
                fromType=from_type,
                toType=to_type,
                symbol=symbol,
                clientOid=client_oid,
            ),
        )

    @legacy_keywords(
        {
            "fromType": "from_type",
            "startTime": "start_time",
            "endTime": "end_time",
            "clientOid": "client_oid",
            "pageNum": "page_num",
            "idLessThan": "id_less_than",
        }
    )
    def get_transfer_records(
        self,
        coin: str,
        from_type: str | None = None,
        start_time: int | str | None = None,
        end_time: int | str | None = None,
        client_oid: str | None = None,
        page_num: int | str | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget account transfer records."""
        return self._native_private(
            "get_transfer_records",
            self._native_params(
                coin=coin,
                fromType=from_type,
                startTime=start_time,
                endTime=end_time,
                clientOid=client_oid,
                pageNum=page_num,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    @legacy_keywords({"fromType": "from_type", "toType": "to_type"})
    def get_transferable_coins(
        self,
        from_type: str,
        to_type: str,
    ) -> dict[str, Any]:
        """Retrieve coins transferable between Bitget account types."""
        return self._native_private(
            "get_transferable_coins",
            self._native_params(fromType=from_type, toType=to_type),
        )

    @legacy_keywords(
        {
            "startTime": "start_time",
            "endTime": "end_time",
            "orderId": "order_id",
            "idLessThan": "id_less_than",
        }
    )
    def get_deposit_records(
        self,
        start_time: int | str,
        end_time: int | str,
        coin: str | None = None,
        order_id: str | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget deposit records."""
        return self._native_private(
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

    def get_uta_account_assets(self) -> dict[str, Any]:
        """Retrieve Bitget UTA account assets."""
        return self._native_private("get_uta_account_assets", [])

    def get_reality_orderbook(self, product_symbol: str) -> dict[str, Any]:
        """Return Reality raw-depth snapshot (requires Bitget whitelist)."""
        return self._native_private(
            "get_reality_orderbook", self._native_params(product_symbol=product_symbol)
        )

    def get_reality_fills(self, product_symbol: str, limit: int | None = None) -> dict[str, Any]:
        """Return recent Reality platform fills (requires Bitget whitelist)."""
        return self._native_private(
            "get_reality_fills", self._native_params(product_symbol=product_symbol, limit=limit)
        )

    def get_uta_account_info(self) -> dict[str, Any]:
        """Retrieve Bitget UTA API account information."""
        return self._native_private("get_uta_account_info", [])

    @legacy_keywords(
        {
            "posSide": "pos_side",
            "marginMode": "margin_mode",
            "longLeverage": "long_leverage",
            "shortLeverage": "short_leverage",
        }
    )
    def set_uta_leverage(
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
        return self._native_private(
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

    @legacy_keywords({"holdMode": "hold_mode"})
    def set_uta_hold_mode(self, hold_mode: str) -> dict[str, Any]:
        """Set Bitget UTA holding mode."""
        return self._native_private(
            "set_uta_hold_mode",
            self._native_params(holdMode=hold_mode),
        )

    @legacy_keywords({"marginCoin": "margin_coin", "productType": "product_type"})
    def get_futures_account(
        self,
        product_symbol: str,
        margin_coin: str = "USDT",
        product_type: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve one Bitget futures account."""
        return self._native_private(
            "get_futures_account",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
            ),
        )

    @legacy_keywords({"productType": "product_type"})
    def get_futures_accounts(
        self,
        product_type: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures accounts."""
        return self._native_private(
            "get_futures_accounts",
            self._native_params(productType=product_type),
        )

    @legacy_keywords(
        {
            "productType": "product_type",
            "businessType": "business_type",
            "onlyFunding": "only_funding",
            "idLessThan": "id_less_than",
            "startTime": "start_time",
            "endTime": "end_time",
        }
    )
    def get_futures_account_bills(
        self,
        product_type: str = "USDT-FUTURES",
        coin: str | None = None,
        business_type: str | None = None,
        only_funding: str | None = None,
        id_less_than: str | None = None,
        start_time: int | str | None = None,
        end_time: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures account bills."""
        return self._native_private(
            "get_futures_account_bills",
            self._native_params(
                productType=product_type,
                coin=coin,
                businessType=business_type,
                onlyFunding=only_funding,
                idLessThan=id_less_than,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    @legacy_keywords(
        {
            "marginCoin": "margin_coin",
            "productType": "product_type",
            "holdSide": "hold_side",
            "longLeverage": "long_leverage",
            "shortLeverage": "short_leverage",
        }
    )
    def set_futures_leverage(
        self,
        product_symbol: str,
        leverage: int | str | None = None,
        margin_coin: str = "USDT",
        product_type: str = "USDT-FUTURES",
        hold_side: str | None = None,
        long_leverage: int | str | None = None,
        short_leverage: int | str | None = None,
    ) -> dict[str, Any]:
        """
        Set Bitget futures leverage.

        Pass ``leverage``, or ``longLeverage``/``shortLeverage`` to set each side separately.
        """
        if leverage is None and long_leverage is None and short_leverage is None:
            raise ValueError("Specify leverage, longLeverage, or shortLeverage.")
        return self._native_private(
            "set_futures_leverage",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
                leverage=leverage,
                holdSide=hold_side,
                longLeverage=long_leverage,
                shortLeverage=short_leverage,
            ),
        )

    @legacy_keywords(
        {"marginMode": "margin_mode", "marginCoin": "margin_coin", "productType": "product_type"}
    )
    def set_futures_margin_mode(
        self,
        product_symbol: str,
        margin_mode: str,
        margin_coin: str = "USDT",
        product_type: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Set Bitget futures margin mode."""
        return self._native_private(
            "set_futures_margin_mode",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
                marginMode=margin_mode,
            ),
        )

    @legacy_keywords({"posMode": "pos_mode", "productType": "product_type"})
    def set_futures_position_mode(
        self,
        pos_mode: str,
        product_type: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Set Bitget futures position mode."""
        return self._native_private(
            "set_futures_position_mode",
            self._native_params(productType=product_type, posMode=pos_mode),
        )

    @legacy_keywords({"productType": "product_type", "marginCoin": "margin_coin"})
    def get_futures_positions(
        self,
        product_type: str = "USDT-FUTURES",
        margin_coin: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve all Bitget futures positions."""
        return self._native_private(
            "get_futures_positions",
            self._native_params(productType=product_type, marginCoin=margin_coin),
        )

    @legacy_keywords({"productType": "product_type", "marginCoin": "margin_coin"})
    def get_futures_position(
        self,
        product_symbol: str,
        product_type: str = "USDT-FUTURES",
        margin_coin: str = "USDT",
    ) -> dict[str, Any]:
        """Retrieve one Bitget futures position."""
        return self._native_private(
            "get_futures_position",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
            ),
        )

    def get_uta_all_fee_rates(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve UTA fee rates for every pair in one product category."""
        return self._native_private(
            "get_uta_all_fee_rates",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
            ),
        )

    def get_uta_loan_data(self) -> dict[str, Any]:
        """Retrieve current UTA borrowing and interest data."""
        return self._native_private("get_uta_loan_data", [])

    def get_crypto_loan_coins(self, coin: str | None = None) -> dict[str, Any]:
        """Get supported Crypto Loan assets, limits, rates, and collateral ratios."""
        return self._native_private("get_crypto_loan_coins", self._native_params(coin=coin))

    @legacy_keywords(
        {"loanCoin": "loan_coin", "pledgeCoin": "pledge_coin", "pledgeAmount": "pledge_amount"}
    )
    def get_crypto_loan_interest(
        self,
        loan_coin: str,
        pledge_coin: str,
        daily: str,
        pledge_amount: str,
    ) -> dict[str, Any]:
        """Estimate Crypto Loan interest and borrowable amount."""
        return self._native_private(
            "get_crypto_loan_interest",
            self._native_params(
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                daily=daily,
                pledgeAmount=pledge_amount,
            ),
        )

    @legacy_keywords(
        {
            "loanCoin": "loan_coin",
            "pledgeCoin": "pledge_coin",
            "pledgeAmount": "pledge_amount",
            "loanAmount": "loan_amount",
        }
    )
    def borrow_crypto_loan(
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
        return self._native_private(
            "borrow_crypto_loan",
            self._native_params(
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                daily=daily,
                pledgeAmount=pledge_amount,
                loanAmount=loan_amount,
            ),
        )

    @legacy_keywords({"orderId": "order_id", "loanCoin": "loan_coin", "pledgeCoin": "pledge_coin"})
    def get_crypto_loan_ongoing(
        self,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
    ) -> dict[str, Any]:
        """Get current Crypto Loan orders and accrued interest."""
        return self._native_private(
            "get_crypto_loan_ongoing",
            self._native_params(orderId=order_id, loanCoin=loan_coin, pledgeCoin=pledge_coin),
        )

    @legacy_keywords(
        {
            "startTime": "start_time",
            "endTime": "end_time",
            "orderId": "order_id",
            "loanCoin": "loan_coin",
            "pledgeCoin": "pledge_coin",
            "pageNum": "page_num",
            "pageSize": "page_size",
        }
    )
    def get_crypto_loan_borrow_history(
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
        return self._native_private(
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

    @legacy_keywords(
        {"orderId": "order_id", "repayAll": "repay_all", "repayUnlock": "repay_unlock"}
    )
    def repay_crypto_loan(
        self,
        order_id: str,
        repay_all: str,
        amount: str | None = None,
        repay_unlock: str | None = None,
    ) -> dict[str, Any]:
        """Repay part or all of a Crypto Loan."""
        return self._native_private(
            "repay_crypto_loan",
            self._native_params(
                orderId=order_id,
                repayAll=repay_all,
                amount=amount,
                repayUnlock=repay_unlock,
            ),
        )

    @legacy_keywords(
        {
            "startTime": "start_time",
            "endTime": "end_time",
            "orderId": "order_id",
            "loanCoin": "loan_coin",
            "pledgeCoin": "pledge_coin",
            "pageNum": "page_num",
            "pageSize": "page_size",
        }
    )
    def get_crypto_loan_repay_history(
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
        return self._native_private(
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

    @legacy_keywords(
        {"orderId": "order_id", "pledgeCoin": "pledge_coin", "reviseType": "revise_type"}
    )
    def revise_crypto_loan_pledge(
        self, order_id: str, amount: str, pledge_coin: str, revise_type: str
    ) -> dict[str, Any]:
        """Add or withdraw collateral for a Crypto Loan."""
        return self._native_private(
            "revise_crypto_loan_pledge",
            self._native_params(
                orderId=order_id,
                amount=amount,
                pledgeCoin=pledge_coin,
                reviseType=revise_type,
            ),
        )

    @legacy_keywords(
        {
            "startTime": "start_time",
            "endTime": "end_time",
            "orderId": "order_id",
            "reviseSide": "revise_side",
            "pledgeCoin": "pledge_coin",
            "pageNum": "page_num",
            "pageSize": "page_size",
        }
    )
    def get_crypto_loan_pledge_history(
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
        return self._native_private(
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

    @legacy_keywords(
        {
            "startTime": "start_time",
            "endTime": "end_time",
            "orderId": "order_id",
            "loanCoin": "loan_coin",
            "pledgeCoin": "pledge_coin",
            "pageNum": "page_num",
            "pageSize": "page_size",
        }
    )
    def get_crypto_loan_liquidations(
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
        return self._native_private(
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

    def get_crypto_loan_debts(self) -> dict[str, Any]:
        """Get Crypto Loan liabilities and collateral assets."""
        return self._native_private("get_crypto_loan_debts", [])

    @legacy_keywords(
        {"repayableCoinList": "repayable_coin_list", "paymentCoinList": "payment_coin_list"}
    )
    def repay_uta_liability(
        self, repayable_coin_list: list[str], payment_coin_list: list[str]
    ) -> dict[str, Any]:
        """Repay UTA liabilities with selected repayment and payment assets."""
        return self._native_private(
            "repay_uta_liability",
            self._native_params(
                repayableCoinList=repayable_coin_list,
                paymentCoinList=payment_coin_list,
            ),
        )

    def get_uta_collateral_type(self) -> dict[str, Any]:
        """Retrieve the UTA collateral-type configuration."""
        return self._native_private("get_uta_collateral_type", [])

    def get_uta_custom_collateral_coins(self) -> dict[str, Any]:
        """Retrieve coins supported as custom UTA collateral."""
        return self._native_private("get_uta_custom_collateral_coins", [])

    @legacy_keywords(
        {
            "marginMode": "margin_mode",
            "longLeverage": "long_leverage",
            "shortLeverage": "short_leverage",
        }
    )
    def get_uta_pre_set_leverage(
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
        return self._native_private(
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
