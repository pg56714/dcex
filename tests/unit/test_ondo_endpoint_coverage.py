# ruff: noqa: D103
"""
Offline wire coverage for every Ondo Perps sync and async endpoint wrapper.

The generic endpoint suite replaces the transport with a fake and never reaches
the native dispatcher.  These tests drive each public wrapper through the real
Rust client against a local HTTP server and assert that the documented Ondo
Perps route (https://docs.ondoperps.xyz/api-reference) and query/body arrive
on the wire, including canonical ``BASE-QUOTE-SWAP`` to ``BASE-QUOTE.P``
market translation.
"""

from __future__ import annotations

import json
import queue
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import pytest

from dcex.async_support.ondo.client import Client as AsyncClient
from dcex.ondo.client import Client
from dcex.utils.errors import FailedRequestError
from tests.unit.native_http_helpers import _http_server

RUST_DIR = Path(__file__).resolve().parents[2] / "crates" / "dcex" / "src" / "exchanges" / "ondo"
RUST_SOURCE = "\n".join(path.read_text(encoding="utf-8") for path in RUST_DIR.glob("*.rs"))
MARKET = "AAPL-USD.P"
DESTINATION = {"id": "acct", "wallet": "margin"}


@dataclass(frozen=True)
class WireCase:
    """One wrapper call and the request it must produce."""

    method: str
    kwargs: dict[str, Any]
    target: str
    body: dict[str, Any] | None = None

    @property
    def id(self) -> str:
        """Return the pytest id for this case."""
        return f"{self.method}-{self.target.split('?')[0]}"


def case(method: str, target: str, body: dict[str, Any] | None = None, **kwargs: Any) -> WireCase:  # noqa: ANN401
    """Build a wire case; ``body`` is the expected JSON request body."""
    return WireCase(method, kwargs, target, body)


CASES = [
    # Market data
    case("get_status", "/status"),
    case("get_markets", "/v1/markets"),
    case("get_trades", "/v1/perps/trades?market=AAPL-USD.P&limit=10", market=MARKET, limit=10),
    case("get_depth", "/v1/perps/depth?market=BTC-USD.P&depth=5", market="BTC-USD-SWAP", depth=5),
    case("get_symbol_info", "/v1/perps/symbol_info"),
    case("get_funding_rates", "/v1/perps/funding_rates?market=AAPL-USD.P", market=MARKET),
    case(
        "get_funding_rate_history",
        "/v1/perps/funding_rate_history?market=AAPL-USD.P&limit=5&startTime=1&endTime=2",
        market=MARKET,
        limit=5,
        startTime=1,
        endTime=2,
    ),
    case("get_mark_prices", "/v1/perps/mark_prices"),
    case("get_open_interest", "/v1/perps/open_interest"),
    case("get_volume", "/v1/perps/volume"),
    case("get_contracts", "/v1/perps/contracts?sparkline=true", sparkline=True),
    case(
        "get_price_history",
        "/v1/perps/history?symbol=AAPL-USD.P&resolution=60&from=1&to=2",
        symbol=MARKET,
        resolution="60",
        from_time=1,
        to_time=2,
    ),
    # Orders
    case(
        "get_orders",
        "/v1/perps/orders?market=AAPL-USD.P&status=open&limit=3&startTime=1&endTime=2",
        market=MARKET,
        status="open",
        limit=3,
        startTime=1,
        endTime=2,
    ),
    case("get_open_orders", "/v1/perps/orders?market=AAPL-USD.P&status=open", market=MARKET),
    case(
        "place_order",
        "/v1/perps/orders",
        {"market": "BTC-USD.P", "side": "buy", "price": "100", "size": "1", "postOnly": True},
        market="BTC-USD-SWAP",
        side="buy",
        price="100",
        size="1",
        postOnly=True,
    ),
    case(
        "place_batch_orders",
        "/v1/perps/orders/batch",
        {"orders": [{"market": "AAPL-USD.P", "side": "sell", "price": "1", "size": "1"}]},
        orders=[{"market": MARKET, "side": "sell", "price": "1", "size": "1"}],
    ),
    case("batch_cancel_orders", "/v1/perps/orders/batch?orderIDs=o1,o2", orderIDs=["o1", "o2"]),
    case("cancel_order", "/v1/perps/orders/o1", orderID="o1"),
    case("cancel_all_orders", "/v1/perps/orders?market=AAPL-USD.P", market=MARKET),
    case("cancel_open_orders", "/v1/perps/orders"),
    case("get_order", "/v1/perps/orders/o1", orderID="o1"),
    case("get_fills_by_order", "/v1/perps/orders/o1/fills", orderID="o1"),
    case(
        "get_fills",
        "/v1/perps/fills?market=AAPL-USD.P&limit=2&startTime=1&endTime=2",
        market=MARKET,
        limit=2,
        startTime=1,
        endTime=2,
    ),
    case(
        "export_orders_csv",
        "/v1/perps/orders/csv?market=AAPL-USD.P&startTime=1",
        market=MARKET,
        startTime=1,
    ),
    case("export_fills_csv", "/v1/perps/fills/csv?endTime=2", endTime=2),
    case(
        "place_twap_order",
        "/v1/perps/twap/order",
        {"market": "AAPL-USD.P", "side": "buy", "size": "5", "runningTime": 600, "frequency": 30},
        market=MARKET,
        side="buy",
        size="5",
        runningTime=600,
        frequency=30,
    ),
    case("get_twap_order", "/v1/perps/twap/order/t1", orderID="t1"),
    case("cancel_twap_order", "/v1/perps/twap/order/t1", orderID="t1"),
    case("get_twap_order_fills", "/v1/perps/twap/order/t1/fills", orderID="t1"),
    case("get_running_twap_orders", "/v1/perps/twap/orders/running"),
    case("get_twap_order_history", "/v1/perps/twap/orders/history?limit=4", limit=4),
    case("get_stop_orders", "/v1/perps/stop_order"),
    case(
        "set_stop_order",
        "/v1/perps/stop_order",
        {
            "market": "AAPL-USD.P",
            "positionDirection": "long",
            "type": "takeProfit",
            "triggerPrice": "300",
        },
        market=MARKET,
        positionDirection="long",
        type="takeProfit",
        triggerPrice="300",
    ),
    case(
        "remove_stop_order",
        "/v1/perps/stop_order?market=AAPL-USD.P&type=stopLoss",
        market=MARKET,
        type="stopLoss",
    ),
    # Account / positions / leverage
    case("get_account", "/v1/account"),
    case("get_balance", "/v1/perps/balance"),
    case("get_positions", "/v1/perps/positions"),
    case("get_open_order_counts", "/v1/counts/orders"),
    case("get_order_summaries", "/v1/perps/orders_summaries"),
    case("get_portfolio_summary", "/v1/portfolio/summary"),
    case("get_portfolio_summary_graph", "/v1/portfolio/summary/graph?range=30d", range_="30d"),
    case(
        "get_klines",
        "/v1/perps/candles?market=AAPL-USD.P&resolution=1H&from=1&to=2",
        market=MARKET,
        resolution="1H",
        from_time=1,
        to_time=2,
    ),
    case(
        "get_candles",
        "/v1/perps/candles?market=BTC-USD.P&resolution=1D&from=1&to=2",
        market="BTC-USD-SWAP",
        resolution="1D",
        from_time=1,
        to_time=2,
    ),
    case("get_funding_fee_payments", "/v1/perps/funding_fees?limit=1", limit=1),
    case("get_liquidation_history", "/v1/perps/liquidation_history?cursor=c", cursor="c"),
    case("get_max_order_size", "/v1/perps/max_order_size?market=AAPL-USD.P", market=MARKET),
    case("get_leverage", "/v1/perps/leverage?market=AAPL-USD.P", market=MARKET),
    case(
        "set_leverage",
        "/v1/perps/leverage",
        {"market": "AAPL-USD.P", "leverage": "3"},
        market=MARKET,
        leverage="3",
    ),
    # Wallet / API keys
    case("get_deposits", "/v1/wallet/deposits"),
    case("get_deposit", "/v1/wallet/deposits/d1", depositID="d1"),
    case("get_withdrawals", "/v1/wallet/withdrawals"),
    case("get_withdrawal", "/v1/wallet/withdrawals/w1", withdrawalID="w1"),
    case("get_withdrawal_limits", "/v1/wallet/withdrawals/limit"),
    case(
        "get_withdrawal_status",
        "/v1/get_withdrawal_status",
        {"customer_withdrawal_id": "c1"},
        customer_withdrawal_id="c1",
    ),
    case(
        "get_deposit_addresses",
        "/v1/wallet/deposit_address/list",
        {"coins": ["USDC"]},
        coins=["USDC"],
    ),
    case(
        "provision_deposit_address",
        "/v1/provision_address",
        {"network": "ethereum", "symbol": "USDC", "deposit_destination": DESTINATION},
        network="ethereum",
        symbol="USDC",
        deposit_destination=DESTINATION,
    ),
    case(
        "sandbox_deposit",
        "/v1/sandbox_deposit",
        {
            "amount": "1",
            "symbol": "USDC",
            "deposit_destination": DESTINATION,
            "chain_id": "eth-sepolia",
        },
        amount="1",
        symbol="USDC",
        deposit_destination=DESTINATION,
        chain_id="eth-sepolia",
    ),
    case("export_deposits_csv", "/v1/wallet/deposits/csv", {"start_time": 1}, start_time=1),
    case("export_withdrawals_csv", "/v1/wallet/withdrawals/csv", {"end_time": 2}, end_time=2),
    case("get_address_book", "/v1/wallet/address_book"),
    case(
        "edit_address_book_entry",
        "/v1/wallet/address_book",
        {"withdrawalAddress": "0xabc", "addressLabel": "cold"},
        withdrawalAddress="0xabc",
        addressLabel="cold",
    ),
    case(
        "remove_address_book_entry",
        "/v1/wallet/address_book",
        {"withdrawalAddress": "0xabc"},
        withdrawalAddress="0xabc",
    ),
    case(
        "get_address_book_challenge",
        "/v1/auth/erc-4361/address_book/get_challenge",
        {"walletAddress": "0x1", "chainId": "43114", "withdrawalAddress": "0x2"},
        walletAddress="0x1",
        chainId="43114",
        withdrawalAddress="0x2",
    ),
    case(
        "complete_address_book_challenge",
        "/v1/auth/erc-4361/address_book/complete_challenge",
        {"id": "c1", "signature": "0xsig"},
        id="c1",
        signature="0xsig",
    ),
    case("list_api_keys", "/v1/api_keys"),
    case(
        "create_api_key",
        "/v1/api_keys",
        {"name": "bot", "scopes": ["trade", "transfer"]},
        name="bot",
        scopes=["trade", "transfer"],
    ),
    case("delete_api_key", "/v1/api_keys/k1", apiKeyID="k1"),
    case(
        "set_api_key_ip_whitelist",
        "/v1/api_keys/k1/ip_whitelist",
        {"ip": "10.0.0.1"},
        apiKeyID="k1",
        ip="10.0.0.1",
    ),
    case(
        "remove_api_key_ip_whitelist",
        "/v1/api_keys/k1/ip_whitelist",
        {"ip": "10.0.0.1"},
        apiKeyID="k1",
        ip="10.0.0.1",
    ),
]


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {"base_url": base_url, "api_key_id": "key-id", "api_secret": "ondoApiSecret_SECRET"}


@pytest.fixture(scope="module")
def server() -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    """Share one recording server across the module to keep the suite fast."""
    with _http_server() as (base_url, received):
        yield base_url, received


def _drain(received: queue.Queue[dict[str, Any]]) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    while not received.empty():
        requests.append(received.get_nowait())
    return requests


def _assert_request(wire: WireCase, requests: list[dict[str, Any]]) -> None:
    assert len(requests) == 1, requests
    request = requests[0]
    assert unquote(request["path"]) == wire.target
    if wire.body is None:
        assert request["body"] == ""
    else:
        assert json.loads(request["body"]) == wire.body


def _wrapper_names() -> set[str]:
    names: set[str] = set()
    for base in Client.__mro__:
        module = getattr(base, "__module__", "")
        if (
            module.startswith("dcex.ondo._")
            and module.endswith("_http")
            and "manager" not in module
        ):
            names.update(
                name
                for name, value in vars(base).items()
                if not name.startswith("_") and callable(value)
            )
    return names


def test_every_endpoint_wrapper_has_a_wire_case() -> None:
    assert _wrapper_names() - {wire.method for wire in CASES} == set()
    for wire in CASES:
        assert f'"{wire.method}"' in RUST_SOURCE, wire.method


@pytest.mark.parametrize("wire", CASES, ids=[wire.id for wire in CASES])
def test_sync_wrapper_reaches_documented_route(
    wire: WireCase, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    try:
        result = getattr(client, wire.method)(**wire.kwargs)
    finally:
        client.close()
    assert result == {"ok": True}
    _assert_request(wire, _drain(received))


@pytest.mark.asyncio
@pytest.mark.parametrize("wire", CASES, ids=[wire.id for wire in CASES])
async def test_async_wrapper_reaches_documented_route(
    wire: WireCase, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    base_url, received = server
    _drain(received)
    client = AsyncClient(**_client_kwargs(base_url))
    try:
        result = await getattr(client, wire.method)(**wire.kwargs)
    finally:
        await client.close()
    assert result == {"ok": True}
    _assert_request(wire, _drain(received))


def test_unsafe_requests_are_rejected_before_the_wire(
    server: tuple[str, queue.Queue[dict[str, Any]]],
) -> None:
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    errors = (ValueError, FailedRequestError)
    try:
        with pytest.raises(errors):
            client.place_order(market=MARKET, side="buy", type="market", price="1", size="1")
        with pytest.raises(errors):
            client.place_order(market=MARKET, side="sell", type="market", quoteSize="10")
        with pytest.raises(errors):
            client.place_order(market="BTC-USD-SPOT", side="buy", price="1", size="1")
        with pytest.raises(errors):
            client.place_batch_orders(orders=[])
        with pytest.raises(ValueError, match="without commas"):
            client.batch_cancel_orders(orderIDs=["a,b"])
        with pytest.raises(errors):
            client.cancel_order(orderID="../all")
    finally:
        client.close()
    assert _drain(received) == []
