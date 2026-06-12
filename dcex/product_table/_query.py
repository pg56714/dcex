"""
Shared product-table query logic.

The query and indexing methods are pure (no network, no awaiting), so the sync
and async product-table managers share them through
:class:`ProductTableQueryMixin` instead of keeping two identical copies. Each
manager only implements its own fetch/initialise layer.

``ProductTableError`` lives here as the single canonical type; both manager
modules re-export it, so ``except ProductTableError`` works regardless of which
module raised it.
"""

from typing import Any

import polars as pl


class ProductTableError(Exception):
    """Exception raised for product table related errors."""

    pass


class ProductTableQueryMixin:
    """
    Pure query/index helpers over a ``self.product_table`` polars DataFrame.

    Subclasses provide ``self.product_table`` and call :meth:`_build_indexes`
    after (re)loading it. All methods here are synchronous and do no I/O.
    """

    product_table: pl.DataFrame

    @staticmethod
    def _row_matches(
        row: dict[str, Any],
        *,
        product_symbol: str | None = None,
        exchange: str | None = None,
        product_type: str | None = None,
        exchange_type: str | None = None,
        exchange_symbol: str | None = None,
    ) -> bool:
        """Return whether a row satisfies every supplied filter."""
        filters = {
            "product_symbol": product_symbol,
            "exchange": exchange,
            "product_type": product_type,
            "exchange_type": exchange_type,
            "exchange_symbol": exchange_symbol,
        }
        return all(value is None or row.get(column) == value for column, value in filters.items())

    def _build_indexes(self) -> None:
        """Build in-memory indexes to accelerate common lookups."""
        self._by_exchange_product: dict[tuple[str, str], dict[str, Any] | None] = {}
        self._by_exchange_exchange_symbol: dict[tuple[str, str], list[dict[str, Any]]] = {}
        self._by_exchange_exchange_symbol_product_type: dict[
            tuple[str, str, str], dict[str, Any] | None
        ] = {}
        self._by_exchange_exchange_symbol_exchange_type: dict[
            tuple[str, str, str], dict[str, Any] | None
        ] = {}
        self._list_cache: dict[tuple[str, str, str | None, str | None], tuple[str, ...]] = {}

        for row in self.product_table.to_dicts():
            exchange = row.get("exchange")
            product_symbol = row.get("product_symbol")
            exchange_symbol = row.get("exchange_symbol")
            product_type = row.get("product_type")
            exchange_type = row.get("exchange_type")

            if exchange is None or product_symbol is None:
                continue

            product_key = (exchange, product_symbol)
            self._by_exchange_product[product_key] = (
                None if product_key in self._by_exchange_product else row
            )

            if exchange_symbol is not None:
                key_ex = (exchange, exchange_symbol)
                self._by_exchange_exchange_symbol.setdefault(key_ex, []).append(row)

                if product_type is not None:
                    key_pt = (exchange, exchange_symbol, product_type)
                    self._by_exchange_exchange_symbol_product_type[key_pt] = (
                        None if key_pt in self._by_exchange_exchange_symbol_product_type else row
                    )

                if exchange_type is not None:
                    key_et = (exchange, exchange_symbol, exchange_type)
                    self._by_exchange_exchange_symbol_exchange_type[key_et] = (
                        None if key_et in self._by_exchange_exchange_symbol_exchange_type else row
                    )

    def get(
        self,
        key: str,
        product_symbol: str | None = None,
        exchange: str | None = None,
        product_type: str | None = None,
        exchange_type: str | None = None,
        exchange_symbol: str | None = None,
    ) -> str:
        """
        Return a single value of key from product that satisfies the conditions.
        The conditions are case-insensitive (except id_).
        """
        # Fast paths via indexes
        if exchange is not None and product_symbol is not None:
            row = self._by_exchange_product.get((exchange, product_symbol))
            if row is not None and self._row_matches(
                row,
                product_symbol=product_symbol,
                exchange=exchange,
                product_type=product_type,
                exchange_type=exchange_type,
                exchange_symbol=exchange_symbol,
            ):
                if key not in row:
                    raise ProductTableError(f"Key not found: {key}")
                return row[key]

        if exchange is not None and exchange_symbol is not None:
            if product_type is not None:
                row = self._by_exchange_exchange_symbol_product_type.get(
                    (exchange, exchange_symbol, product_type)
                )
                if row is not None and self._row_matches(
                    row,
                    product_symbol=product_symbol,
                    exchange=exchange,
                    product_type=product_type,
                    exchange_type=exchange_type,
                    exchange_symbol=exchange_symbol,
                ):
                    if key not in row:
                        raise ProductTableError(f"Key not found: {key}")
                    return row[key]
            elif exchange_type is not None:
                row = self._by_exchange_exchange_symbol_exchange_type.get(
                    (exchange, exchange_symbol, exchange_type)
                )
                if row is not None and self._row_matches(
                    row,
                    product_symbol=product_symbol,
                    exchange=exchange,
                    product_type=product_type,
                    exchange_type=exchange_type,
                    exchange_symbol=exchange_symbol,
                ):
                    if key not in row:
                        raise ProductTableError(f"Key not found: {key}")
                    return row[key]

        # Fallback to DataFrame filters for general queries
        data = self.product_table
        if product_symbol is not None:
            data = data.filter(pl.col("product_symbol") == product_symbol)
        if exchange is not None:
            data = data.filter(pl.col("exchange") == exchange)
        if product_type is not None:
            data = data.filter(pl.col("product_type") == product_type)
        if exchange_type is not None:
            data = data.filter(pl.col("exchange_type") == exchange_type)
        if exchange_symbol is not None:
            data = data.filter(pl.col("exchange_symbol") == exchange_symbol)

        if data.height > 1:
            raise ProductTableError(
                f"Exist multiple {key} for product_symbol: {product_symbol}, "
                f"exchange: {exchange}, product_type: {product_type}"
            )
        if data.height == 0:
            raise ProductTableError(
                f"Not exist {key} for product_symbol: {product_symbol}, "
                f"exchange: {exchange}, product_type: {product_type}, "
                f"exchange_symbol: {exchange_symbol}"
            )

        return data.select(key).item()

    def get_exchange_symbol(self, exchange: str, product_symbol: str) -> str:
        """
        Get exchange symbol for a product.

        Args:
            exchange: Exchange name
            product_symbol: Product symbol

        Returns:
            str: Exchange-specific symbol
        """
        row = self._by_exchange_product.get((exchange, product_symbol))
        if row is None:
            return self.get("exchange_symbol", product_symbol, exchange)
        value = row.get("exchange_symbol")
        if value is None:
            raise ProductTableError(
                f"Not exist exchange_symbol for product_symbol: {product_symbol}, "
                f"exchange: {exchange}"
            )
        return value

    def get_product_symbol(
        self,
        exchange: str,
        exchange_symbol: str,
        product_type: str | None = None,
        exchange_type: str | None = None,
    ) -> str:
        """
        Get product symbol from exchange symbol.

        Args:
            exchange: Exchange name
            exchange_symbol: Exchange-specific symbol
            product_type: Product type filter
            exchange_type: Exchange type filter

        Returns:
            str: Standardized product symbol
        """
        if product_type is not None and exchange_type is None:
            row = self._by_exchange_exchange_symbol_product_type.get(
                (exchange, exchange_symbol, product_type)
            )
            if row is not None:
                return row["product_symbol"]
            return self.get(
                "product_symbol",
                exchange_symbol=exchange_symbol,
                exchange=exchange,
                product_type=product_type,
            )
        elif product_type is None and exchange_type is not None:
            row = self._by_exchange_exchange_symbol_exchange_type.get(
                (exchange, exchange_symbol, exchange_type)
            )
            if row is not None:
                return row["product_symbol"]
            return self.get(
                "product_symbol",
                exchange_symbol=exchange_symbol,
                exchange=exchange,
                exchange_type=exchange_type,
            )
        elif product_type is not None and exchange_type is not None:
            row = self._by_exchange_exchange_symbol_product_type.get(
                (exchange, exchange_symbol, product_type)
            )
            if row is not None and self._row_matches(
                row,
                exchange=exchange,
                product_type=product_type,
                exchange_type=exchange_type,
                exchange_symbol=exchange_symbol,
            ):
                return row["product_symbol"]
            return self.get(
                "product_symbol",
                exchange_symbol=exchange_symbol,
                exchange=exchange,
                product_type=product_type,
                exchange_type=exchange_type,
            )
        else:
            raise ProductTableError("You must specify either product_type or exchange_type")

    def get_product_type(
        self, exchange: str, product_symbol: str | None = None, exchange_symbol: str | None = None
    ) -> str:
        """
        Get product type for a product.

        Args:
            exchange: Exchange name
            product_symbol: Product symbol (optional)
            exchange_symbol: Exchange symbol (optional)

        Returns:
            str: Product type
        """
        if product_symbol is not None:
            row = self._by_exchange_product.get((exchange, product_symbol))
            if row is not None and row.get("product_type") is not None:
                return row["product_type"]
            return self.get("product_type", product_symbol=product_symbol, exchange=exchange)
        elif exchange_symbol is not None:
            rows = self._by_exchange_exchange_symbol.get((exchange, exchange_symbol))
            if rows and len(rows) == 1 and rows[0].get("product_type") is not None:
                return rows[0]["product_type"]
            return self.get("product_type", exchange_symbol=exchange_symbol, exchange=exchange)
        else:
            raise ProductTableError("You must specify either product_symbol or exchange_symbol")

    def get_exchange_type(
        self, exchange: str, product_symbol: str | None = None, exchange_symbol: str | None = None
    ) -> str:
        """
        Get exchange type for a product.

        Args:
            exchange: Exchange name
            product_symbol: Product symbol (optional)
            exchange_symbol: Exchange symbol (optional)

        Returns:
            str: Exchange type
        """
        if product_symbol is not None:
            row = self._by_exchange_product.get((exchange, product_symbol))
            if row is not None and row.get("exchange_type") is not None:
                return row["exchange_type"]
            return self.get("exchange_type", product_symbol=product_symbol, exchange=exchange)
        elif exchange_symbol is not None:
            rows = self._by_exchange_exchange_symbol.get((exchange, exchange_symbol))
            if rows and len(rows) == 1 and rows[0].get("exchange_type") is not None:
                return rows[0]["exchange_type"]
            return self.get("exchange_type", exchange_symbol=exchange_symbol, exchange=exchange)
        else:
            raise ProductTableError("You must specify either product_symbol or exchange_symbol")

    def get_base_currency(self, exchange: str, product_symbol: str) -> str:
        """
        Get base currency for a product.

        Args:
            exchange: Exchange name
            product_symbol: Product symbol

        Returns:
            str: Base currency
        """
        return self.get("base_currency", product_symbol, exchange)

    def get_quote_currency(self, exchange: str, product_symbol: str) -> str:
        """
        Get quote currency for a product.

        Args:
            exchange: Exchange name
            product_symbol: Product symbol

        Returns:
            str: Quote currency
        """
        return self.get("quote_currency", product_symbol, exchange)

    def get_trading_details(self, exchange: str, product_symbol: str) -> dict[str, Any]:
        """
        Get trading details for a product.

        Args:
            exchange: Exchange name
            product_symbol: Product symbol

        Returns:
            dict: Trading details including precision and limits
        """
        return {
            "price_precision": self.get("price_precision", product_symbol, exchange),
            "size_precision": self.get("size_precision", product_symbol, exchange),
            "min_size": self.get("min_size", product_symbol, exchange),
            "min_notional": self.get("min_notional", product_symbol, exchange),
            "size_per_contract": self.get("size_per_contract", product_symbol, exchange),
        }

    def get_exchange_symbols(
        self, exchange: str, product_type: str | None = None, exchange_type: str | None = None
    ) -> list[str]:
        """
        Get exchange symbols for a given exchange.

        Args:
            exchange: Exchange name
            product_type: Product type filter (optional)
            exchange_type: Exchange type filter (optional)

        Returns:
            list[str]: List of exchange symbols
        """
        cache_key = ("exchange_symbols", exchange, product_type, exchange_type)
        cached = (
            getattr(self, "_list_cache", {}).get(cache_key)
            if hasattr(self, "_list_cache")
            else None
        )
        if cached is not None:
            return list(cached)

        data = self.product_table.filter(pl.col("exchange") == exchange)
        if product_type is not None:
            data = data.filter(pl.col("product_type") == product_type)
        if exchange_type is not None:
            data = data.filter(pl.col("exchange_type") == exchange_type)
        result = data.select("exchange_symbol").to_series().to_list()
        self._list_cache[cache_key] = tuple(result)
        return result

    def get_product_symbols(
        self, exchange: str, product_type: str | None = None, exchange_type: str | None = None
    ) -> list[str]:
        """
        Get product symbols for a given exchange.

        Args:
            exchange: Exchange name
            product_type: Product type filter (optional)
            exchange_type: Exchange type filter (optional)

        Returns:
            list[str]: List of product symbols
        """
        cache_key = ("product_symbols", exchange, product_type, exchange_type)
        cached = (
            getattr(self, "_list_cache", {}).get(cache_key)
            if hasattr(self, "_list_cache")
            else None
        )
        if cached is not None:
            return list(cached)

        data = self.product_table.filter(pl.col("exchange") == exchange)
        if product_type is not None:
            data = data.filter(pl.col("product_type") == product_type)
        if exchange_type is not None:
            data = data.filter(pl.col("exchange_type") == exchange_type)
        result = data.select("product_symbol").to_series().to_list()
        self._list_cache[cache_key] = tuple(result)
        return result
