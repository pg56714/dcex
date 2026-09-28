"""Exercise every native Binance WS schema against an independent recording peer."""

import asyncio
import hashlib
import hmac
import re
from pathlib import Path

import pytest

from dcex.ws.binance import CoinFuturesApiClient, FuturesApiClient, SpotApiClient
from tests.unit.ws_test_peer import echo_peer

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "crates/dcex/src/exchanges/binance/websocket/api_schema.rs"
SCHEMAS = []
for match in re.finditer(
    r'\(BinanceWebSocketApiMarket::(\w+), "([^"]+)"\) => Some\(\((.*?)\)\),',
    SOURCE.read_text(encoding="utf8"),
    re.S,
):
    market, method, body = match.groups()
    fields = re.findall(r'name: "([^"]+)",\s*kind: Kind::(\w+),\s*required: (true|false)', body)
    SCHEMAS.append((market, method, re.search(r"Auth::(\w+)", body)[1], fields))


def parameters(method, fields):
    values = {
        "Text": "example",
        "Decimal": "1.25",
        "Integer": 7,
        "Bool": True,
        "Strings": ["BTCUSDT"],
    }
    specific = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "LIMIT",
        "timeInForce": "GTC",
        "workingSide": "BUY",
        "pendingSide": "SELL",
        "workingType": "LIMIT",
        "pendingType": "MARKET",
        "aboveType": "LIMIT_MAKER",
        "belowType": "STOP_LOSS",
        "pendingAboveType": "LIMIT_MAKER",
        "pendingBelowType": "STOP_LOSS",
        "interval": "1m",
        "cancelReplaceMode": "STOP_ON_FAILURE",
        "algoType": "CONDITIONAL",
    }
    fields = {name: (kind, required) for name, kind, required in fields}
    result = {
        name: specific.get(name, values[kind])
        for name, (kind, required) in fields.items()
        if required == "true"
    }
    # Exercise optional payload fields while respecting documented mutually exclusive groups.
    for name in [
        "symbol",
        "orderId",
        "orderListId",
        "cancelOrderId",
        "algoId",
        "quantity",
        "price",
        "timeInForce",
        "workingPrice",
        "workingTimeInForce",
        "abovePrice",
        "belowStopPrice",
        "pendingAbovePrice",
        "pendingBelowStopPrice",
        "subscriptionId",
        "limit",
    ]:
        if name in fields:
            result[name] = specific.get(name, values[fields[name][0]])
    if method == "algoOrder.place":
        result.update(type="STOP_MARKET", triggerPrice="12.5")
    if "timestamp" in fields:
        result["timestamp"] = 1645423376532
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "market,method,auth,fields", SCHEMAS, ids=[f"{s[0]}:{s[1]}" for s in SCHEMAS]
)
async def test_every_schema_method_reaches_wire(market, method, auth, fields):
    cls = {"Spot": SpotApiClient, "Futures": FuturesApiClient, "CoinFutures": CoinFuturesApiClient}[
        market
    ]
    params = parameters(method, fields)
    async with echo_peer() as (url, received):
        client = cls("key", "secret", base_url=url)
        try:
            if method == "session.logon":
                with pytest.raises(ValueError, match="Ed25519"):
                    await client.request(method, params)
                assert received == []
                return
            await client.connect()
            request_id = await asyncio.wait_for(client.request(method, params), 10)
            message = await asyncio.wait_for(client.recv(), 10)
            assert message["id"] == request_id
            assert received[-1]["method"] == method
            wire = dict(received[-1]["params"])
            signature = wire.pop("signature", None)
            if auth in {"Signed", "Key"}:
                assert wire.pop("apiKey") == "key"
            if auth == "Signed":
                signed = {**wire, "apiKey": "key"}
                text = "&".join(
                    f"{key}={str(value).lower() if isinstance(value, bool) else value}"
                    for key, value in sorted(signed.items())
                )
                assert signature == hmac.new(b"secret", text.encode(), hashlib.sha256).hexdigest()
                if "timestamp" not in params:
                    assert isinstance(wire.pop("timestamp"), int)
            else:
                assert signature is None
            assert wire == params
        finally:
            await client.close()


def test_schema_cases_cover_the_entire_native_table():
    assert len(SCHEMAS) == SOURCE.read_text(encoding="utf8").count("=> Some((")
    assert {"openOrders.cancelAll", "session.subscriptions", "sor.order.place", "myTrades"} <= {
        s[1] for s in SCHEMAS
    }
