"""
Product table management module.

This module provides the ProductTableManager class for managing exchange product
mapping tables and standardized product information across different exchanges.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import polars as pl

from .fetch import binance, bitmart, bitmex, bybit, gateio, okx

VALID_EXCHANGES = [
    binance,
    bitmart,
    bitmex,
    bybit,
    gateio,
    okx,
]


class ProductTableError(Exception):
    """Exception raised for product table related errors."""

    pass


class ProductTableManager:
    """
    Exchange Product Mapping Table.

    This table provides a structured mapping between product symbols and their
    corresponding exchange-specific symbols, along with key trading attributes.
    It helps standardize the representation of products across different exchanges.

    Columns:
        - product_symbol: Standardized product identifier used internally.
        - exchange_symbol: The product symbol as recognized on the exchange.
        - exchange: The name of the exchange where the product is traded.
        - product_type: The category of the product (e.g., SPOT, SWAP, FUTURES).
        - price_precision: The decimal precision allowed for price values (if applicable).
        - size_precision: The decimal precision allowed for order sizes (if applicable).
        - contract_value: The notional value of one contract (for derivatives).
        - min_size: The minimum order size allowed on the exchange.
        - min_notional: The minimum notional value required for an order.

    Example:
        | product_symbol  | exchange_symbol | exchange | product_type |
        | price_precision | size_precision | contract_value | min_size |
        | min_notional |
        |-----------------|-----------------|----------|--------------|
        |-----------------|----------------|----------------|----------|
        |--------------|
        | BTC-USDT-SPOT   | BTC/USDT        | BINANCE  | SPOT         |
        | 0.01            | 0.0001         | N/A            | 0.0001   |
        | 10           |
        | BTC-USD-SWAP    | BTCUSDT         | BINANCE  | SWAP         |
        | 0.1             | 0.001          | 100 USD        | 0.001    |
        | 5            |
        | BTC-USD-FUTURES | BTC-USD-SWAP    | OKX      | FUTURES      |
        | 0.01            | 0.0001         | 10 USD         | 0.0001   |
        | 1            |

    Use this mapping to correctly interpret product symbols and their attributes
    when integrating with multiple exchanges.
    """

    _instance = {}

    @classmethod
    def get_instance(cls, exchange_name: str | None = None) -> "ProductTableManager":
        """
        Get or create a ProductTableManager instance for the specified exchange.

        Args:
            exchange_name: Name of the exchange to initialize for

        Returns:
            ProductTableManager: The singleton instance
        """
        if exchange_name not in cls._instance:
            cls._instance[exchange_name] = cls()
            cls._instance[exchange_name]._initialize(exchange_name=exchange_name)
        return cls._instance[exchange_name]

    def _initialize(self, exchange_name: str | None = None) -> None:
        """Initialize the product table by fetching data from valid exchanges."""
        self.product_table = self._fetch_product_tables(exchange_name)
        self._build_indexes()

    def _fetch_product_tables(self, exchange_name: str | None = None) -> pl.DataFrame:
        """
        Fetch product tables from all valid exchanges and combine them into a single DataFrame.
        """
        functions = (
            list(VALID_EXCHANGES)
            if exchange_name is None
            else [func for func in VALID_EXCHANGES if func.__name__ == exchange_name]
        )

        tables: list[pl.DataFrame] = []
        # Use threads to parallelize synchronous HTTP calls
        with ThreadPoolExecutor(max_workers=min(8, max(1, len(functions)))) as executor:
            future_to_name = {executor.submit(func): func.__name__ for func in functions}
            for future in as_completed(future_to_name):
                try:
                    table = future.result()
                    if isinstance(table, pl.DataFrame):
                        tables.append(table)
                except Exception as exc:
                    # Skip failed exchanges; align with async version behavior
                    _ = exc  # avoid unused var warning
                    continue

        if not tables:
            raise ProductTableError("Failed to fetch product tables from any exchange")

        return pl.concat(tables, how="vertical")

    def _build_indexes(self) -> None:
        """Build in-memory indexes to accelerate common lookups."""
        self._by_exchange_product: dict[tuple[str, str], dict[str, Any]] = {}
        self._by_exchange_exchange_symbol: dict[tuple[str, str], list[dict[str, Any]]] = {}
        self._by_exchange_exchange_symbol_product_type: dict[
            tuple[str, str, str], dict[str, Any]
        ] = {}
        self._by_exchange_exchange_symbol_exchange_type: dict[
            tuple[str, str, str], dict[str, Any]
        ] = {}
        self._list_cache: dict[tuple[str, str, str | None, str | None], list[str]] = {}

        for row in self.product_table.to_dicts():
            exchange = row.get("exchange")
            product_symbol = row.get("product_symbol")
            exchange_symbol = row.get("exchange_symbol")
            product_type = row.get("product_type")
            exchange_type = row.get("exchange_type")

            if exchange is None or product_symbol is None:
                continue

            self._by_exchange_product[(exchange, product_symbol)] = row

            if exchange_symbol is not None:
                key_ex = (exchange, exchange_symbol)
                self._by_exchange_exchange_symbol.setdefault(key_ex, []).append(row)

                if product_type is not None:
                    key_pt = (exchange, exchange_symbol, product_type)
                    self._by_exchange_exchange_symbol_product_type[key_pt] = row

                if exchange_type is not None:
                    key_et = (exchange, exchange_symbol, exchange_type)
                    self._by_exchange_exchange_symbol_exchange_type[key_et] = row

    def refresh(self, exchange_name: str | None = None) -> None:
        """
        Refresh product table and indexes.

        If exchange_name is provided, only that exchange is fetched.
        """
        self._initialize(exchange_name=exchange_name)

    # Removed async client context; sync manager does not maintain async clients

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
            if row is not None:
                if key not in row:
                    raise ProductTableError(f"Key not found: {key}")
                return row[key]

        if exchange is not None and exchange_symbol is not None:
            if product_type is not None:
                row = self._by_exchange_exchange_symbol_product_type.get(
                    (exchange, exchange_symbol, product_type)
                )
                if row is not None:
                    if key not in row:
                        raise ProductTableError(f"Key not found: {key}")
                    return row[key]
            elif exchange_type is not None:
                row = self._by_exchange_exchange_symbol_exchange_type.get(
                    (exchange, exchange_symbol, exchange_type)
                )
                if row is not None:
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
            # Prefer product_type if both provided
            row = self._by_exchange_exchange_symbol_product_type.get(
                (exchange, exchange_symbol, product_type)
            )
            if row is None:
                row = self._by_exchange_exchange_symbol_exchange_type.get(
                    (exchange, exchange_symbol, exchange_type)
                )
            if row is not None:
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
            return cached

        data = self.product_table.filter(pl.col("exchange") == exchange)
        if product_type is not None:
            data = data.filter(pl.col("product_type") == product_type)
        if exchange_type is not None:
            data = data.filter(pl.col("exchange_type") == exchange_type)
        result = data.select("exchange_symbol").to_series().to_list()
        self._list_cache[cache_key] = result
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
            return cached

        data = self.product_table.filter(pl.col("exchange") == exchange)
        if product_type is not None:
            data = data.filter(pl.col("product_type") == product_type)
        if exchange_type is not None:
            data = data.filter(pl.col("exchange_type") == exchange_type)
        result = data.select("product_symbol").to_series().to_list()
        self._list_cache[cache_key] = result
        return result
