"""Python compatibility layer for the Rust product table."""

from pathlib import Path
from typing import Any, cast

from .. import _native


class ProductTableError(Exception):
    """Exception raised for product table related errors."""


class ProductTableQueryMixin:
    """Expose the existing Python query API through the Rust product table."""

    product_table: _native.ProductTable
    _native_table: _native.ProductTable

    def _build_indexes(self) -> None:
        """Build the Rust indexes from the current table rows."""
        self.product_table = _coerce_product_table(self.product_table)
        self._native_table = self.product_table

    @property
    def df(self) -> _native.ProductTable:
        """Return the native product table kept for source compatibility."""
        return self.product_table

    def rows(self) -> list[dict[str, str]]:
        """Return product table rows."""
        return self.product_table.to_dicts()

    def to_dicts(self) -> list[dict[str, str]]:
        """Return product table rows."""
        return self.rows()

    def write_csv(self, path: str | Path) -> None:
        """Write product table rows to CSV."""
        self.product_table.write_csv(path)

    def _call(self, method: str, *args: object, **kwargs: object) -> Any:  # noqa: ANN401
        try:
            return getattr(self._native_table, method)(*args, **kwargs)
        except ValueError as exc:
            raise ProductTableError(str(exc)) from exc

    def get(
        self,
        key: str,
        product_symbol: str | None = None,
        exchange: str | None = None,
        product_type: str | None = None,
        exchange_type: str | None = None,
        exchange_symbol: str | None = None,
    ) -> str:
        """Return one product-table field matching all supplied filters."""
        return self._call(
            "get",
            key,
            product_symbol,
            exchange,
            product_type,
            exchange_type,
            exchange_symbol,
        )

    def get_exchange_symbol(self, exchange: str, product_symbol: str) -> str:
        """Return the exchange-specific symbol for a canonical product symbol."""
        return self._call("get_exchange_symbol", str(exchange), product_symbol)

    def get_product_symbol(
        self,
        exchange: str,
        exchange_symbol: str,
        product_type: str | None = None,
        exchange_type: str | None = None,
    ) -> str:
        """Return the canonical product symbol for an exchange-specific symbol."""
        return self._call(
            "get_product_symbol",
            str(exchange),
            exchange_symbol,
            product_type,
            exchange_type,
        )

    def get_product_type(
        self,
        exchange: str,
        product_symbol: str | None = None,
        exchange_symbol: str | None = None,
    ) -> str:
        """Return the canonical product type."""
        return self._call(
            "get_product_type",
            str(exchange),
            product_symbol,
            exchange_symbol,
        )

    def get_exchange_type(
        self,
        exchange: str,
        product_symbol: str | None = None,
        exchange_symbol: str | None = None,
    ) -> str:
        """Return the exchange-specific product type."""
        return self._call(
            "get_exchange_type",
            str(exchange),
            product_symbol,
            exchange_symbol,
        )

    def get_base_currency(self, exchange: str, product_symbol: str) -> str:
        """Return the base currency."""
        return self._call("get_base_currency", str(exchange), product_symbol)

    def get_quote_currency(self, exchange: str, product_symbol: str) -> str:
        """Return the quote currency."""
        return self._call("get_quote_currency", str(exchange), product_symbol)

    def get_trading_details(self, exchange: str, product_symbol: str) -> dict[str, str]:
        """Return precision, minimum size and contract details."""
        return self._call("get_trading_details", str(exchange), product_symbol)

    def get_exchange_symbols(
        self,
        exchange: str,
        product_type: str | None = None,
        exchange_type: str | None = None,
    ) -> list[str]:
        """Return exchange symbols matching the supplied filters."""
        return self._call(
            "get_exchange_symbols",
            str(exchange),
            product_type,
            exchange_type,
        )

    def get_product_symbols(
        self,
        exchange: str,
        product_type: str | None = None,
        exchange_type: str | None = None,
    ) -> list[str]:
        """Return canonical product symbols matching the supplied filters."""
        return self._call(
            "get_product_symbols",
            str(exchange),
            product_type,
            exchange_type,
        )


def _coerce_product_table(value: object) -> _native.ProductTable:
    if isinstance(value, _native.ProductTable):
        return value
    return _native.ProductTable(cast("list[dict[str, str]]", value))
