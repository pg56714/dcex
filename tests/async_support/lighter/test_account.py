# ruff: noqa: ANN001, ANN201, D100, D103

import os
import re
import time

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.lighter.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

ACCOUNT_INDEX = os.getenv("LIGHTER_ACCOUNT_INDEX")
API_KEY_INDEX = os.getenv("LIGHTER_API_KEY_INDEX")
API_PRIVATE_KEY = os.getenv("LIGHTER_API_PRIVATE_KEY")
L1_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")

pytestmark = pytest.mark.private


@pytest_asyncio.fixture
async def client():
    async with Client(
        account_index=int(ACCOUNT_INDEX or 0),
        api_key_index=int(API_KEY_INDEX or 0),
        api_private_key=API_PRIVATE_KEY,
        preload_product_table=False,
    ) as client_instance:
        yield client_instance


def _assert_response(res) -> None:
    assert isinstance(res, dict)
    assert res.get("code", 200) == 200


def _skip_if_no_export_data(exc: FailedRequestError) -> None:
    if exc.status_code == 400 and (
        "22504" in exc.message or "no export data found" in exc.message.lower()
    ):
        pytest.skip("Lighter account has no export data for the requested interval.")


def _find_l1_address(value) -> str | None:
    if isinstance(value, str) and L1_ADDRESS_RE.fullmatch(value):
        return value
    if isinstance(value, dict):
        for key in ("l1_address", "l1Address", "eth_address", "address"):
            found = _find_l1_address(value.get(key))
            if found is not None:
                return found
        for nested in value.values():
            found = _find_l1_address(nested)
            if found is not None:
                return found
    if isinstance(value, list):
        for nested in value:
            found = _find_l1_address(nested)
            if found is not None:
                return found
    return None


async def _l1_address(client: Client, account_index: int) -> str:
    address = _find_l1_address(await client.get_account(by="index", value=str(account_index)))
    if address is None:
        pytest.skip("Lighter account response did not include an L1 address.")
    return address


@pytest.mark.asyncio
async def test_auth_token_and_key_check(client):
    token = await client.create_auth_token()
    assert isinstance(token, str)
    assert token
    assert await client.check_client() is None


@pytest.mark.asyncio
async def test_private_account_reads(client):
    account_index = int(ACCOUNT_INDEX or 0)
    now = int(time.time())

    _assert_response(await client.get_account(by="index", value=str(account_index)))
    _assert_response(await client.get_account_metadata(by="index", value=str(account_index)))
    _assert_response(await client.get_account_limits())
    _assert_response(
        await client.get_api_keys(
            account_index=account_index,
            api_key_index=int(API_KEY_INDEX or 0),
        )
    )
    _assert_response(await client.get_account_active_orders())
    _assert_response(await client.get_account_inactive_orders(limit=5))
    _assert_response(await client.get_position_funding(limit=5))
    _assert_response(await client.get_maker_only_api_keys())
    _assert_response(await client.get_tokens(account_index=account_index))
    _assert_response(await client.get_public_pools_metadata(index=0, limit=5))
    _assert_response(
        await client.get_pnl(
            by="index",
            value=str(account_index),
            resolution="1d",
            start_timestamp=now - 86400,
            end_timestamp=now,
            count_back=1,
        )
    )
    _assert_response(
        await client.get_trades(account_index=account_index, sort_by="timestamp", limit=5)
    )
    _assert_response(await client.get_next_nonce())


@pytest.mark.asyncio
async def test_private_bridge_and_history_reads(client):
    account_index = int(ACCOUNT_INDEX or 0)
    l1_address = await _l1_address(client, account_index)

    _assert_response(await client.get_accounts_by_l1_address(l1_address=l1_address))
    _assert_response(await client.get_l1_metadata(l1_address=l1_address))
    _assert_response(await client.get_deposit_history(l1_address=l1_address, filter="all"))
    _assert_response(await client.get_fastwithdraw_info())
    _assert_response(await client.get_transfer_history())
    _assert_response(await client.get_transfer_fee_info())
    _assert_response(await client.get_withdraw_history(filter="all"))


@pytest.mark.asyncio
@pytest.mark.generated
async def test_private_export_read(client):
    now_ms = int(time.time() * 1000)
    try:
        response = await client.get_export(
            type_="trade",
            start_timestamp=now_ms - 86_400_000,
            end_timestamp=now_ms,
        )
    except FailedRequestError as exc:
        _skip_if_no_export_data(exc)
        raise

    _assert_response(response)


@pytest.mark.asyncio
async def test_private_referral_lease_reads(client):
    account_index = int(ACCOUNT_INDEX or 0)
    l1_address = await _l1_address(client, account_index)

    _assert_response(await client.get_liquidations(limit=5))
    _assert_response(await client.get_referral_points())
    _assert_response(await client.get_referral_user_referrals(l1_address=l1_address, limit=5))
    _assert_response(await client.get_leases(limit=5))
    _assert_response(await client.get_partner_stats())
