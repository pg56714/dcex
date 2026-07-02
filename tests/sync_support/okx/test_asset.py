# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time

import pytest
from dotenv import load_dotenv

from dcex.okx.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_API_SECRET = os.getenv("OKX_API_SECRET")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")


def _is_deposit_withdraw_status_unavailable(exc) -> bool:
    message = str(exc)
    return "58214" in message


def _is_rate_limited(exc) -> bool:
    message = str(exc)
    return "50011" in message or "Too many requests" in message


def _fail_if_deposit_withdraw_status_unavailable(exc) -> None:
    if _is_deposit_withdraw_status_unavailable(exc):
        pytest.fail("OKX deposit/withdraw status is unavailable for every candidate.")
    if _is_rate_limited(exc):
        pytest.fail("OKX rate-limited the deposit/withdraw status endpoint.", pytrace=False)


def _get_deposit_withdraw_status_with_retry(client, deposit) -> object:
    last_error = None
    for attempt in range(4):
        try:
            return client.get_deposit_withdraw_status(
                txId=deposit["txId"],
                ccy=deposit["ccy"],
                to=deposit["to"],
                chain=deposit["chain"],
            )
        except FailedRequestError as exc:
            if not _is_rate_limited(exc):
                raise
            last_error = exc
            time.sleep(15 * (attempt + 1))
    assert last_error is not None
    raise last_error


@pytest.fixture
def client():
    return Client(
        api_key=OKX_API_KEY,
        api_secret=OKX_API_SECRET,
        passphrase=OKX_PASSPHRASE,
    )


@pytest.mark.private
def test_get_currencies(client):
    res = client.get_currencies()
    assert res is not None


@pytest.mark.private
def test_get_balances(client):
    res = client.get_balances()
    assert res is not None


@pytest.mark.private
def test_get_asset_valuation(client):
    res = client.get_asset_valuation()
    assert res is not None


@pytest.mark.private
def test_get_bills(client):
    res = client.get_bills()
    assert res is not None


@pytest.mark.private
def test_get_deposit_address(client):
    res = client.get_deposit_address(ccy="BTC")
    assert res is not None


@pytest.mark.private
def test_get_deposit_history(client):
    res = client.get_deposit_history()
    assert res is not None


@pytest.mark.private
def test_get_deposit_withdraw_status(client):
    history = client.get_deposit_history()
    deposits = [
        item
        for item in history.get("data", [])
        if isinstance(item, dict)
        and item.get("txId")
        and item.get("ccy")
        and item.get("to")
        and item.get("chain")
    ]
    if not deposits:
        pytest.fail("OKX account has no complete deposit record to query.", pytrace=False)
    last_error = None
    for deposit in deposits:
        try:
            res = _get_deposit_withdraw_status_with_retry(client, deposit)
        except FailedRequestError as exc:
            if _is_deposit_withdraw_status_unavailable(exc):
                last_error = exc
                time.sleep(0.5)
                continue
            _fail_if_deposit_withdraw_status_unavailable(exc)
            raise
        assert res is not None
        return
    assert last_error is not None
    assert _is_deposit_withdraw_status_unavailable(last_error)


@pytest.mark.private
def test_get_exchange_list(client):
    res = client.get_exchange_list()
    assert res is not None


@pytest.mark.private
def test_post_monthly_statement(client):
    res = client.post_monthly_statement(month="Mar")
    assert res is not None


@pytest.mark.private
def test_get_monthly_statement(client):
    res = client.get_monthly_statement(month="Mar")
    assert res is not None


@pytest.mark.private
def test_get_convert_currencies(client):
    res = client.get_convert_currencies()
    assert res is not None


@pytest.mark.private
def test_get_convert_history(client):
    res = client.get_convert_history()
    assert res is not None
