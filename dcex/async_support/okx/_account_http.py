from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import Account


class AccountHTTP(HTTPManager):
    async def get_account_instruments(
        self,
        instType: str,
        product_symbol: str | None = None,
        instFamily: str | None = None,
        uly: str | None = None,
    ) -> dict[str, Any]:
        """
        Get account instruments information.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            product_symbol: Product symbol. Only applicable to FUTURES/SWAP/OPTION.
                If instType is OPTION, either uly or instFamily is required.
            instFamily: Instrument family. Only applicable to FUTURES/SWAP/OPTION.
                If instType is OPTION, either uly or instFamily is required.
            uly: Underlying asset

        Returns:
            Dict containing instruments information
        """
        payload = {
            "instType": instType,
        }
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if uly is not None:
            payload["uly"] = uly

        res = await self._request(
            method="GET",
            path=Account.GET_INSTRUMENTS,
            query=payload,
        )
        return res

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
        payload = {}
        if ccy is not None:
            coinName = ",".join(ccy)
            payload = {
                "ccy": coinName,
            }

        res = await self._request(
            method="GET",
            path=Account.ACCOUNT_INFO,
            query=payload,
        )
        return res

    async def get_positions(
        self,
        instType: str | None = None,
        product_symbol: str | None = None,
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
        payload = {}
        if instType is not None:
            payload["instType"] = instType
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)

        res = await self._request(
            method="GET",
            path=Account.POSITION_INFO,
            query=payload,
        )
        return res

    async def get_positions_history(
        self,
        instType: str | None = None,
        product_symbol: str | None = None,
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
        payload = {}
        if instType is not None:
            payload["instType"] = instType
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if mgnMode is not None:
            payload["mgnMode"] = mgnMode
        if type is not None:
            payload["type"] = type
        if after is not None:
            payload["after"] = after
        if before is not None:
            payload["before"] = before
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Account.POSITIONS_HISTORY,
            query=payload,
        )
        return res

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
        payload = {}
        if instType is not None:
            payload["instType"] = instType

        res = await self._request(
            method="GET",
            path=Account.POSITION_RISK,
            query=payload,
        )
        return res

    async def get_account_bills(
        self,
        instType: str | None = None,
        product_symbol: str | None = None,
        ccy: str | None = None,
        mgnMode: str | None = None,
        ctType: str | None = None,
        type: str | None = None,
        subType: str | None = None,
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
        payload = {}
        if instType is not None:
            payload["instType"] = instType
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ccy is not None:
            payload["ccy"] = ccy
        if mgnMode is not None:
            payload["mgnMode"] = mgnMode
        if ctType is not None:
            payload["ctType"] = ctType
        if type is not None:
            payload["type"] = type
        if subType is not None:
            payload["subType"] = subType
        if begin is not None:
            payload["begin"] = begin
        if end is not None:
            payload["end"] = end
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Account.BILLS_DETAIL,
            query=payload,
        )
        return res

    async def get_account_bills_archive(
        self,
        instType: str | None = None,
        product_symbol: str | None = None,
        ccy: str | None = None,
        mgnMode: str | None = None,
        ctType: str | None = None,
        type: str | None = None,
        subType: str | None = None,
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
        payload = {}
        if instType is not None:
            payload["instType"] = instType
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ccy is not None:
            payload["ccy"] = ccy
        if mgnMode is not None:
            payload["mgnMode"] = mgnMode
        if ctType is not None:
            payload["ctType"] = ctType
        if type is not None:
            payload["type"] = type
        if subType is not None:
            payload["subType"] = subType
        if begin is not None:
            payload["begin"] = begin
        if end is not None:
            payload["end"] = end
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Account.BILLS_ARCHIVE,
            query=payload,
        )
        return res

    async def get_account_bills_history_archive(
        self,
        year: str,
        quarter: str,
    ) -> dict[str, Any]:
        """
        Get account bills history archive.

        Args:
            year: Year (e.g., "2023")
            quarter: Quarter (e.g., "Q1", "Q2", "Q3", "Q4")

        Returns:
            Dict containing bills history archive information
        """
        payload = {
            "year": year,
            "quarter": quarter,
        }

        res = await self._request(
            method="GET",
            path=Account.BILLS_HISTORY_ARCHIVE,
            query=payload,
        )
        return res

    async def post_account_bills_history_archive(
        self,
        year: str,
        quarter: str,
    ) -> dict[str, Any]:
        """
        Generate account bills history archive.

        Args:
            year: Year (e.g., "2023")
            quarter: Quarter (e.g., "Q1", "Q2", "Q3", "Q4")

        Returns:
            Dict containing archive generation result
        """
        payload = {
            "year": year,
            "quarter": quarter,
        }

        res = await self._request(
            method="POST",
            path=Account.BILLS_HISTORY_ARCHIVE,
            query=payload,
        )
        return res

    async def get_account_config(self) -> dict[str, Any]:
        """
        Get account configuration.

        Returns:
            Dict containing account configuration information
        """
        res = await self._request(
            method="GET",
            path=Account.ACCOUNT_CONFIG,
            query={},
        )
        return res

    async def set_position_mode(self, posMode: str) -> dict[str, Any]:
        """
        Set position mode.

        Args:
            posMode: Position mode (long_short_mode, net_mode)

        Returns:
            Dict containing operation result
        """
        payload = {
            "posMode": posMode,
        }

        res = await self._request(
            method="POST",
            path=Account.POSITION_MODE,
            query=payload,
        )
        return res

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
        payload = {
            "lever": lever,
            "mgnMode": mgnMode,
        }
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ccy is not None:
            payload["ccy"] = ccy
        if posSide is not None:
            payload["posSide"] = posSide

        res = await self._request(
            method="POST",
            path=Account.SET_LEVERAGE,
            query=payload,
        )
        return res

    async def get_max_order_size(
        self,
        product_symbol: str,
        tdMode: str,
        ccy: str | None = None,
        px: str | None = None,
        leverage: str | None = None,
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
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
            "tdMode": tdMode,
        }
        if ccy is not None:
            payload["ccy"] = ccy
        if px is not None:
            payload["px"] = px
        if leverage is not None:
            payload["leverage"] = leverage

        res = await self._request(
            method="GET",
            path=Account.MAX_TRADE_SIZE,
            query=payload,
        )
        return res

    async def get_max_avail_size(
        self,
        product_symbol: str,
        tdMode: str,
        ccy: str | None = None,
        reduceOnly: str | None = None,
        px: str | None = None,
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
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
            "tdMode": tdMode,
        }
        if ccy is not None:
            payload["ccy"] = ccy
        if reduceOnly is not None:
            payload["reduceOnly"] = reduceOnly
        if px is not None:
            payload["px"] = px

        res = await self._request(
            method="GET",
            path=Account.MAX_AVAIL_SIZE,
            query=payload,
        )
        return res

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
        payload = {
            "mgnMode": mgnMode,
        }
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ccy is not None:
            payload["ccy"] = ccy

        res = await self._request(
            method="GET",
            path=Account.GET_LEVERAGE,
            query=payload,
        )
        return res

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
        payload = {
            "instType": instType,
            "mgnMode": mgnMode,
            "lever": lever,
        }
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ccy is not None:
            payload["ccy"] = ccy
        if posSide is not None:
            payload["posSide"] = posSide

        res = await self._request(
            method="GET",
            path=Account.GET_ADJUST_LEVERAGE,
            query=payload,
        )
        return res

    async def get_max_loan(
        self,
        mgnMode: str,
        product_symbol: str | None = None,
        ccy: str | None = None,
        mgnCcy: str | None = None,
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
        payload = {
            "mgnMode": mgnMode,
        }
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ccy is not None:
            payload["ccy"] = ccy
        if mgnCcy is not None:
            payload["mgnCcy"] = mgnCcy

        res = await self._request(
            method="GET",
            path=Account.MAX_LOAN,
            query=payload,
        )
        return res

    async def get_fee_rates(
        self,
        instType: str,
        ruleType: str | None = None,
        product_symbol: str | None = None,
        uly: str | None = None,
        instFamily: str | None = None,
    ) -> dict[str, Any]:
        """
        Get trading fee rates.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            ruleType: Trading rule types. normal: normal trading, pre_market:
                pre-market trading. ruleType can not be passed through together
                with product_symbol/instFamily/uly
            product_symbol: Product symbol
            uly: Underlying asset
            instFamily: Instrument family

        Returns:
            Dict containing fee rates information
        """
        payload = {
            "instType": instType,
        }
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if ruleType is not None:
            payload["ruleType"] = ruleType

        res = await self._request(
            method="GET",
            path=Account.FEE_RATES,
            query=payload,
        )
        return res

    async def get_interest_accrued(
        self,
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
        payload = {}
        if ccy is not None:
            payload["ccy"] = ccy
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if mgnMode is not None:
            payload["mgnMode"] = mgnMode
        if after is not None:
            payload["after"] = after
        if before is not None:
            payload["before"] = before
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Account.INTEREST_ACCRUED,
            query=payload,
        )
        return res

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
        payload = {}
        if ccy is not None:
            payload["ccy"] = ccy

        res = await self._request(
            method="GET",
            path=Account.INTEREST_RATE,
            query=payload,
        )
        return res

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
        payload = {
            "greeksType": greeksType,
        }

        res = await self._request(
            method="POST",
            path=Account.SET_GREEKS,
            query=payload,
        )
        return res

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
        payload = {}
        if ccy is not None:
            ccyName = ",".join(ccy)
            payload = {
                "ccy": ccyName,
            }

        res = await self._request(
            method="GET",
            path=Account.MAX_WITHDRAWAL,
            query=payload,
        )
        return res

    async def get_interest_limits(
        self,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Get interest limits information.

        Args:
            ccy: Currency

        Returns:
            Dict containing interest limits information
        """
        payload = {}
        if ccy is not None:
            payload["ccy"] = ccy

        res = await self._request(
            method="GET",
            path=Account.INTEREST_LIMITS,
            query=payload,
        )
        return res

    async def set_auto_loan(
        self,
        autoLoan: str,
    ) -> dict[str, Any]:
        """
        Set auto loan feature.

        Args:
            autoLoan: Whether to enable auto loan

        Returns:
            Dict containing operation result
        """
        kwargs = {
            "autoLoan": autoLoan,
        }

        res = await self._request(
            method="POST",
            path=Account.SET_AUTO_LOAN,
            query=kwargs,
        )
        return res
