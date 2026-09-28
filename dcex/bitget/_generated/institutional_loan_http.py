"""Generated bitget institutional loan HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedInstitutionalLoanHTTP(MarketHTTP):
    """Institutional loan API methods."""

    def classic_instloan_account_get_ltv(
        self, *, risk_unit_id: str | None = None
    ) -> dict[str, Any]:
        """
        Get LTV.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-account/classic-instloan-account#get-ltv
        """
        return self._native_private(
            "classic_instloan_account_get_ltv", self._native_params(**{"riskUnitId": risk_unit_id})
        )

    def classic_instloan_account_bind_risk_unit(
        self, *, uid: str, operate: str, risk_unit_id: str | None = None
    ) -> dict[str, Any]:
        """
        Bind/Unbind Sub-account UID to Risk Unit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-account/classic-instloan-account#bind-unbind-sub-account-uid-to-risk-unit
        """
        return self._native_private(
            "classic_instloan_account_bind_risk_unit",
            self._native_params(**{"uid": uid, "operate": operate, "riskUnitId": risk_unit_id}),
        )

    def classic_instloan_account_get_risk_unit(self) -> dict[str, Any]:
        """
        Get Risk Unit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-account/classic-instloan-account#get-risk-unit
        """
        return self._native_private(
            "classic_instloan_account_get_risk_unit", self._native_params(**{})
        )

    def classic_instloan_orders_get_loan_orders(
        self,
        *,
        order_id: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Loan Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-orders/classic-instloan-orders#get-loan-orders
        """
        return self._native_private(
            "classic_instloan_orders_get_loan_orders",
            self._native_params(
                **{"orderId": order_id, "startTime": start_time, "endTime": end_time}
            ),
        )

    def classic_instloan_orders_get_repayment_orders(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Repayment Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-orders/classic-instloan-orders#get-repayment-orders
        """
        return self._native_private(
            "classic_instloan_orders_get_repayment_orders",
            self._native_params(**{"startTime": start_time, "endTime": end_time, "limit": limit}),
        )

    def classic_instloan_public_get_product_info(self, *, product_id: str) -> dict[str, Any]:
        """
        Get Product Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-public/classic-instloan-public#get-product-info
        """
        return self._native_private(
            "classic_instloan_public_get_product_info",
            self._native_params(**{"productId": product_id}),
        )

    def classic_instloan_public_get_margin_coin_info(self, *, product_id: str) -> dict[str, Any]:
        """
        Get Margin Coin Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-public/classic-instloan-public#get-margin-coin-info
        """
        return self._native_private(
            "classic_instloan_public_get_margin_coin_info",
            self._native_params(**{"productId": product_id}),
        )

    def classic_instloan_public_get_spot_symbols(self, *, product_id: str) -> dict[str, Any]:
        """
        Get Spot Symbols.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-instloan-public/classic-instloan-public#get-spot-symbols
        """
        return self._native_private(
            "classic_instloan_public_get_spot_symbols",
            self._native_params(**{"productId": product_id}),
        )

    def institutional_loan_bind_uid(
        self, *, uid: str, operate: str, risk_unit_id: str | None = None
    ) -> dict[str, Any]:
        """
        Bind/Unbind UID to Risk Unit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#bind-unbind-uid-to-risk-unit
        """
        return self._native_private(
            "institutional_loan_bind_uid",
            self._native_params(**{"uid": uid, "operate": operate, "riskUnitId": risk_unit_id}),
        )

    def institutional_loan_get_margin_coin_info(self, *, product_id: str) -> dict[str, Any]:
        """
        Get Margin Coin Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-margin-coin-info
        """
        return self._native_private(
            "institutional_loan_get_margin_coin_info",
            self._native_params(**{"productId": product_id}),
        )

    def institutional_loan_get_ltv(self, *, risk_unit_id: str | None = None) -> dict[str, Any]:
        """
        Get LTV.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-ltv
        """
        return self._native_private(
            "institutional_loan_get_ltv", self._native_params(**{"riskUnitId": risk_unit_id})
        )

    def institutional_loan_get_loan_orders(
        self,
        *,
        order_id: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Loan Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-loan-orders
        """
        return self._native_private(
            "institutional_loan_get_loan_orders",
            self._native_params(
                **{"orderId": order_id, "startTime": start_time, "endTime": end_time}
            ),
        )

    def institutional_loan_get_product_info(self, *, product_id: str) -> dict[str, Any]:
        """
        Get Product Info.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-product-info
        """
        return self._native_private(
            "institutional_loan_get_product_info", self._native_params(**{"productId": product_id})
        )

    def institutional_loan_get_repayment_orders(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Repayment Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-repayment-orders
        """
        return self._native_private(
            "institutional_loan_get_repayment_orders",
            self._native_params(**{"startTime": start_time, "endTime": end_time, "limit": limit}),
        )

    def institutional_loan_get_risk_unit(self) -> dict[str, Any]:
        """
        Get Risk Unit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-risk-unit
        """
        return self._native_private("institutional_loan_get_risk_unit", self._native_params(**{}))

    def institutional_loan_get_trade_symbols(self, *, product_id: str) -> dict[str, Any]:
        """
        Get Trade Symbols.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/institutional-loan/loan#get-trade-symbols
        """
        return self._native_private(
            "institutional_loan_get_trade_symbols", self._native_params(**{"productId": product_id})
        )
