"""Async OKX Savings and staking HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager


class FinanceHTTP(HTTPManager):
    """Async HTTP client for OKX Savings, On-chain Earn, and native staking."""

    async def _native_finance_public(
        self, method_name: str, params: list[tuple[str, str]]
    ) -> dict[str, Any]:
        if self._native_client is None:
            raise RuntimeError("OKX native client is required for finance methods.")
        response, data = await request_native_json_async(
            self._native_client, "public_request", method_name, params
        )
        self._store_response_headers(response)
        return data

    async def get_saving_balance(self, ccy: str | None = None) -> dict[str, Any]:
        return await self._native_private("get_saving_balance", self._native_params(ccy=ccy))

    async def purchase_redeem_savings(
        self, ccy: str, amt: str, side: str, *, rate: str | None = None
    ) -> dict[str, Any]:
        return await self._native_private(
            "purchase_redeem_savings",
            self._native_params(ccy=ccy, amt=amt, side=side, rate=rate),
        )

    async def set_savings_lending_rate(self, ccy: str, rate: str) -> dict[str, Any]:
        return await self._native_private(
            "set_savings_lending_rate", self._native_params(ccy=ccy, rate=rate)
        )

    async def get_savings_lending_history(
        self,
        ccy: str | None = None,
        *,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_savings_lending_history",
            self._native_params(ccy=ccy, after=after, before=before, limit=limit),
        )

    async def get_public_borrow_info(self, ccy: str | None = None) -> dict[str, Any]:
        return await self._native_finance_public(
            "get_public_borrow_info", self._native_params(ccy=ccy)
        )

    async def get_public_borrow_history(
        self,
        ccy: str | None = None,
        *,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_finance_public(
            "get_public_borrow_history",
            self._native_params(ccy=ccy, after=after, before=before, limit=limit),
        )

    async def set_auto_earn(
        self, ccy: str, action: str, *, earnType: str | None = None
    ) -> dict[str, Any]:
        return await self._native_private(
            "set_auto_earn",
            self._native_params(ccy=ccy, action=action, earnType=earnType),
        )

    async def get_staking_offers(
        self,
        productId: str | None = None,
        *,
        protocolType: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_staking_offers",
            self._native_params(productId=productId, protocolType=protocolType, ccy=ccy),
        )

    async def purchase_staking(
        self,
        productId: str,
        investData: list[dict[str, Any]],
        *,
        term: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "purchase_staking",
            self._native_params(productId=productId, investData=investData, term=term, tag=tag),
        )

    async def redeem_staking(
        self, ordId: str, protocolType: str, *, allowEarlyRedeem: bool | None = None
    ) -> dict[str, Any]:
        return await self._native_private(
            "redeem_staking",
            self._native_params(
                ordId=ordId,
                protocolType=protocolType,
                allowEarlyRedeem=allowEarlyRedeem,
            ),
        )

    async def cancel_staking(self, ordId: str, protocolType: str) -> dict[str, Any]:
        return await self._native_private(
            "cancel_staking", self._native_params(ordId=ordId, protocolType=protocolType)
        )

    async def get_active_staking_orders(
        self,
        productId: str | None = None,
        *,
        protocolType: str | None = None,
        ccy: str | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_active_staking_orders",
            self._native_params(
                productId=productId, protocolType=protocolType, ccy=ccy, state=state
            ),
        )

    async def get_staking_order_history(
        self,
        productId: str | None = None,
        *,
        protocolType: str | None = None,
        ccy: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_staking_order_history",
            self._native_params(
                productId=productId,
                protocolType=protocolType,
                ccy=ccy,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    async def get_eth_staking_product_info(self) -> dict[str, Any]:
        return await self._native_private("get_eth_staking_product_info", [])

    async def purchase_eth_staking(self, amt: str) -> dict[str, Any]:
        return await self._native_private("purchase_eth_staking", self._native_params(amt=amt))

    async def redeem_eth_staking(self, amt: str) -> dict[str, Any]:
        return await self._native_private("redeem_eth_staking", self._native_params(amt=amt))

    async def cancel_eth_staking_redemption(self, ordId: str) -> dict[str, Any]:
        return await self._native_private(
            "cancel_eth_staking_redemption", self._native_params(ordId=ordId)
        )

    async def get_eth_staking_balance(self) -> dict[str, Any]:
        return await self._native_private("get_eth_staking_balance", [])

    async def get_eth_staking_history(
        self,
        type: str | None = None,
        *,
        status: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_eth_staking_history",
            self._native_params(type=type, status=status, after=after, before=before, limit=limit),
        )

    async def get_eth_staking_apy_history(self, days: int) -> dict[str, Any]:
        return await self._native_finance_public(
            "get_eth_staking_apy_history", self._native_params(days=days)
        )

    async def get_sol_staking_product_info(self) -> dict[str, Any]:
        return await self._native_private("get_sol_staking_product_info", [])

    async def purchase_sol_staking(self, amt: str) -> dict[str, Any]:
        return await self._native_private("purchase_sol_staking", self._native_params(amt=amt))

    async def redeem_sol_staking(self, amt: str) -> dict[str, Any]:
        return await self._native_private("redeem_sol_staking", self._native_params(amt=amt))

    async def get_sol_staking_balance(self) -> dict[str, Any]:
        return await self._native_private("get_sol_staking_balance", [])

    async def get_sol_staking_history(
        self,
        type: str | None = None,
        *,
        status: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_sol_staking_history",
            self._native_params(type=type, status=status, after=after, before=before, limit=limit),
        )

    async def get_sol_staking_apy_history(self, days: int) -> dict[str, Any]:
        return await self._native_finance_public(
            "get_sol_staking_apy_history", self._native_params(days=days)
        )

    async def get_flexible_loan_borrow_currencies(self) -> dict[str, Any]:
        return await self._native_private("get_flexible_loan_borrow_currencies", [])

    async def get_flexible_loan_collateral_assets(self, ccy: str | None = None) -> dict[str, Any]:
        return await self._native_private(
            "get_flexible_loan_collateral_assets", self._native_params(ccy=ccy)
        )

    async def get_flexible_loan_max_loan(
        self, borrowCcy: str, supCollateral: list[dict[str, Any]]
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_flexible_loan_max_loan",
            self._native_params(borrowCcy=borrowCcy, supCollateral=supCollateral),
        )

    async def get_flexible_loan_max_collateral_redeem(self, ccy: str) -> dict[str, Any]:
        return await self._native_private(
            "get_flexible_loan_max_collateral_redeem",
            self._native_params(ccy=ccy),
        )

    async def adjust_flexible_loan_collateral(
        self, type: str, collateralCcy: str, collateralAmt: str
    ) -> dict[str, Any]:
        return await self._native_private(
            "adjust_flexible_loan_collateral",
            self._native_params(
                type=type,
                collateralCcy=collateralCcy,
                collateralAmt=collateralAmt,
            ),
        )

    async def get_flexible_loan_info(self, ordId: str | None = None) -> dict[str, Any]:
        return await self._native_private(
            "get_flexible_loan_info", self._native_params(ordId=ordId)
        )

    async def get_flexible_loan_history(
        self,
        type: str | None = None,
        *,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_flexible_loan_history",
            self._native_params(type=type, after=after, before=before, limit=limit),
        )

    async def get_flexible_loan_interest_accrued(
        self,
        ccy: str | None = None,
        *,
        ordId: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_flexible_loan_interest_accrued",
            self._native_params(
                ccy=ccy,
                ordId=ordId,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    async def borrow_flexible_loan(
        self,
        loanData: list[dict[str, Any]],
        clOrdId: str,
        *,
        ordId: str | None = None,
        collateralData: list[dict[str, Any]] | None = None,
        eMode: bool | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "borrow_flexible_loan",
            self._native_params(
                loanData=loanData,
                clOrdId=clOrdId,
                ordId=ordId,
                collateralData=collateralData,
                eMode=eMode,
            ),
        )

    async def repay_flexible_loan(
        self, ordId: str, ccy: str, amt: str, clOrdId: str
    ) -> dict[str, Any]:
        return await self._native_private(
            "repay_flexible_loan",
            self._native_params(ordId=ordId, ccy=ccy, amt=amt, clOrdId=clOrdId),
        )

    async def get_flexible_loan_emode_info(self) -> dict[str, Any]:
        return await self._native_private("get_flexible_loan_emode_info", [])

    async def get_dual_investment_currency_pairs(self) -> dict[str, Any]:
        return await self._native_private("get_dual_investment_currency_pairs", [])

    async def get_dual_investment_products(
        self,
        baseCcy: str,
        quoteCcy: str,
        optType: str,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_dual_investment_products",
            self._native_params(baseCcy=baseCcy, quoteCcy=quoteCcy, optType=optType),
        )

    async def request_dual_investment_quote(
        self, productId: str, notionalSz: str, notionalCcy: str
    ) -> dict[str, Any]:
        return await self._native_private(
            "request_dual_investment_quote",
            self._native_params(
                productId=productId,
                notionalSz=notionalSz,
                notionalCcy=notionalCcy,
            ),
        )

    async def trade_dual_investment(self, quoteId: str) -> dict[str, Any]:
        return await self._native_private(
            "trade_dual_investment", self._native_params(quoteId=quoteId)
        )

    async def request_dual_investment_redeem_quote(self, ordId: str) -> dict[str, Any]:
        return await self._native_private(
            "request_dual_investment_redeem_quote",
            self._native_params(ordId=ordId),
        )

    async def redeem_dual_investment(self, ordId: str, quoteId: str) -> dict[str, Any]:
        return await self._native_private(
            "redeem_dual_investment",
            self._native_params(ordId=ordId, quoteId=quoteId),
        )

    async def get_dual_investment_order_status(self, ordId: str) -> dict[str, Any]:
        return await self._native_private(
            "get_dual_investment_order_status",
            self._native_params(ordId=ordId),
        )

    async def get_dual_investment_order_history(
        self,
        *,
        ordId: str | None = None,
        productId: str | None = None,
        uly: str | None = None,
        state: str | None = None,
        beginId: str | None = None,
        endId: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_dual_investment_order_history",
            self._native_params(
                ordId=ordId,
                productId=productId,
                uly=uly,
                state=state,
                beginId=beginId,
                endId=endId,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    async def get_okusd_limits(self) -> dict[str, Any]:
        return await self._native_private("get_okusd_limits", [])

    async def get_okusd_account(self) -> dict[str, Any]:
        return await self._native_private("get_okusd_account", [])

    async def get_okusd_rate_history(
        self,
        *,
        limit: int | None = None,
        begin: str | None = None,
        end: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_okusd_rate_history",
            self._native_params(limit=limit, begin=begin, end=end),
        )

    async def get_okusd_subscribe_history(
        self,
        *,
        limit: int | None = None,
        begin: str | None = None,
        end: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_okusd_subscribe_history",
            self._native_params(limit=limit, begin=begin, end=end),
        )

    async def get_okusd_redeem_history(
        self,
        *,
        limit: int | None = None,
        begin: str | None = None,
        end: str | None = None,
        type: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_okusd_redeem_history",
            self._native_params(limit=limit, begin=begin, end=end, type=type),
        )

    async def get_okusd_rewards_history(
        self,
        *,
        limit: int | None = None,
        begin: str | None = None,
        end: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_okusd_rewards_history",
            self._native_params(limit=limit, begin=begin, end=end),
        )

    async def subscribe_okusd(self, amt: str, client_order_id: str) -> dict[str, Any]:
        return await self._native_private(
            "subscribe_okusd",
            self._native_params(amt=amt, clOrdId=client_order_id),
        )

    async def redeem_okusd(
        self, amt: str, redeem_type: str, client_order_id: str
    ) -> dict[str, Any]:
        return await self._native_private(
            "redeem_okusd",
            self._native_params(amt=amt, redeemType=redeem_type, clOrdId=client_order_id),
        )
