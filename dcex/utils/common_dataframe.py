"""Common DataFrame utilities for data conversion."""

from typing import Any

import polars as pl


def to_dataframe(
    data: list[dict[str, Any]] | dict[str, Any] | None, schema: list[str] | None = None
) -> pl.DataFrame:
    """
    Convert data to a Polars DataFrame.

    Args:
        data: Input data to convert to DataFrame
        schema: Optional schema for the DataFrame

    Returns:
        pl.DataFrame: The converted DataFrame
    """
    if not data:
        return pl.DataFrame()

    if isinstance(data, list):
        if schema:
            return pl.DataFrame(data, schema=schema, orient="row")
        elif all(isinstance(item, dict) for item in data):
            return pl.DataFrame(data)
        else:
            return pl.DataFrame(data, orient="row")

    if isinstance(data, dict):
        return pl.DataFrame([data])

    return pl.DataFrame()
