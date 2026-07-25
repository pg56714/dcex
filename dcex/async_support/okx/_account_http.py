from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    async def get_account_instruments(
        self,
        instType: str,
        product_symbol: str | None = None,
        instFamily: str | None = None,
        seriesId: str | None = None,
    ) -> dict[str, Any]:
        """
        Get account instruments information.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            product_symbol: Product symbol.
            instFamily: Instrument family. Only applicable to FUTURES/SWAP/OPTION.
            seriesId: Instrument series identifier.

        Returns:
            Dict containing instruments information
        """
        return await self._native_private(
            "get_account_instruments",
            self._native_params(
                instType=instType,
                product_symbol=product_symbol,
                instFamily=instFamily,
                seriesId=seriesId,
            ),
        )

    async def get_account_balance(
        self,
        ccy: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get account balance information.

        Args:
            ccy: List of currencies to query

        Returns:
            Dict containing account balance information
        """
        return await self._native_private(
            "get_account_balance",
            self._native_params(ccy=ccy),
        )

    async def get_positions(
        self,
        instType: str | None = None,
        product_symbol: str | None = None,
        posId: str | None = None,
    ) -> dict[str, Any]:
        """
        Get positions information.

        Args:
            instType: Instrument type (MARGIN, SWAP, FUTURES, OPTION).
                instId will be checked against instType when both parameters are passed.
            product_symbol: Product symbol

        Returns:
            Dict containing positions information
        """
        return await self._native_private(
            "get_positions",
            self._native_params(instType=instType, product_symbol=product_symbol, posId=posId),
        )

    async def get_positions_history(
        self,
        instType: str | None = None,
        product_symbol: str | None = None,
        posId: str | None = None,
        mgnMode: str | None = None,
        type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get positions history.

        Args:
            instType: Instrument type (MARGIN, SWAP, FUTURES, OPTION)
            product_symbol: Product symbol
            mgnMode: Margin mode (cross, isolated)
            type: Position close type (1: Close position partially; 2: Close all;
                3: Liquidation; 4: Partial liquidation; 5: ADL)
            after: Pagination parameter - records after this ID
            before: Pagination parameter - records before this ID
            limit: Number of results per request (max 100)

        Returns:
            Dict containing positions history
        """
        return await self._native_private(
            "get_positions_history",
            self._native_params(
                instType=instType,
                product_symbol=product_symbol,
                posId=posId,
                mgnMode=mgnMode,
                type=type,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    async def get_position_risk(
        self,
        instType: str | None = None,
    ) -> dict[str, Any]:
        """
        Get position risk information.

        Args:
            instType: Instrument type (MARGIN, SWAP, FUTURES, OPTION)

        Returns:
            Dict containing position risk information
        """
        return await self._native_private(
            "get_position_risk",
            self._native_params(instType=instType),
        )

    async def get_account_bills(
        self,
        instType: str | None = None,
        product_symbol: str | None = None,
        ccy: str | None = None,
        mgnMode: str | None = None,
        ctType: str | None = None,
        type: str | None = None,
        subType: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get account bills details.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            product_symbol: Product symbol
            ccy: Currency
            mgnMode: Margin mode (cross, isolated)
            ctType: Contract type
            type: Bill type
            subType: Bill subtype
            begin: Start time (Unix timestamp in milliseconds)
            end: End time (Unix timestamp in milliseconds)
            limit: Number of results per request (max 100)

        Returns:
            Dict containing account bills information
        """
        return await self._native_private(
            "get_account_bills",
            self._native_params(
                instType=instType,
                product_symbol=product_symbol,
                ccy=ccy,
                mgnMode=mgnMode,
                ctType=ctType,
                type=type,
                subType=subType,
                after=after,
                before=before,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    async def get_account_bills_archive(
        self,
        instType: str | None = None,
        product_symbol: str | None = None,
        ccy: str | None = None,
        mgnMode: str | None = None,
        ctType: str | None = None,
        type: str | None = None,
        subType: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get archived account bills.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            product_symbol: Product symbol
            ccy: Currency
            mgnMode: Margin mode (cross, isolated)
            ctType: Contract type
            type: Bill type
            subType: Bill subtype
            begin: Start time (Unix timestamp in milliseconds)
            end: End time (Unix timestamp in milliseconds)
            limit: Number of results per request (max 100)

        Returns:
            Dict containing archived account bills information
        """
        return await self._native_private(
            "get_account_bills_archive",
            self._native_params(
                instType=instType,
                product_symbol=product_symbol,
                ccy=ccy,
                mgnMode=mgnMode,
                ctType=ctType,
                type=type,
                subType=subType,
                after=after,
                before=before,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    async def get_account_bills_history_archive(
        self,
        year: str,
        quarter: str,
        type: str | None = None,
    ) -> dict[str, Any]:
        """
        Get account bills history archive.

        Args:
            year: Year (e.g., "2023")
            quarter: Quarter (e.g., "Q1", "Q2", "Q3", "Q4")

        Returns:
            Dict containing bills history archive information
        """
        return await self._native_private(
            "get_account_bills_history_archive",
            self._native_params(year=year, quarter=quarter, type=type),
        )

    async def post_account_bills_history_archive(
        self,
        year: str,
        quarter: str,
        type: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate account bills history archive.

        Args:
            year: Year (e.g., "2023")
            quarter: Quarter (e.g., "Q1", "Q2", "Q3", "Q4")

        Returns:
            Dict containing archive generation result
        """
        return await self._native_private(
            "post_account_bills_history_archive",
            self._native_params(year=year, quarter=quarter, type=type),
        )

    async def get_account_config(self) -> dict[str, Any]:
        """
        Get account configuration.

        Returns:
            Dict containing account configuration information
        """
        return await self._native_private("get_account_config", [])

    async def set_position_mode(self, posMode: str) -> dict[str, Any]:
        """
        Set position mode.

        Args:
            posMode: Position mode (long_short_mode, net_mode)

        Returns:
            Dict containing operation result
        """
        return await self._native_private(
            "set_position_mode",
            self._native_params(posMode=posMode),
        )

    async def set_leverage(
        self,
        lever: str,
        mgnMode: str,
        product_symbol: str | None = None,
        ccy: str | None = None,
        posSide: str | None = None,
    ) -> dict[str, Any]:
        """
        Set leverage for trading.

        Args:
            lever: Leverage value
            mgnMode: Margin mode (cross, isolated). Can only be cross if ccy is passed.
            product_symbol: Product symbol. Under cross mode, either instId or ccy is required;
                if both are passed, instId will be used by default.
            ccy: Currency. Only applicable to cross MARGIN of Spot mode/Multi-currency
                margin/Portfolio margin
            posSide: Position side. Only required when margin mode is isolated in
                long/short mode for FUTURES/SWAP.

        Returns:
            Dict containing operation result
        """
        return await self._native_private(
            "set_leverage",
            self._native_params(
                lever=lever,
                mgnMode=mgnMode,
                product_symbol=product_symbol,
                ccy=ccy,
                posSide=posSide,
            ),
        )

    async def get_max_order_size(
        self,
        product_symbol: str,
        tdMode: str,
        ccy: str | None = None,
        px: str | None = None,
        leverage: str | None = None,
        tradeQuoteCcy: str | None = None,
        outcome: str | None = None,
    ) -> dict[str, Any]:
        """
        Get maximum order size.

        Args:
            product_symbol: Product symbol
            tdMode: Trading mode (cross, isolated, cash, spot_isolated)
            ccy: Currency used for margin. Applicable to isolated MARGIN and cross
                MARGIN orders in Spot and futures mode.
            px: Price
            leverage: Leverage value

        Returns:
            Dict containing maximum order size information
        """
        return await self._native_private(
            "get_max_order_size",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                ccy=ccy,
                px=px,
                leverage=leverage,
                tradeQuoteCcy=tradeQuoteCcy,
                outcome=outcome,
            ),
        )

    async def get_max_avail_size(
        self,
        product_symbol: str,
        tdMode: str,
        ccy: str | None = None,
        reduceOnly: str | None = None,
        px: str | None = None,
        tradeQuoteCcy: str | None = None,
    ) -> dict[str, Any]:
        """
        Get maximum available size.

        Args:
            product_symbol: Product symbol
            tdMode: Trading mode (cross, isolated, cash, spot_isolated)
            ccy: Currency. Applicable to isolated MARGIN and cross MARGIN in Spot
                and futures mode.
            reduceOnly: Whether to reduce position only. Only applicable to MARGIN
            px: Price. Only applicable to reduceOnly MARGIN.

        Returns:
            Dict containing maximum available size information
        """
        return await self._native_private(
            "get_max_avail_size",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                ccy=ccy,
                reduceOnly=reduceOnly,
                px=px,
                tradeQuoteCcy=tradeQuoteCcy,
            ),
        )

    async def get_leverage(
        self,
        mgnMode: str,
        product_symbol: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Get leverage information.

        Args:
            mgnMode: Margin mode (cross, isolated)
            product_symbol: Product symbol
            ccy: Currency used for getting leverage of currency level. Applicable to
                cross MARGIN of Spot mode/Multi-currency margin/Portfolio margin.
                Supported single currency or multiple currencies (no more than 20)
                separated with comma.

        Returns:
            Dict containing leverage information
        """
        return await self._native_private(
            "get_leverage",
            self._native_params(mgnMode=mgnMode, product_symbol=product_symbol, ccy=ccy),
        )

    async def get_adjust_leverage(
        self,
        instType: str,
        mgnMode: str,
        lever: str,
        product_symbol: str | None = None,
        ccy: str | None = None,
        posSide: str | None = None,
    ) -> dict[str, Any]:
        """
        Get adjust leverage information.

        Args:
            instType: Instrument type (MARGIN, SWAP, FUTURES)
            mgnMode: Margin mode (cross, isolated)
            lever: Leverage value
            product_symbol: Product symbol
            ccy: Currency
            posSide: Position side (long, short)

        Returns:
            Dict containing adjust leverage information
        """
        return await self._native_private(
            "get_adjust_leverage",
            self._native_params(
                instType=instType,
                mgnMode=mgnMode,
                lever=lever,
                product_symbol=product_symbol,
                ccy=ccy,
                posSide=posSide,
            ),
        )

    async def get_max_loan(
        self,
        mgnMode: str,
        product_symbol: str | None = None,
        ccy: str | None = None,
        mgnCcy: str | None = None,
        tradeQuoteCcy: str | None = None,
    ) -> dict[str, Any]:
        """
        Get maximum loan amount.

        Args:
            mgnMode: Margin mode (cross, isolated)
            product_symbol: Product symbol
            ccy: Currency
            mgnCcy: Margin currency

        Returns:
            Dict containing maximum loan information
        """
        return await self._native_private(
            "get_max_loan",
            self._native_params(
                mgnMode=mgnMode,
                product_symbol=product_symbol,
                ccy=ccy,
                mgnCcy=mgnCcy,
                tradeQuoteCcy=tradeQuoteCcy,
            ),
        )

    async def _request_fee_rates(
        self,
        method_name: str,
        product_symbol: str | None = None,
        instFamily: str | None = None,
        groupId: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            method_name,
            self._native_params(
                product_symbol=product_symbol,
                instFamily=instFamily,
                groupId=groupId,
            ),
        )

    async def get_spot_fee_rates(
        self,
        product_symbol: str | None = None,
        instFamily: str | None = None,
        groupId: str | None = None,
    ) -> dict[str, Any]:
        """Get OKX Spot trading fee rates."""
        return await self._request_fee_rates(
            "get_spot_fee_rates", product_symbol, instFamily, groupId
        )

    async def get_margin_fee_rates(
        self,
        product_symbol: str | None = None,
        instFamily: str | None = None,
        groupId: str | None = None,
    ) -> dict[str, Any]:
        """Get OKX margin trading fee rates."""
        return await self._request_fee_rates(
            "get_margin_fee_rates", product_symbol, instFamily, groupId
        )

    async def get_swap_fee_rates(
        self,
        product_symbol: str | None = None,
        instFamily: str | None = None,
        groupId: str | None = None,
    ) -> dict[str, Any]:
        """Get OKX perpetual-swap trading fee rates."""
        return await self._request_fee_rates(
            "get_swap_fee_rates", product_symbol, instFamily, groupId
        )

    async def get_futures_fee_rates(
        self,
        product_symbol: str | None = None,
        instFamily: str | None = None,
        groupId: str | None = None,
    ) -> dict[str, Any]:
        """Get OKX delivery-futures trading fee rates."""
        return await self._request_fee_rates(
            "get_futures_fee_rates", product_symbol, instFamily, groupId
        )

    async def get_option_fee_rates(
        self,
        product_symbol: str | None = None,
        instFamily: str | None = None,
        groupId: str | None = None,
    ) -> dict[str, Any]:
        """Get OKX option trading fee rates."""
        return await self._request_fee_rates(
            "get_option_fee_rates", product_symbol, instFamily, groupId
        )

    async def get_interest_accrued(
        self,
        type: str | None = None,
        ccy: str | None = None,
        product_symbol: str | None = None,
        mgnMode: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get interest accrued information.

        Args:
            ccy: Currency
            product_symbol: Product symbol
            mgnMode: Margin mode (cross, isolated)
            after: Pagination parameter - records after this ID
            before: Pagination parameter - records before this ID
            limit: Number of results per request (max 100)

        Returns:
            Dict containing interest accrued information
        """
        return await self._native_private(
            "get_interest_accrued",
            self._native_params(
                type=type,
                ccy=ccy,
                product_symbol=product_symbol,
                mgnMode=mgnMode,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    async def get_interest_rate(
        self,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Get interest rate information.

        Args:
            ccy: Currency

        Returns:
            Dict containing interest rate information
        """
        return await self._native_private(
            "get_interest_rate",
            self._native_params(ccy=ccy),
        )

    async def set_greeks(
        self,
        greeksType: str,
    ) -> dict[str, Any]:
        """
        Set Greeks display type.

        Args:
            greeksType: Greeks type (PA: Greeks in coins, BS: Black-Scholes Greeks in dollars)

        Returns:
            Dict containing operation result
        """
        return await self._native_private(
            "set_greeks",
            self._native_params(greeksType=greeksType),
        )

    async def get_max_withdrawal(
        self,
        ccy: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get maximum withdrawal amount.

        Args:
            ccy: List of currencies to query

        Returns:
            Dict containing maximum withdrawal information
        """
        return await self._native_private(
            "get_max_withdrawal",
            self._native_params(ccy=ccy),
        )

    async def get_interest_limits(
        self,
        type: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Get interest limits information.

        Args:
            ccy: Currency

        Returns:
            Dict containing interest limits information
        """
        return await self._native_private(
            "get_interest_limits",
            self._native_params(type=type, ccy=ccy),
        )
