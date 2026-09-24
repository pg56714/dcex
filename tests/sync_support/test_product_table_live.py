"""Read-only product discovery checks across every supported exchange."""

import pytest

from dcex import _native


@pytest.mark.parametrize("exchange", _native.exchange_names())
def test_public_product_table_is_available(exchange: str) -> None:
    """Each registered exchange must expose at least one public market."""
    table = _native.fetch_product_table(exchange, timeout=15.0)
    assert table.height > 0
    if exchange == "lighter":
        networks = {row["exchange"] for row in table.rows()}
        assert {"lighter", "lighter_robinhood"} <= networks
