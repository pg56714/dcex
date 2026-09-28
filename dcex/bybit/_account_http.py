"""Bybit account HTTP client backed by Rust."""

from typing import Any

from .._operation_guards import require_confirmation
from ._batch_http import AccountHTTPBatchHTTP
from ._http_manager import HTTPManager
from ._transfers_http import AccountHTTPTransfersHTTP
from ._withdrawals_http import AccountHTTPWithdrawalsHTTP


class AccountHTTP(
    AccountHTTPTransfersHTTP, AccountHTTPBatchHTTP, AccountHTTPWithdrawalsHTTP, HTTPManager
):
    """HTTP client for Bybit account operations."""

    def get_wallet_balance(self, coin: str | None = None) -> dict[str, Any]:
        """Get wallet balance for UNIFIED account."""
        return self._native_private("get_wallet_balance", self._native_params(coin=coin))

    def upgrade_to_unified_trading_account(self) -> dict[str, Any]:
        """Upgrade account to unified trading account."""
        return self._native_private("upgrade_to_unified_trading_account", [])

    def get_borrow_history(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get borrow history."""
        return self._native_private(
            "get_borrow_history",
            self._native_params(
                coin=coin,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_collateral_info(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Get collateral information."""
        return self._native_private(
            "get_collateral_info",
            self._native_params(currency=currency),
        )

    def manual_borrow(self, coin: str, amount: str) -> dict[str, Any]:
        """Borrow an asset at Bybit's variable rate."""
        return self._native_private(
            "manual_borrow",
            self._native_params(coin=coin, amount=amount),
        )

    def manual_repay(
        self,
        coin: str | None = None,
        amount: str | None = None,
        repaymentType: str = "FLEXIBLE",
    ) -> dict[str, Any]:
        """Repay flexible, fixed-rate, or all UTA liabilities."""
        return self._native_private(
            "manual_repay",
            self._native_params(
                coin=coin,
                amount=amount,
                repaymentType=repaymentType,
            ),
        )

    def manual_repay_without_conversion(
        self,
        coin: str,
        amount: str | None = None,
        repaymentType: str = "FLEXIBLE",
    ) -> dict[str, Any]:
        """Repay using only the available balance of the debt asset."""
        return self._native_private(
            "manual_repay_without_conversion",
            self._native_params(
                coin=coin,
                amount=amount,
                repaymentType=repaymentType,
            ),
        )

    def _request_fee_rates(
        self,
        method_name: str,
        product_symbol: str | None = None,
        baseCoin: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            method_name,
            self._native_params(product_symbol=product_symbol, baseCoin=baseCoin),
        )

    def get_spot_fee_rates(
        self, product_symbol: str | None = None, baseCoin: str | None = None
    ) -> dict[str, Any]:
        """Get Bybit Spot trading fee rates."""
        return self._request_fee_rates("get_spot_fee_rates", product_symbol, baseCoin)

    def get_linear_fee_rates(
        self, product_symbol: str | None = None, baseCoin: str | None = None
    ) -> dict[str, Any]:
        """Get Bybit linear-contract trading fee rates."""
        return self._request_fee_rates("get_linear_fee_rates", product_symbol, baseCoin)

    def get_inverse_fee_rates(
        self, product_symbol: str | None = None, baseCoin: str | None = None
    ) -> dict[str, Any]:
        """Get Bybit inverse-contract trading fee rates."""
        return self._request_fee_rates("get_inverse_fee_rates", product_symbol, baseCoin)

    def get_option_fee_rates(
        self, product_symbol: str | None = None, baseCoin: str | None = None
    ) -> dict[str, Any]:
        """Get Bybit option trading fee rates."""
        return self._request_fee_rates("get_option_fee_rates", product_symbol, baseCoin)

    def get_account_info(self) -> dict[str, Any]:
        """Get account information."""
        return self._native_private("get_account_info", [])

    def get_transaction_log(
        self,
        accountType: str | None = None,
        category: str | None = None,
        coin: str | None = None,
        baseCoin: str | None = None,
        type_: str | None = None,
        transSubType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get transaction log."""
        return self._native_private(
            "get_transaction_log",
            self._native_params(
                accountType=accountType,
                category=category,
                coin=coin,
                baseCoin=baseCoin,
                type=type_,
                transSubType=transSubType,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def set_margin_mode(
        self,
        margin_mode: str,
    ) -> dict[str, Any]:
        """Set margin mode."""
        return self._native_private(
            "set_margin_mode",
            self._native_params(margin_mode=margin_mode),
        )

    def set_spot_margin_leverage(
        self, leverage: str, *, currency: str | None = None
    ) -> dict[str, Any]:
        """Set UTA spot cross-margin leverage, optionally for one currency."""
        return self._native_private(
            "set_spot_margin_leverage", self._native_params(leverage=leverage, currency=currency)
        )

    def set_spot_margin_mode(self, spot_margin_mode: str) -> dict[str, Any]:
        """Enable (``1``) or disable (``0``) UTA spot margin trading."""
        return self._native_private(
            "set_spot_margin_mode", self._native_params(spotMarginMode=spot_margin_mode)
        )

    def get_account_instruments(
        self,
        category: str,
        product_symbol: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get account instruments; see
        https://bybit-exchange.github.io/docs/v5/account/instrument.
        """
        return self._native_private(
            "get_account_instruments",
            self._native_params(
                category=category, product_symbol=product_symbol, limit=limit, cursor=cursor
            ),
        )

    def get_dcp_info(self) -> dict[str, Any]:
        """Get dcp info; see https://bybit-exchange.github.io/docs/v5/account/dcp-info."""
        return self._native_private("get_dcp_info", self._native_params())

    def get_coin_greeks(self, base_coin: str | None = None) -> dict[str, Any]:
        """Get coin greeks; see https://bybit-exchange.github.io/docs/v5/account/coin-greeks."""
        return self._native_private("get_coin_greeks", self._native_params(baseCoin=base_coin))

    def repay_liability(self, coin: str | None = None) -> dict[str, Any]:
        """Repay liability; see https://bybit-exchange.github.io/docs/v5/account/repay-liability."""
        return self._native_private("repay_liability", self._native_params(coin=coin))

    def set_collateral_coin(self, coin: str, collateral_switch: str) -> dict[str, Any]:
        """
        Set collateral coin; see
        https://bybit-exchange.github.io/docs/v5/account/set-collateral.
        """
        return self._native_private(
            "set_collateral_coin",
            self._native_params(coin=coin, collateralSwitch=collateral_switch),
        )

    def get_asset_overview(
        self,
        member_id: str | None = None,
        valuation_currency: str | None = None,
        account_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Get asset overview; see
        https://bybit-exchange.github.io/docs/v5/asset/balance/asset-overview.
        """
        return self._native_private(
            "get_asset_overview",
            self._native_params(
                memberId=member_id, valuationCurrency=valuation_currency, accountType=account_type
            ),
        )

    def get_delivery_records(
        self,
        category: str,
        product_symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        exp_date: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get delivery records; see https://bybit-exchange.github.io/docs/v5/asset/delivery."""
        return self._native_private(
            "get_delivery_records",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                startTime=start_time,
                endTime=end_time,
                expDate=exp_date,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_settlement_records(
        self,
        category: str,
        product_symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get settlement records; see https://bybit-exchange.github.io/docs/v5/asset/settlement."""
        return self._native_private(
            "get_settlement_records",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_funding_account_history(
        self,
        create_time_from: str | None = None,
        create_time_to: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get funding account history; see
        https://bybit-exchange.github.io/docs/v5/asset/fund-history.
        """
        return self._native_private(
            "get_funding_account_history",
            self._native_params(
                createTimeFrom=create_time_from,
                createTimeTo=create_time_to,
                limit=limit,
                cursor=cursor,
            ),
        )

    def request_convert_quote(
        self,
        account_type: str,
        from_coin: str,
        to_coin: str,
        request_coin: str,
        request_amount: str,
        from_coin_type: str | None = None,
        to_coin_type: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Request convert quote; see
        https://bybit-exchange.github.io/docs/v5/asset/convert/apply-quote.
        """
        return self._native_private(
            "request_convert_quote",
            self._native_params(
                accountType=account_type,
                fromCoin=from_coin,
                toCoin=to_coin,
                requestCoin=request_coin,
                requestAmount=request_amount,
                fromCoinType=from_coin_type,
                toCoinType=to_coin_type,
                requestId=request_id,
            ),
        )

    def execute_convert_quote(self, quote_tx_id: str) -> dict[str, Any]:
        """
        Execute convert quote; see
        https://bybit-exchange.github.io/docs/v5/asset/convert/confirm-quote.
        """
        return self._native_private(
            "execute_convert_quote", self._native_params(quoteTxId=quote_tx_id)
        )

    def get_convert_result(self, quote_tx_id: str, account_type: str) -> dict[str, Any]:
        """
        Get convert result; see
        https://bybit-exchange.github.io/docs/v5/asset/convert/get-convert-result.
        """
        return self._native_private(
            "get_convert_result",
            self._native_params(quoteTxId=quote_tx_id, accountType=account_type),
        )

    def confirm_pending_mmr(self, category: str, product_symbol: str) -> dict[str, Any]:
        """
        Confirm pending mmr; see https://bybit-exchange.github.io/docs/v5/position/confirm-mmr.
        """
        return self._native_private(
            "confirm_pending_mmr",
            self._native_params(category=category, product_symbol=product_symbol),
        )

    def get_position_symbol_info(
        self, category: str, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """
        Get position symbol info; see
        https://bybit-exchange.github.io/docs/v5/position/batch-lvg.
        """
        return self._native_private(
            "get_position_symbol_info",
            self._native_params(category=category, product_symbol=product_symbol),
        )

    def get_api_key_info(self) -> dict[str, Any]:
        """Get api key info; see https://bybit-exchange.github.io/docs/v5/user/apikey-info."""
        return self._native_private("get_api_key_info", self._native_params())

    def get_option_asset_info(self) -> dict[str, Any]:
        """
        Get option asset info; see
        https://bybit-exchange.github.io/docs/v5/account/option-asset-info.
        """
        return self._native_private("get_option_asset_info", self._native_params())

    def get_portfolio_margin_info(self, base_coin: str | None = None) -> dict[str, Any]:
        """
        Get portfolio margin info; see
        https://bybit-exchange.github.io/docs/v5/asset/portfolio-margin.
        """
        return self._native_private(
            "get_portfolio_margin_info", self._native_params(baseCoin=base_coin)
        )

    def get_repayment_info(self, coin: str | None = None) -> dict[str, Any]:
        """Get repayment info; see https://bybit-exchange.github.io/docs/v5/account/pay-info."""
        return self._native_private("get_repayment_info", self._native_params(coin=coin))

    def get_trade_analysis(
        self, product_symbol: str, start_time: int | None = None, end_time: int | None = None
    ) -> dict[str, Any]:
        """
        Get trade analysis; see
        https://bybit-exchange.github.io/docs/v5/account/trade-info-for-analysis.
        """
        return self._native_private(
            "get_trade_analysis",
            self._native_params(
                product_symbol=product_symbol, startTime=start_time, endTime=end_time
            ),
        )

    def get_total_members_assets(self, coin: str | None = None) -> dict[str, Any]:
        """
        Get total members assets; see
        https://bybit-exchange.github.io/docs/v5/asset/total-members-assets.
        """
        return self._native_private("get_total_members_assets", self._native_params(coin=coin))

    def get_smp_group(self) -> dict[str, Any]:
        """GET /v5/account/smp-group; account-family restrictions are enforced by Bybit."""
        return self._native_private("get_smp_group", self._native_params())

    def get_trade_behavior_config(self) -> dict[str, Any]:
        """
        GET /v5/account/user-setting-config; account-family restrictions are enforced by Bybit.
        """
        return self._native_private("get_trade_behavior_config", self._native_params())

    def set_delta_mode(self, *, delta_enable: str) -> dict[str, Any]:
        """POST /v5/account/set-delta-mode; account-family restrictions are enforced by Bybit."""
        return self._native_private("set_delta_mode", self._native_params(deltaEnable=delta_enable))

    def set_spot_hedging(self, *, mode: str) -> dict[str, Any]:
        """POST /v5/account/set-hedging-mode; account-family restrictions are enforced by Bybit."""
        return self._native_private("set_spot_hedging", self._native_params(setHedgingMode=mode))

    def set_price_limit_behavior(self, *, category: str, modify_enable: bool) -> dict[str, Any]:
        """
        POST /v5/account/set-limit-px-action; account-family restrictions are enforced by Bybit.
        """
        return self._native_private(
            "set_price_limit_behavior",
            self._native_params(category=category, modifyEnable=modify_enable),
        )

    def get_closed_option_positions(
        self,
        *,
        category: str,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/position/get-closed-positions; account-family restrictions are enforced by
        Bybit.
        """
        return self._native_private(
            "get_closed_option_positions",
            self._native_params(
                category=category,
                symbol=symbol,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_move_position_history(
        self,
        *,
        category: str | None = None,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        status: str | None = None,
        block_trade_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """GET /v5/position/move-history; account-family restrictions are enforced by Bybit."""
        return self._native_private(
            "get_move_position_history",
            self._native_params(
                category=category,
                symbol=symbol,
                startTime=start_time,
                endTime=end_time,
                status=status,
                blockTradeId=block_trade_id,
                limit=limit,
                cursor=cursor,
            ),
        )

    def move_positions(
        self, *, from_uid: str, to_uid: str, legs: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """POST /v5/position/move-positions; account-family restrictions are enforced by Bybit."""
        return self._native_private(
            "move_positions", self._native_params(fromUid=from_uid, toUid=to_uid, list=legs)
        )

    def execute_small_balance_quote(self, *, quote_id: str) -> dict[str, Any]:
        """
        POST /v5/asset/covert/small-balance-execute.

        Source:
        https://bybit-exchange.github.io/docs/v5/asset/convert-small-balance/confirm-quote

        """
        return self._native_private(
            "execute_small_balance_quote", self._native_params(quoteId=quote_id)
        )

    def get_small_balance_history(
        self,
        *,
        account_type: str | None = None,
        quote_id: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        cursor: str | None = None,
        size: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/asset/covert/small-balance-history.

        Source:
        https://bybit-exchange.github.io/docs/v5/asset/convert-small-balance/exchange-history

        """
        return self._native_private(
            "get_small_balance_history",
            self._native_params(
                accountType=account_type,
                quoteId=quote_id,
                startTime=start_time,
                endTime=end_time,
                cursor=cursor,
                size=size,
            ),
        )

    def request_small_balance_quote(
        self, *, account_type: str, from_coin_list: list[str], to_coin: str
    ) -> dict[str, Any]:
        """
        POST /v5/asset/covert/get-quote.

        Source:
        https://bybit-exchange.github.io/docs/v5/asset/convert-small-balance/request-quote

        """
        return self._native_private(
            "request_small_balance_quote",
            self._native_params(
                accountType=account_type, fromCoinList=from_coin_list, toCoin=to_coin
            ),
        )

    def get_small_balance_coins(
        self, *, account_type: str, from_coin: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/asset/covert/small-balance-list.

        Source:
        https://bybit-exchange.github.io/docs/v5/asset/convert-small-balance/small-balanc-coins

        """
        return self._native_private(
            "get_small_balance_coins",
            self._native_params(accountType=account_type, fromCoin=from_coin),
        )

    def get_convert_coins(
        self, *, account_type: str, coin: str | None = None, side: int | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/asset/exchange/query-coin-list.

        Source:
        https://bybit-exchange.github.io/docs/v5/asset/convert/convert-coin-list

        """
        return self._native_private(
            "get_convert_coins", self._native_params(accountType=account_type, coin=coin, side=side)
        )

    def get_convert_history(
        self, *, account_type: str | None = None, index: int | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/asset/exchange/query-convert-history.

        Source:
        https://bybit-exchange.github.io/docs/v5/asset/convert/get-convert-history

        """
        return self._native_private(
            "get_convert_history",
            self._native_params(accountType=account_type, index=index, limit=limit),
        )

    def get_sub_account_deposit_address(
        self, *, coin: str, chain_type: str, sub_member_id: str
    ) -> dict[str, Any]:
        """
        GET /v5/asset/deposit/query-sub-member-address.

        Source:
        https://bybit-exchange.github.io/docs/v5/asset/deposit/sub-deposit-addr

        """
        return self._native_private(
            "get_sub_account_deposit_address",
            self._native_params(coin=coin, chainType=chain_type, subMemberId=sub_member_id),
        )

    def get_exchange_order_records(
        self,
        *,
        from_coin: str | None = None,
        to_coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/asset/exchange/order-record.

        Source:
        https://bybit-exchange.github.io/docs/v5/asset/exchange

        """
        return self._native_private(
            "get_exchange_order_records",
            self._native_params(fromCoin=from_coin, toCoin=to_coin, limit=limit, cursor=cursor),
        )

    def get_pre_upgrade_closed_pnl(
        self,
        *,
        category: str,
        symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/pre-upgrade/position/closed-pnl.

        Source:
        https://bybit-exchange.github.io/docs/v5/pre-upgrade/close-pnl

        """
        return self._native_private(
            "get_pre_upgrade_closed_pnl",
            self._native_params(
                category=category,
                symbol=symbol,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_pre_upgrade_delivery_records(
        self,
        *,
        category: str,
        symbol: str | None = None,
        exp_date: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/pre-upgrade/asset/delivery-record.

        Source:
        https://bybit-exchange.github.io/docs/v5/pre-upgrade/delivery

        """
        return self._native_private(
            "get_pre_upgrade_delivery_records",
            self._native_params(
                category=category, symbol=symbol, expDate=exp_date, limit=limit, cursor=cursor
            ),
        )

    def get_pre_upgrade_executions(
        self,
        *,
        category: str,
        symbol: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        base_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        exec_type: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/pre-upgrade/execution/list.

        Source:
        https://bybit-exchange.github.io/docs/v5/pre-upgrade/execution

        """
        return self._native_private(
            "get_pre_upgrade_executions",
            self._native_params(
                category=category,
                symbol=symbol,
                orderId=order_id,
                orderLinkId=order_link_id,
                baseCoin=base_coin,
                startTime=start_time,
                endTime=end_time,
                execType=exec_type,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_pre_upgrade_order_history(
        self,
        *,
        category: str,
        symbol: str | None = None,
        base_coin: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        order_filter: str | None = None,
        order_status: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/pre-upgrade/order/history.

        Source:
        https://bybit-exchange.github.io/docs/v5/pre-upgrade/order-list

        """
        return self._native_private(
            "get_pre_upgrade_order_history",
            self._native_params(
                category=category,
                symbol=symbol,
                baseCoin=base_coin,
                orderId=order_id,
                orderLinkId=order_link_id,
                orderFilter=order_filter,
                orderStatus=order_status,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_pre_upgrade_settlement_records(
        self,
        *,
        category: str,
        symbol: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/pre-upgrade/asset/settlement-record.

        Source:
        https://bybit-exchange.github.io/docs/v5/pre-upgrade/settlement

        """
        return self._native_private(
            "get_pre_upgrade_settlement_records",
            self._native_params(category=category, symbol=symbol, limit=limit, cursor=cursor),
        )

    def get_pre_upgrade_transaction_log(
        self,
        *,
        category: str,
        base_coin: str | None = None,
        type_: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/pre-upgrade/account/transaction-log.

        Source:
        https://bybit-exchange.github.io/docs/v5/pre-upgrade/transaction-log

        """
        return self._native_private(
            "get_pre_upgrade_transaction_log",
            self._native_params(
                category=category,
                baseCoin=base_coin,
                type=type_,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_margin_currency_data(self, *, currency: str | None = None) -> dict[str, Any]:
        """
        GET /v5/spot-margin-trade/currency-data.

        Source:
        https://bybit-exchange.github.io/docs/v5/spot-margin-uta/currency-data

        """
        return self._native_private(
            "get_margin_currency_data", self._native_params(currency=currency)
        )

    def create_sub_account_api_key(
        self,
        *,
        subuid: int,
        read_only: int,
        permissions: dict[str, list[str]],
        note: str | None = None,
        ips: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /v5/user/create-sub-api.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/create-subuid-apikey

        """
        return self._native_private(
            "create_sub_account_api_key",
            self._native_params(
                subuid=subuid, note=note, readOnly=read_only, ips=ips, permissions=permissions
            ),
        )

    def create_sub_account(
        self,
        *,
        username: str,
        member_type: int,
        password: str | None = None,
        switch: int | None = None,
        note: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /v5/user/create-sub-member.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/create-subuid

        """
        return self._native_private(
            "create_sub_account",
            self._native_params(
                username=username,
                password=password,
                memberType=member_type,
                switch=switch,
                note=note,
            ),
        )

    def set_sub_account_frozen(self, *, subuid: int, frozen: int) -> dict[str, Any]:
        """
        POST /v5/user/frozen-sub-member.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/froze-subuid

        """
        return self._native_private(
            "set_sub_account_frozen", self._native_params(subuid=subuid, frozen=frozen)
        )

    def get_sub_account_api_keys(
        self, *, sub_member_id: str, limit: int | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/user/sub-apikeys.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/list-sub-apikeys

        """
        return self._native_private(
            "get_sub_account_api_keys",
            self._native_params(subMemberId=sub_member_id, limit=limit, cursor=cursor),
        )

    def modify_api_key(
        self,
        *,
        read_only: int | None = None,
        permissions: dict[str, list[str]] | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """
        POST /v5/user/update-api.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/modify-master-apikey



        Requires confirm=True. This changes the API key permissions.
        """
        require_confirmation(confirm)
        if read_only is None and permissions is None:
            raise ValueError("provide at least one API key change")
        return self._native_private(
            "modify_api_key",
            self._native_params(confirm=confirm, readOnly=read_only, permissions=permissions),
        )

    def modify_sub_account_api_key(
        self,
        *,
        apikey: str | None = None,
        read_only: int | None = None,
        ips: str | None = None,
        permissions: dict[str, list[str]] | None = None,
    ) -> dict[str, Any]:
        """
        POST /v5/user/update-sub-api.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/modify-sub-apikey

        """
        return self._native_private(
            "modify_sub_account_api_key",
            self._native_params(
                apikey=apikey, readOnly=read_only, ips=ips, permissions=permissions
            ),
        )

    def get_sub_accounts_paginated(
        self, *, page_size: str | None = None, next_cursor: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/user/submembers.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/page-subuid

        """
        return self._native_private(
            "get_sub_accounts_paginated",
            self._native_params(pageSize=page_size, nextCursor=next_cursor),
        )

    def delete_api_key(self, *, confirm: bool = False) -> dict[str, Any]:
        """
        POST /v5/user/delete-api.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/rm-master-apikey



        Requires confirm=True. This revokes the API key and its access.
        """
        require_confirmation(confirm)
        return self._native_private("delete_api_key", self._native_params(confirm=confirm))

    def delete_sub_account_api_key(self, *, apikey: str | None = None) -> dict[str, Any]:
        """
        POST /v5/user/delete-sub-api.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/rm-sub-apikey

        """
        return self._native_private(
            "delete_sub_account_api_key", self._native_params(apikey=apikey)
        )

    def delete_sub_account(self, *, sub_member_id: str) -> dict[str, Any]:
        """
        POST /v5/user/del-submember.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/rm-subuid

        """
        return self._native_private(
            "delete_sub_account", self._native_params(subMemberId=sub_member_id)
        )

    def sign_trading_agreement(self, *, category_v2: int, agree: bool) -> dict[str, Any]:
        """
        POST /v5/user/agreement.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/sign-agreement

        """
        return self._native_private(
            "sign_trading_agreement", self._native_params(categoryV2=category_v2, agree=agree)
        )

    def get_sub_accounts(self) -> dict[str, Any]:
        """
        GET /v5/user/query-sub-members.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/subuid-list

        """
        return self._native_private("get_sub_accounts", self._native_params())

    def get_member_wallet_types(self, *, member_ids: str | None = None) -> dict[str, Any]:
        """
        GET /v5/user/get-member-type.

        Source:
        https://bybit-exchange.github.io/docs/v5/user/wallet-type

        """
        return self._native_private(
            "get_member_wallet_types", self._native_params(memberIds=member_ids)
        )

    def get_all_api_rate_limits(
        self, *, limit: str | None = None, cursor: str | None = None, uids: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/apilimit/query-all.

        Source:
        https://bybit-exchange.github.io/docs/v5/rate-limit/rules-for-pros/apilimit-query-all

        """
        return self._native_private(
            "get_all_api_rate_limits", self._native_params(limit=limit, cursor=cursor, uids=uids)
        )

    def get_api_rate_limit_cap(self) -> dict[str, Any]:
        """
        GET /v5/apilimit/query-cap.

        Source:
        https://bybit-exchange.github.io/docs/v5/rate-limit/rules-for-pros/apilimit-query-cap

        """
        return self._native_private("get_api_rate_limit_cap", self._native_params())

    def get_api_rate_limits(self, *, uids: str) -> dict[str, Any]:
        """
        GET /v5/apilimit/query.

        Source:
        https://bybit-exchange.github.io/docs/v5/rate-limit/rules-for-pros/apilimit-query

        """
        return self._native_private("get_api_rate_limits", self._native_params(uids=uids))

    def set_api_rate_limits(self, *, list: list[dict[str, Any]]) -> dict[str, Any]:
        """
        POST /v5/apilimit/set.

        Source:
        https://bybit-exchange.github.io/docs/v5/rate-limit/rules-for-pros/apilimit-set

        """
        return self._native_private("set_api_rate_limits", self._native_params(list=list))

    def submit_deposit_information(
        self, *, deposit_id: int, questionnaire: str, sub_account_id: int | None = None
    ) -> dict[str, Any]:
        """
        POST /v5/asset/travel-rule/deposit/submit.

        Source:
        https://bybit-exchange.github.io/docs/v5/asset/deposit/submit-info

        """
        return self._native_private(
            "submit_deposit_information",
            self._native_params(
                depositId=deposit_id, subAccountId=sub_account_id, questionnaire=questionnaire
            ),
        )

    def get_crypto_loan_borrowable_collateralisable_number(
        self, *, loan_currency: str, collateral_currency: str
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan/borrowable-collateralisable-number.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/acct-borrow-collateral.mdx
        """
        return self._native_private(
            "get_crypto_loan_borrowable_collateralisable_number",
            self._native_params(loanCurrency=loan_currency, collateralCurrency=collateral_currency),
        )

    def crypto_loan_adjust_ltv(
        self, *, order_id: str, amount: str, direction: str
    ) -> dict[str, Any]:
        """
        POST /v5/crypto-loan/adjust-ltv.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/adjust-collateral.mdx
        """
        return self._native_private(
            "crypto_loan_adjust_ltv",
            self._native_params(orderId=order_id, amount=amount, direction=direction),
        )

    def get_crypto_loan_borrow_history(
        self,
        *,
        order_id: str | None = None,
        loan_currency: str | None = None,
        collateral_currency: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan/borrow-history.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/completed-loan-order.mdx
        """
        return self._native_private(
            "get_crypto_loan_borrow_history",
            self._native_params(
                orderId=order_id,
                loanCurrency=loan_currency,
                collateralCurrency=collateral_currency,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_crypto_loan_adjustment_history(
        self,
        *,
        order_id: str | None = None,
        adjust_id: str | None = None,
        collateral_currency: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan/adjustment-history.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/ltv-adjust-history.mdx
        """
        return self._native_private(
            "get_crypto_loan_adjustment_history",
            self._native_params(
                orderId=order_id,
                adjustId=adjust_id,
                collateralCurrency=collateral_currency,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_crypto_loan_max_collateral_amount(self, *, order_id: str) -> dict[str, Any]:
        """
        GET /v5/crypto-loan/max-collateral-amount.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/reduce-max-collateral-amt.mdx
        """
        return self._native_private(
            "get_crypto_loan_max_collateral_amount", self._native_params(orderId=order_id)
        )

    def get_crypto_loan_repayment_history(
        self,
        *,
        order_id: str | None = None,
        repay_id: str | None = None,
        loan_currency: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan/repayment-history.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/repay-transaction.mdx
        """
        return self._native_private(
            "get_crypto_loan_repayment_history",
            self._native_params(
                orderId=order_id,
                repayId=repay_id,
                loanCurrency=loan_currency,
                limit=limit,
                cursor=cursor,
            ),
        )

    def crypto_loan_repay(self, *, order_id: str, amount: str) -> dict[str, Any]:
        """
        POST /v5/crypto-loan/repay.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/repay.mdx
        """
        return self._native_private(
            "crypto_loan_repay", self._native_params(orderId=order_id, amount=amount)
        )

    def get_crypto_loan_ongoing_orders(
        self,
        *,
        order_id: str | None = None,
        loan_currency: str | None = None,
        collateral_currency: str | None = None,
        loan_term_type: str | None = None,
        loan_term: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan/ongoing-orders.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/unpaid-loan-order.mdx
        """
        return self._native_private(
            "get_crypto_loan_ongoing_orders",
            self._native_params(
                orderId=order_id,
                loanCurrency=loan_currency,
                collateralCurrency=collateral_currency,
                loanTermType=loan_term_type,
                loanTerm=loan_term,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_spot_x_puzzle_project_list(
        self,
        *,
        status: int,
        project_id: str | None = None,
        activity_coin: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/spot-x/puzzle/project/list.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/finance/spot-x/puzzle/puzzle-project-list.mdx
        """
        return self._native_private(
            "get_spot_x_puzzle_project_list",
            self._native_params(
                status=status,
                projectId=project_id,
                activityCoin=activity_coin,
                cursor=cursor,
                limit=limit,
            ),
        )

    def get_spot_x_token_splash_project_list(
        self,
        *,
        status: int,
        project_id: str | None = None,
        activity_coin: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/spot-x/token-splash/project/list.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/finance/spot-x/token-splash/token-splash-project-list.mdx
        """
        return self._native_private(
            "get_spot_x_token_splash_project_list",
            self._native_params(
                status=status,
                projectId=project_id,
                activityCoin=activity_coin,
                cursor=cursor,
                limit=limit,
            ),
        )

    def get_spot_x_token_splash_user_activity_params(
        self, *, project_id: str | None = None, activity_coin: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/spot-x/token-splash/user/activity-params.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/finance/spot-x/token-splash/token-splash-user-activity-params.mdx
        """
        return self._native_private(
            "get_spot_x_token_splash_user_activity_params",
            self._native_params(projectId=project_id, activityCoin=activity_coin),
        )

    def crypto_loan_common_adjust_ltv(
        self, *, currency: str, amount: str, direction: str
    ) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-common/adjust-ltv.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/adjust-collateral.mdx
        """
        return self._native_private(
            "crypto_loan_common_adjust_ltv",
            self._native_params(currency=currency, amount=amount, direction=direction),
        )

    def get_crypto_loan_common_position(self) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-common/position.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/crypto-loan-position.mdx
        """
        return self._native_private("get_crypto_loan_common_position", self._native_params())

    def get_crypto_loan_fixed_available_inventory(
        self, *, currency: str, term: str, annual_rate: str
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-fixed/available-inventory.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/available-inventory.mdx
        """
        return self._native_private(
            "get_crypto_loan_fixed_available_inventory",
            self._native_params(currency=currency, term=term, annualRate=annual_rate),
        )

    def get_crypto_loan_fixed_borrow_contract_info(
        self,
        *,
        order_id: str | None = None,
        loan_id: str | None = None,
        order_currency: str | None = None,
        term: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-fixed/borrow-contract-info.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/borrow-contract.mdx
        """
        return self._native_private(
            "get_crypto_loan_fixed_borrow_contract_info",
            self._native_params(
                orderId=order_id,
                loanId=loan_id,
                orderCurrency=order_currency,
                term=term,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_crypto_loan_fixed_borrow_order_info(
        self,
        *,
        order_id: str | None = None,
        order_currency: str | None = None,
        state: str | None = None,
        term: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-fixed/borrow-order-info.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/borrow-order.mdx
        """
        return self._native_private(
            "get_crypto_loan_fixed_borrow_order_info",
            self._native_params(
                orderId=order_id,
                orderCurrency=order_currency,
                state=state,
                term=term,
                limit=limit,
                cursor=cursor,
            ),
        )

    def crypto_loan_fixed_borrow(
        self,
        *,
        order_currency: str,
        order_amount: str,
        annual_rate: str,
        term: str,
        repay_type: str | None = None,
        strategy_type: str | None = None,
        collateral_list: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-fixed/borrow.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/borrow.mdx
        """
        return self._native_private(
            "crypto_loan_fixed_borrow",
            self._native_params(
                orderCurrency=order_currency,
                orderAmount=order_amount,
                annualRate=annual_rate,
                term=term,
                repayType=repay_type,
                strategyType=strategy_type,
                collateralList=collateral_list,
            ),
        )

    def crypto_loan_fixed_borrow_order_cancel(self, *, order_id: str) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-fixed/borrow-order-cancel.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/cancel-borrow.mdx
        """
        return self._native_private(
            "crypto_loan_fixed_borrow_order_cancel", self._native_params(orderId=order_id)
        )

    def crypto_loan_fixed_supply_order_cancel(
        self, *, order_id: str, refunded_account: str | None = None
    ) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-fixed/supply-order-cancel.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/cancel-supply.mdx
        """
        return self._native_private(
            "crypto_loan_fixed_supply_order_cancel",
            self._native_params(orderId=order_id, refundedAccount=refunded_account),
        )

    def get_crypto_loan_fixed_renew_info(
        self,
        *,
        order_id: str | None = None,
        order_currency: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-fixed/renew-info.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/renew-order.mdx
        """
        return self._native_private(
            "get_crypto_loan_fixed_renew_info",
            self._native_params(
                orderId=order_id, orderCurrency=order_currency, limit=limit, cursor=cursor
            ),
        )

    def crypto_loan_fixed_renew(
        self, *, loan_id: str, collateral_list: list[dict[str, str]] | None = None
    ) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-fixed/renew.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/renew.mdx
        """
        return self._native_private(
            "crypto_loan_fixed_renew",
            self._native_params(loanId=loan_id, collateralList=collateral_list),
        )

    def crypto_loan_fixed_repay_collateral(
        self, *, loan_currency: str, collateral_coin: str, amount: str, loan_id: str | None = None
    ) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-fixed/repay-collateral.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/repay-collateral.mdx
        """
        return self._native_private(
            "crypto_loan_fixed_repay_collateral",
            self._native_params(
                loanId=loan_id,
                loanCurrency=loan_currency,
                collateralCoin=collateral_coin,
                amount=amount,
            ),
        )

    def get_crypto_loan_fixed_repayment_history(
        self,
        *,
        repay_id: str | None = None,
        loan_currency: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-fixed/repayment-history.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/repay-history.mdx
        """
        return self._native_private(
            "get_crypto_loan_fixed_repayment_history",
            self._native_params(
                repayId=repay_id, loanCurrency=loan_currency, limit=limit, cursor=cursor
            ),
        )

    def crypto_loan_fixed_fully_repay(
        self, *, loan_id: str | None = None, loan_currency: str | None = None
    ) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-fixed/fully-repay.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/repay.mdx
        """
        return self._native_private(
            "crypto_loan_fixed_fully_repay",
            self._native_params(loanId=loan_id, loanCurrency=loan_currency),
        )

    def get_crypto_loan_fixed_supply_order_info(
        self,
        *,
        order_id: str | None = None,
        order_currency: str | None = None,
        state: str | None = None,
        term: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-fixed/supply-order-info.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/supply-order.mdx
        """
        return self._native_private(
            "get_crypto_loan_fixed_supply_order_info",
            self._native_params(
                orderId=order_id,
                orderCurrency=order_currency,
                state=state,
                term=term,
                limit=limit,
                cursor=cursor,
            ),
        )

    def crypto_loan_fixed_supply(
        self,
        *,
        order_currency: str,
        order_amount: str,
        annual_rate: str,
        term: str,
        available_source: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-fixed/supply.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/supply.mdx
        """
        return self._native_private(
            "crypto_loan_fixed_supply",
            self._native_params(
                orderCurrency=order_currency,
                orderAmount=order_amount,
                annualRate=annual_rate,
                term=term,
                availableSource=available_source,
            ),
        )

    def get_crypto_loan_flexible_available_inventory(self, *, currency: str) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-flexible/available-inventory.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/available-inventory.mdx
        """
        return self._native_private(
            "get_crypto_loan_flexible_available_inventory", self._native_params(currency=currency)
        )

    def crypto_loan_flexible_borrow(
        self,
        *,
        loan_currency: str,
        loan_amount: str,
        collateral_list: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-flexible/borrow.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/borrow.mdx
        """
        return self._native_private(
            "crypto_loan_flexible_borrow",
            self._native_params(
                loanCurrency=loan_currency, loanAmount=loan_amount, collateralList=collateral_list
            ),
        )

    def get_crypto_loan_flexible_borrow_history(
        self,
        *,
        order_id: str | None = None,
        loan_currency: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-flexible/borrow-history.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/loan-orders.mdx
        """
        return self._native_private(
            "get_crypto_loan_flexible_borrow_history",
            self._native_params(
                orderId=order_id, loanCurrency=loan_currency, limit=limit, cursor=cursor
            ),
        )

    def crypto_loan_flexible_repay_collateral(
        self, *, loan_currency: str, collateral_coin: str, amount: str
    ) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-flexible/repay-collateral.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/repay-collateral.mdx
        """
        return self._native_private(
            "crypto_loan_flexible_repay_collateral",
            self._native_params(
                loanCurrency=loan_currency, collateralCoin=collateral_coin, amount=amount
            ),
        )

    def get_crypto_loan_flexible_repayment_history(
        self,
        *,
        repay_id: str | None = None,
        loan_currency: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-flexible/repayment-history.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/repay-orders.mdx
        """
        return self._native_private(
            "get_crypto_loan_flexible_repayment_history",
            self._native_params(
                repayId=repay_id, loanCurrency=loan_currency, limit=limit, cursor=cursor
            ),
        )

    def crypto_loan_flexible_repay(self, *, loan_currency: str, amount: str) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-flexible/repay.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/repay.mdx
        """
        return self._native_private(
            "crypto_loan_flexible_repay",
            self._native_params(loanCurrency=loan_currency, amount=amount),
        )

    def get_crypto_loan_flexible_ongoing_coin(
        self, *, loan_currency: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-flexible/ongoing-coin.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/unpaid-loan-order.mdx
        """
        return self._native_private(
            "get_crypto_loan_flexible_ongoing_coin", self._native_params(loanCurrency=loan_currency)
        )

    def get_crypto_loan_common_adjustment_history(
        self,
        *,
        adjust_id: str | None = None,
        collateral_currency: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-common/adjustment-history.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/ltv-adjust-history.mdx
        """
        return self._native_private(
            "get_crypto_loan_common_adjustment_history",
            self._native_params(
                adjustId=adjust_id,
                collateralCurrency=collateral_currency,
                limit=limit,
                cursor=cursor,
            ),
        )

    def crypto_loan_common_max_loan(
        self, *, currency: str, collateral_list: list[dict[str, str]] | None = None
    ) -> dict[str, Any]:
        """
        POST /v5/crypto-loan-common/max-loan.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/max-loan-amt.mdx
        """
        return self._native_private(
            "crypto_loan_common_max_loan",
            self._native_params(currency=currency, collateralList=collateral_list),
        )

    def get_crypto_loan_common_max_collateral_amount(self, *, currency: str) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-common/max-collateral-amount.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/reduce-max-collateral-amt.mdx
        """
        return self._native_private(
            "get_crypto_loan_common_max_collateral_amount", self._native_params(currency=currency)
        )

    def get_spot_lever_token_order_record(
        self,
        *,
        lt_coin: str | None = None,
        order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        lt_order_type: int | None = None,
        serial_no: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/spot-lever-token/order-record.

        Decimal amounts are strings. Source: https://github.com/bybit-exchange/docs/blob/master/docs/v5/lt/order-record.mdx
        """
        return self._native_private(
            "get_spot_lever_token_order_record",
            self._native_params(
                ltCoin=lt_coin,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                ltOrderType=lt_order_type,
                serialNo=serial_no,
            ),
        )

    def spot_lever_token_purchase(
        self, *, lt_coin: str, lt_amount: str, serial_no: str | None = None
    ) -> dict[str, Any]:
        """
        POST /v5/spot-lever-token/purchase.

        Decimal amounts are strings. Source: https://github.com/bybit-exchange/docs/blob/master/docs/v5/lt/purchase.mdx
        """
        return self._native_private(
            "spot_lever_token_purchase",
            self._native_params(ltCoin=lt_coin, ltAmount=lt_amount, serialNo=serial_no),
        )

    def spot_lever_token_redeem(
        self, *, lt_coin: str, quantity: str, serial_no: str | None = None
    ) -> dict[str, Any]:
        """
        POST /v5/spot-lever-token/redeem.

        Decimal amounts are strings. Source: https://github.com/bybit-exchange/docs/blob/master/docs/v5/lt/redeem.mdx
        """
        return self._native_private(
            "spot_lever_token_redeem",
            self._native_params(ltCoin=lt_coin, quantity=quantity, serialNo=serial_no),
        )

    def get_fixed_loan_supply_contract_info(
        self,
        *,
        order_id: str | None = None,
        supply_id: str | None = None,
        supply_currency: str | None = None,
        term: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Query fixed crypto-loan supply contracts."""
        return self._native_private(
            "get_fixed_loan_supply_contract_info",
            self._native_params(
                orderId=order_id,
                supplyId=supply_id,
                supplyCurrency=supply_currency,
                term=term,
                limit=limit,
                cursor=cursor,
            ),
        )
