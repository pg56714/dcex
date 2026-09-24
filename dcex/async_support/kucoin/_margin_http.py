"""Async KuCoin Margin and Credit HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager


class MarginHTTP(HTTPManager):
    """Async HTTP client for KuCoin margin borrowing and lending workflows."""

    async def get_cross_margin_symbols(self, product_symbol: str | None = None) -> dict[str, Any]:
        return await self._native_public(
            "get_cross_margin_symbols",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_isolated_margin_symbols(self) -> dict[str, Any]:
        return await self._native_public("get_isolated_margin_symbols", [])

    async def get_margin_collateral_ratio(self, currencyList: str | None = None) -> dict[str, Any]:
        return await self._native_public(
            "get_margin_collateral_ratio",
            self._native_params(currencyList=currencyList),
        )

    async def get_margin_available_inventory(self, currency: str | None = None) -> dict[str, Any]:
        return await self._native_public(
            "get_margin_available_inventory",
            self._native_params(currency=currency),
        )

    async def get_margin_loan_market_interest_rate(self, currency: str) -> dict[str, Any]:
        return await self._native_public(
            "get_margin_loan_market_interest_rate",
            self._native_params(currency=currency),
        )

    async def get_cross_margin_account(
        self,
        quoteCurrency: str | None = None,
        queryType: str = "MARGIN",
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_cross_margin_account",
            self._native_params(quoteCurrency=quoteCurrency, queryType=queryType),
        )

    async def get_isolated_margin_account(
        self,
        product_symbol: str | None = None,
        quoteCurrency: str | None = None,
        queryType: str = "ISOLATED",
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_isolated_margin_account",
            self._native_params(
                product_symbol=product_symbol,
                quoteCurrency=quoteCurrency,
                queryType=queryType,
            ),
        )

    async def get_margin_borrow_interest_rate(
        self,
        vipLevel: int | None = None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_margin_borrow_interest_rate",
            self._native_params(vipLevel=vipLevel, currency=currency),
        )

    async def borrow_margin(
        self,
        currency: str,
        size: str,
        timeInForce: str | None = None,
        isIsolated: bool | None = None,
        isHf: bool | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "borrow_margin",
            self._native_params(
                currency=currency,
                size=size,
                timeInForce=timeInForce,
                isIsolated=isIsolated,
                isHf=isHf,
                product_symbol=product_symbol,
            ),
        )

    async def get_margin_borrow_history(
        self,
        currency: str | None = None,
        isIsolated: bool | None = None,
        product_symbol: str | None = None,
        orderNo: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        currentPage: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_margin_borrow_history",
            self._native_params(
                currency=currency,
                isIsolated=isIsolated,
                product_symbol=product_symbol,
                orderNo=orderNo,
                startTime=startTime,
                endTime=endTime,
                currentPage=currentPage,
                pageSize=pageSize,
            ),
        )

    async def repay_margin(
        self,
        currency: str,
        size: str,
        isIsolated: bool | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "repay_margin",
            self._native_params(
                currency=currency,
                size=size,
                isIsolated=isIsolated,
                product_symbol=product_symbol,
            ),
        )

    async def get_margin_repay_history(
        self,
        currency: str | None = None,
        isIsolated: bool | None = None,
        product_symbol: str | None = None,
        orderNo: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        currentPage: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_margin_repay_history",
            self._native_params(
                currency=currency,
                isIsolated=isIsolated,
                product_symbol=product_symbol,
                orderNo=orderNo,
                startTime=startTime,
                endTime=endTime,
                currentPage=currentPage,
                pageSize=pageSize,
            ),
        )

    async def get_margin_interest_history(
        self,
        currency: str | None = None,
        isIsolated: bool | None = None,
        product_symbol: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        currentPage: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_margin_interest_history",
            self._native_params(
                currency=currency,
                isIsolated=isIsolated,
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
                currentPage=currentPage,
                pageSize=pageSize,
            ),
        )

    async def modify_margin_leverage(
        self,
        leverage: str,
        isIsolated: bool | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "modify_margin_leverage",
            self._native_params(
                leverage=leverage,
                isIsolated=isIsolated,
                product_symbol=product_symbol,
            ),
        )

    async def get_margin_loan_market(self, currency: str | None = None) -> dict[str, Any]:
        return await self._native_private(
            "get_margin_loan_market", self._native_params(currency=currency)
        )

    async def purchase_margin_lending(
        self, currency: str, size: str, interestRate: str
    ) -> dict[str, Any]:
        return await self._native_private(
            "purchase_margin_lending",
            self._native_params(currency=currency, size=size, interestRate=interestRate),
        )

    async def modify_margin_lending_purchase(
        self, currency: str, purchaseOrderNo: str, interestRate: str
    ) -> dict[str, Any]:
        return await self._native_private(
            "modify_margin_lending_purchase",
            self._native_params(
                currency=currency,
                purchaseOrderNo=purchaseOrderNo,
                interestRate=interestRate,
            ),
        )

    async def get_margin_lending_purchase_orders(
        self,
        status: str,
        currency: str | None = None,
        purchaseOrderNo: str | None = None,
        currentPage: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_margin_lending_purchase_orders",
            self._native_params(
                status=status,
                currency=currency,
                purchaseOrderNo=purchaseOrderNo,
                currentPage=currentPage,
                pageSize=pageSize,
            ),
        )

    async def redeem_margin_lending(
        self, currency: str, size: str, purchaseOrderNo: str
    ) -> dict[str, Any]:
        return await self._native_private(
            "redeem_margin_lending",
            self._native_params(currency=currency, size=size, purchaseOrderNo=purchaseOrderNo),
        )

    async def get_margin_lending_redeem_orders(
        self,
        status: str,
        currency: str | None = None,
        redeemOrderNo: str | None = None,
        currentPage: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_margin_lending_redeem_orders",
            self._native_params(
                status=status,
                currency=currency,
                redeemOrderNo=redeemOrderNo,
                currentPage=currentPage,
                pageSize=pageSize,
            ),
        )

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        if self._native_client is None:
            raise RuntimeError("KuCoin native client is required for public margin methods.")
        response, data = await request_native_json_async(
            self._native_client,
            "public_request",
            method_name,
            params,
        )
        self._store_response_headers(response)
        return data
