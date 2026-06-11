# ruff: noqa: ANN001, ANN201, D100, D103

import os
from contextlib import suppress

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.aster.client import Client

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


@pytest_asyncio.fixture
async def client():
    async with Client(
        user_address=ASTER_USER_ADDRESS,
        signer_address=ASTER_SIGNER_ADDRESS,
        private_key=ASTER_PRIVATE_KEY,
        preload_product_table=False,
        timeout=20,
    ) as client_instance:
        yield client_instance


def _assert_response(response: object) -> None:
    assert isinstance(response, dict | list | bool)


async def _require_idle_account(client: Client) -> None:
    if await client.get_futures_open_orders():
        pytest.skip("Aster has existing futures open orders.")
    positions = await client.get_futures_position_risk()
    assert isinstance(positions, list)
    if any(float(position.get("positionAmt", 0)) != 0 for position in positions):
        pytest.skip("Aster has an existing futures position.")


@pytest.mark.asyncio
async def test_futures_account_settings_lifecycle(client):
    await _require_idle_account(client)
    position_mode = await client.get_futures_position_mode()
    stp_mode = await client.get_futures_stp_mode()
    multi_assets_mode = await client.get_futures_multi_assets_mode()
    position_risk = await client.get_futures_position_risk(FUTURES_SYMBOL)
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
        _assert_response(await client.set_futures_position_mode(not original_dual))
        assert (await client.get_futures_position_mode())["dualSidePosition"] is not original_dual

        _assert_response(await client.set_futures_stp_mode(alternate_stp))
        assert (await client.get_futures_stp_mode())["stpMode"] == alternate_stp

        if not original_multi_assets and original_margin_type == "ISOLATED":
            _assert_response(await client.set_futures_margin_type(FUTURES_SYMBOL, "CROSSED"))
        _assert_response(await client.set_futures_multi_assets_mode(not original_multi_assets))
        assert (await client.get_futures_multi_assets_mode())[
            "multiAssetsMargin"
        ] is not original_multi_assets
    finally:
        with suppress(Exception):
            await client.set_futures_multi_assets_mode(original_multi_assets)
        if not original_multi_assets and original_margin_type == "ISOLATED":
            with suppress(Exception):
                await client.set_futures_margin_type(FUTURES_SYMBOL, "ISOLATED")
        with suppress(Exception):
            await client.set_futures_stp_mode(original_stp)
        with suppress(Exception):
            await client.set_futures_position_mode(original_dual)


@pytest.mark.asyncio
async def test_futures_mmp_lifecycle(client):
    await _require_idle_account(client)
    try:
        _assert_response(
            await client.update_futures_mmp(
                FUTURES_SYMBOL,
                windowTimeInMilliseconds=5000,
                frozenTimeInMilliseconds=5000,
                qtyLimit="1000",
            )
        )
        _assert_response(await client.get_futures_mmp(FUTURES_SYMBOL))
        _assert_response(await client.reset_futures_mmp(FUTURES_SYMBOL))
    finally:
        with suppress(Exception):
            await client.delete_futures_mmp(FUTURES_SYMBOL)
