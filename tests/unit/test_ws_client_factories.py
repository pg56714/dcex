"""Offline coverage for ws client factories."""
# ruff: noqa: D103

from dcex.ws import bitget, bybit


def test_websocket_factories_select_documented_domains() -> None:
    trade = bybit.trade("key", "secret")
    assert trade._native_client is not None
    rfq = bybit.public(category="rfq")
    assert rfq._native_client is not None
    reality = bitget.reality_private("key", "secret", "passphrase")
    assert reality._native_client is not None
