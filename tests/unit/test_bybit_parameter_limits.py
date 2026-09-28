"""Offline coverage for bybit parameter limits."""
# ruff: noqa: ANN001, ANN201, D103

from urllib.parse import parse_qsl, urlsplit

import pytest


@pytest.mark.parametrize(
    "method,limit",
    [
        ("get_crypto_loan_borrow_history", 100),
        ("get_crypto_loan_common_adjustment_history", 100),
        ("get_spot_lever_token_order_record", 500),
    ],
)
def test_bybit_endpoint_specific_page_limit(method, limit):
    from tests.unit.test_bybit_endpoint_coverage import CASES, _route_server, _sync_client

    case = next(c for c in CASES if c.method_name == method)
    with _route_server() as (base, received):
        client = _sync_client(base)
        try:
            getattr(client, method)(*case.args, **dict(case.kwargs, limit=limit))
        finally:
            client.close()
        assert dict(parse_qsl(urlsplit(received.get(timeout=2)["path"]).query))["limit"] == str(
            limit
        )


def test_bybit_max_loan_accepts_collateral_list():
    import json

    from tests.unit.test_bybit_endpoint_coverage import _route_server, _sync_client

    collateral = [{"ccy": "BTC", "amount": "1"}]
    with _route_server() as (base, received):
        client = _sync_client(base)
        try:
            client.crypto_loan_common_max_loan(currency="USDT", collateral_list=collateral)
        finally:
            client.close()
        assert json.loads(received.get(timeout=2)["body"])["collateralList"] == collateral
