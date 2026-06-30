# ruff: noqa: ANN001, ANN201, D100, D103

import os
from contextlib import suppress

import pytest
from dotenv import load_dotenv

from dcex.aster.client import Client

load_dotenv()

ASTER_USER_ADDRESS = os.getenv("ASTER_USER_ADDRESS")
ASTER_SIGNER_ADDRESS = os.getenv("ASTER_SIGNER_ADDRESS")
ASTER_PRIVATE_KEY = os.getenv("ASTER_PRIVATE_KEY")
FUTURES_SYMBOL = "ASTERUSDT"

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run Aster account mutation tests.",
    ),
]


@pytest.fixture
def client():
    client_instance = Client(
        user_address=ASTER_USER_ADDRESS,
        signer_address=ASTER_SIGNER_ADDRESS,
        private_key=ASTER_PRIVATE_KEY,
        preload_product_table=False,
        timeout=20,
    )
    try:
        yield client_instance
    finally:
        client_instance.close()


def _assert_response(response: object) -> None:
    assert isinstance(response, dict | list | bool)


def _require_idle_account(client: Client) -> None:
    if client.get_futures_open_orders():
        pytest.fail("Aster has existing futures open orders.", pytrace=False)
    positions = client.get_futures_position_risk()
    assert isinstance(positions, list)
    if any(float(position.get("positionAmt", 0)) != 0 for position in positions):
        pytest.fail("Aster has an existing futures position.", pytrace=False)


def test_futures_account_settings_lifecycle(client):
    _require_idle_account(client)
    position_mode = client.get_futures_position_mode()
    stp_mode = client.get_futures_stp_mode()
    multi_assets_mode = client.get_futures_multi_assets_mode()
    position_risk = client.get_futures_position_risk(FUTURES_SYMBOL)
    assert isinstance(position_mode, dict)
    assert isinstance(stp_mode, dict)
    assert isinstance(multi_assets_mode, dict)
    assert isinstance(position_risk, list)

    original_dual = bool(position_mode["dualSidePosition"])
    original_stp = str(stp_mode["stpMode"])
    original_multi_assets = bool(multi_assets_mode["multiAssetsMargin"])
    original_margin_type = str(position_risk[0].get("marginType", "crossed")).upper()
    alternate_stp = "EXPIRE_TAKER" if original_stp != "EXPIRE_TAKER" else "EXPIRE_MAKER"

    try:
        _assert_response(client.set_futures_position_mode(not original_dual))
        assert client.get_futures_position_mode()["dualSidePosition"] is not original_dual

        _assert_response(client.set_futures_stp_mode(alternate_stp))
        assert client.get_futures_stp_mode()["stpMode"] == alternate_stp

        if not original_multi_assets and original_margin_type == "ISOLATED":
            _assert_response(client.set_futures_margin_type(FUTURES_SYMBOL, "CROSSED"))
        _assert_response(client.set_futures_multi_assets_mode(not original_multi_assets))
        assert (
            client.get_futures_multi_assets_mode()["multiAssetsMargin"] is not original_multi_assets
        )
    finally:
        with suppress(Exception):
            client.set_futures_multi_assets_mode(original_multi_assets)
        if not original_multi_assets and original_margin_type == "ISOLATED":
            with suppress(Exception):
                client.set_futures_margin_type(FUTURES_SYMBOL, "ISOLATED")
        with suppress(Exception):
            client.set_futures_stp_mode(original_stp)
        with suppress(Exception):
            client.set_futures_position_mode(original_dual)


def test_futures_mmp_lifecycle(client):
    _require_idle_account(client)
    try:
        _assert_response(
            client.update_futures_mmp(
                FUTURES_SYMBOL,
                windowTimeInMilliseconds=5000,
                frozenTimeInMilliseconds=5000,
                qtyLimit="1000",
            )
        )
        _assert_response(client.get_futures_mmp(FUTURES_SYMBOL))
        _assert_response(client.reset_futures_mmp(FUTURES_SYMBOL))
    finally:
        with suppress(Exception):
            client.delete_futures_mmp(FUTURES_SYMBOL)
