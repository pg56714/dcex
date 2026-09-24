"""KuCoin Earn HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class EarnHTTP(HTTPManager):
    """HTTP client for KuCoin Simple Earn and structured Earn workflows."""

    def purchase_earn(
        self,
        productId: str,
        amount: str,
        accountType: str = "TRADE",
    ) -> dict[str, Any]:
        return self._native_private(
            "purchase_earn",
            self._native_params(productId=productId, amount=amount, accountType=accountType),
        )

    def get_earn_redeem_preview(
        self,
        orderId: str,
        fromAccountType: str,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_earn_redeem_preview",
            self._native_params(orderId=orderId, fromAccountType=fromAccountType),
        )

    def redeem_earn(
        self,
        orderId: str,
        amount: str | None = None,
        fromAccountType: str | None = None,
        confirmPunishRedeem: bool | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "redeem_earn",
            self._native_params(
                orderId=orderId,
                amount=amount,
                fromAccountType=fromAccountType,
                confirmPunishRedeem=confirmPunishRedeem,
            ),
        )

    def get_earn_savings_products(self, currency: str | None = None) -> dict[str, Any]:
        return self._earn_products("get_earn_savings_products", currency)

    def get_earn_promotion_products(self, currency: str | None = None) -> dict[str, Any]:
        return self._earn_products("get_earn_promotion_products", currency)

    def get_earn_staking_products(self, currency: str | None = None) -> dict[str, Any]:
        return self._earn_products("get_earn_staking_products", currency)

    def get_earn_kcs_staking_products(self, currency: str | None = None) -> dict[str, Any]:
        return self._earn_products("get_earn_kcs_staking_products", currency)

    def get_earn_eth_staking_products(self, currency: str | None = None) -> dict[str, Any]:
        return self._earn_products("get_earn_eth_staking_products", currency)

    def get_earn_account_holdings(
        self,
        currency: str | None = None,
        productId: str | None = None,
        productCategory: str | None = None,
        currentPage: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_earn_account_holdings",
            self._native_params(
                currency=currency,
                productId=productId,
                productCategory=productCategory,
                currentPage=currentPage,
                pageSize=pageSize,
            ),
        )

    def get_dual_investment_products(
        self,
        category: str,
        strikeCurrency: str,
        investCurrency: str,
        side: str,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_dual_investment_products",
            self._native_params(
                category=category,
                strikeCurrency=strikeCurrency,
                investCurrency=investCurrency,
                side=side,
            ),
        )

    def purchase_structured_earn(
        self,
        productId: str,
        investCurrency: str,
        investAmount: str,
        accountType: str = "TRADE",
    ) -> dict[str, Any]:
        return self._native_private(
            "purchase_structured_earn",
            self._native_params(
                productId=productId,
                investCurrency=investCurrency,
                investAmount=investAmount,
                accountType=accountType,
            ),
        )

    def get_structured_earn_orders(
        self,
        categories: str,
        orderId: str | None = None,
        investCurrency: str | None = None,
        currentPage: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_structured_earn_orders",
            self._native_params(
                categories=categories,
                orderId=orderId,
                investCurrency=investCurrency,
                currentPage=currentPage,
                pageSize=pageSize,
            ),
        )

    def _earn_products(self, method_name: str, currency: str | None) -> dict[str, Any]:
        return self._native_private(method_name, self._native_params(currency=currency))
