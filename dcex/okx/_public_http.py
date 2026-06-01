from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.public import Public


class PublicHTTP(HTTPManager):
    def get_public_instruments(
        self,
        instType: str,
        uly: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get public instrument information.

        Args:
            instType: Instrument type
            uly: Underlying asset symbol
            instFamily: Instrument family
            product_symbol: Product symbol

        Returns:
            Dictionary containing instrument information.
        """
        payload: dict[str, Any] = {
            "instType": instType,
        }
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)

        res = self._request(
            method="GET",
            path=Public.GET_INSTRUMENT_INFO,
            query=payload,
            signed=False,
        )
        return res

    def get_funding_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Get current funding rate for a trading pair.

        Args:
            product_symbol: Trading pair symbol

        Returns:
            Dictionary containing funding rate information.
        """
        payload: dict[str, Any] = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }

        res = self._request(
            method="GET",
            path=Public.GET_FUNDING_RATE,
            query=payload,
            signed=False,
        )
        return res

    def get_funding_rate_history(
        self,
        product_symbol: str,
        before: str | None = None,
        after: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get historical funding rates for a trading pair.

        Args:
            product_symbol: Trading pair symbol
            before: Pagination parameter - timestamp before this value
            after: Pagination parameter - timestamp after this value
            limit: Number of results to return

        Returns:
            Dictionary containing historical funding rate data.
        """
        payload: dict[str, Any] = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }
        if before is not None:
            payload["before"] = before
        if after is not None:
            payload["after"] = after
        if limit is not None:
            payload["limit"] = limit

        res = self._request(
            method="GET",
            path=Public.GET_FUNDING_RATE_HISTORY,
            query=payload,
            signed=False,
        )
        return res

    def get_open_interest(
        self,
        instType: str = "SWAP",
        uly: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get public open interest data."""
        payload: dict[str, Any] = {"instType": instType}
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)

        res = self._request(
            method="GET",
            path=Public.GET_OPEN_INTEREST,
            query=payload,
            signed=False,
        )
        return res

    def get_position_tiers(
        self,
        instType: str = "SWAP",
        tdMode: str = "isolated",
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ccy: str | None = None,
        tier: str | None = None,
    ) -> dict[str, Any]:
        """
        Get position tiers information.

        Args:
            instType: Instrument type.
            tdMode: Trading mode.
            instFamily: Instrument family.
            product_symbol: Trading pair symbol.
            ccy: Currency.
            tier: Tier level.

        Returns:
            Dictionary containing position tiers information.
        """
        payload: dict[str, Any] = {"instType": instType, "tdMode": tdMode}
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ccy is not None:
            payload["ccy"] = ccy
        if tier is not None:
            payload["tier"] = tier

        res = self._request(
            method="GET",
            path=Public.GET_POSITION_TIERS,
            query=payload,
            signed=False,
        )
        return res

    def get_trading_data_support_coin(self) -> dict[str, Any]:
        """Get currencies supported by OKX trading data endpoints."""
        res = self._request(
            method="GET",
            path=Public.GET_TRADING_DATA_SUPPORT_COIN,
            query={},
            signed=False,
        )
        return res

    def get_taker_volume(
        self,
        ccy: str,
        instType: str = "SPOT",
        begin: int | None = None,
        end: int | None = None,
        period: str = "5m",
    ) -> dict[str, Any]:
        """Get taker volume by currency and instrument type."""
        payload: dict[str, Any] = {
            "ccy": ccy,
            "instType": instType,
            "period": period,
        }
        if begin is not None:
            payload["begin"] = str(begin)
        if end is not None:
            payload["end"] = str(end)

        res = self._request(
            method="GET",
            path=Public.GET_TAKER_VOLUME,
            query=payload,
            signed=False,
        )
        return res

    def get_contract_taker_volume(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get contract taker volume history."""
        payload: dict[str, Any] = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
            "period": period,
        }
        if begin is not None:
            payload["begin"] = str(begin)
        if end is not None:
            payload["end"] = str(end)

        res = self._request(
            method="GET",
            path=Public.GET_CONTRACT_TAKER_VOLUME,
            query=payload,
            signed=False,
        )
        return res

    def get_long_short_ratio(
        self,
        ccy: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get long and short account ratio by currency."""
        payload: dict[str, Any] = {"ccy": ccy, "period": period}
        if begin is not None:
            payload["begin"] = str(begin)
        if end is not None:
            payload["end"] = str(end)

        res = self._request(
            method="GET",
            path=Public.GET_LONG_SHORT_RATIO,
            query=payload,
            signed=False,
        )
        return res

    def get_contract_long_short_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get contract long and short account ratio."""
        payload: dict[str, Any] = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
            "period": period,
        }
        if begin is not None:
            payload["begin"] = str(begin)
        if end is not None:
            payload["end"] = str(end)

        res = self._request(
            method="GET",
            path=Public.GET_CONTRACT_LONG_SHORT_RATIO,
            query=payload,
            signed=False,
        )
        return res

    def get_top_trader_long_short_account_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get top trader contract long and short account ratio."""
        payload: dict[str, Any] = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
            "period": period,
        }
        if begin is not None:
            payload["begin"] = str(begin)
        if end is not None:
            payload["end"] = str(end)

        res = self._request(
            method="GET",
            path=Public.GET_TOP_TRADER_LONG_SHORT_ACCOUNT_RATIO,
            query=payload,
            signed=False,
        )
        return res

    def get_top_trader_long_short_position_ratio(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get top trader contract long and short position ratio."""
        payload: dict[str, Any] = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
            "period": period,
        }
        if begin is not None:
            payload["begin"] = str(begin)
        if end is not None:
            payload["end"] = str(end)

        res = self._request(
            method="GET",
            path=Public.GET_TOP_TRADER_LONG_SHORT_POSITION_RATIO,
            query=payload,
            signed=False,
        )
        return res

    def get_contracts_open_interest_and_volume(
        self,
        ccy: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get contracts open interest and volume by currency."""
        payload: dict[str, Any] = {"ccy": ccy, "period": period}
        if begin is not None:
            payload["begin"] = str(begin)
        if end is not None:
            payload["end"] = str(end)

        res = self._request(
            method="GET",
            path=Public.GET_CONTRACTS_OPEN_INTEREST_VOLUME,
            query=payload,
            signed=False,
        )
        return res

    def get_contract_open_interest_history(
        self,
        product_symbol: str,
        period: str = "5m",
        begin: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get contract open interest history."""
        payload: dict[str, Any] = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
            "period": period,
        }
        if begin is not None:
            payload["begin"] = str(begin)
        if end is not None:
            payload["end"] = str(end)

        res = self._request(
            method="GET",
            path=Public.GET_CONTRACT_OPEN_INTEREST_HISTORY,
            query=payload,
            signed=False,
        )
        return res
