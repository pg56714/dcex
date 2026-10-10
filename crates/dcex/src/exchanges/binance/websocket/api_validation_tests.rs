//! Local order-parameter checks for the WebSocket API. Each rejection is matched by its
//! message, so a test cannot pass because some unrelated rule fired first.

use serde_json::{Value, json};

use super::api::BinanceWebSocketApiMarket::{self, CoinFutures, Futures, Spot};
use super::api_schema::schema;
use super::api_validation::validate;

fn check(market: BinanceWebSocketApiMarket, method: &str, params: Value) -> Result<(), String> {
    let (_, fields) = schema(market, method).unwrap_or_else(|| panic!("{method} on {market:?}"));
    validate(market, method, params.as_object().expect("object"), fields)
        .map_err(|error| error.to_string())
}

#[track_caller]
fn rejects(market: BinanceWebSocketApiMarket, method: &str, params: Value, reason: &str) {
    let error = check(market, method, params).expect_err(reason);
    assert!(error.contains(reason), "expected {reason:?}, got {error:?}");
}

fn spot_limit() -> Value {
    json!({"symbol": "BTCUSDT", "side": "BUY", "type": "LIMIT", "timeInForce": "GTC", "price": "100", "quantity": "1"})
}

#[test]
fn valid_orders_pass() {
    check(Spot, "order.place", spot_limit()).unwrap();
    check(
        Spot,
        "order.place",
        json!({"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quoteOrderQty": "10"}),
    )
    .unwrap();
    check(Spot, "order.place", json!({"symbol": "BTCUSDT", "side": "SELL", "type": "LIMIT_MAKER", "price": "100", "quantity": "1", "icebergQty": "0.1"})).unwrap();
    check(Spot, "order.place", json!({"symbol": "BTCUSDT", "side": "SELL", "type": "STOP_LOSS", "quantity": "1", "trailingDelta": 100})).unwrap();
    check(Spot, "order.place", json!({"symbol": "BTCUSDT", "side": "BUY", "type": "LIMIT", "timeInForce": "GTC", "pegPriceType": "PRIMARY_PEG", "pegOffsetValue": 1, "pegOffsetType": "PRICE_LEVEL", "quantity": "1"})).unwrap();
    check(Futures, "order.place", json!({"symbol": "BTCUSDT", "side": "BUY", "type": "LIMIT", "timeInForce": "GTD", "goodTillDate": 1_700_000_000_000_u64, "price": "100", "quantity": "1", "positionSide": "BOTH", "reduceOnly": "true", "recvWindow": 5000})).unwrap();
    check(Futures, "algoOrder.place", json!({"algoType": "CONDITIONAL", "symbol": "BTCUSDT", "side": "SELL", "type": "STOP_MARKET", "triggerPrice": "90", "closePosition": "true", "workingType": "MARK_PRICE", "priceProtect": "TRUE"})).unwrap();
    check(Futures, "algoOrder.place", json!({"algoType": "CONDITIONAL", "symbol": "BTCUSDT", "side": "SELL", "type": "TRAILING_STOP_MARKET", "quantity": "1", "callbackRate": "1.5"})).unwrap();
    check(Futures, "algoOrder.place", json!({"algoType": "CONDITIONAL", "symbol": "BTCUSDT", "side": "SELL", "type": "STOP", "quantity": "1", "triggerPrice": "90", "price": "89"})).unwrap();
    check(
        Spot,
        "allOrders",
        json!({"symbol": "BTCUSDT", "startTime": 1, "endTime": 2, "recvWindow": "5000.5"}),
    )
    .unwrap();
    check(Spot, "order.place", json!({"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "1", "returnRateLimits": false})).unwrap();
}

#[test]
fn types_and_required_fields() {
    let mut missing = spot_limit();
    missing.as_object_mut().unwrap().remove("side");
    rejects(Spot, "order.place", missing, "side is required");
    let mut extra = spot_limit();
    extra["leverage"] = json!(5);
    rejects(
        Spot,
        "order.place",
        extra,
        "unsupported parameter: leverage",
    );
    let mut numeric = spot_limit();
    numeric["quantity"] = json!(1);
    rejects(
        Spot,
        "order.place",
        numeric,
        "invalid JSON type or value for quantity",
    );
    let mut negative = spot_limit();
    negative["price"] = json!("-1");
    rejects(
        Spot,
        "order.place",
        negative,
        "invalid JSON type or value for price",
    );
    let mut text_id = spot_limit();
    text_id["strategyId"] = json!("7");
    rejects(
        Spot,
        "order.place",
        text_id,
        "invalid JSON type or value for strategyId",
    );
    let mut blank = spot_limit();
    blank["newClientOrderId"] = json!("");
    rejects(
        Spot,
        "order.place",
        blank,
        "invalid JSON type or value for newClientOrderId",
    );
    let mut flag = spot_limit();
    flag["returnRateLimits"] = json!("false");
    rejects(
        Spot,
        "order.place",
        flag,
        "returnRateLimits must be boolean",
    );
    for window in [json!("0"), json!("60001"), json!("5000.1234")] {
        rejects(
            Spot,
            "allOrders",
            json!({"symbol": "BTCUSDT", "recvWindow": window}),
            "invalid JSON type or value for recvWindow",
        );
    }
    rejects(
        Futures,
        "order.place",
        json!({"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "1", "recvWindow": 60001}),
        "recvWindow must be 1..=60000",
    );
    rejects(
        Spot,
        "allOrders",
        json!({"symbol": "BTCUSDT", "startTime": 2, "endTime": 1}),
        "startTime cannot exceed endTime",
    );
}

#[test]
fn enumerations_and_exclusive_fields() {
    let mut side = spot_limit();
    side["side"] = json!("buy");
    rejects(Spot, "order.place", side, "invalid side");
    let base = json!({"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "1"});
    let with = |key: &str, value: Value| {
        let mut params = base.clone();
        params[key] = value;
        params
    };
    rejects(
        Futures,
        "order.place",
        with("positionSide", json!("NET")),
        "invalid positionSide",
    );
    rejects(
        Futures,
        "order.place",
        with("reduceOnly", json!("TRUE")),
        "invalid reduceOnly",
    );
    rejects(
        Futures,
        "order.place",
        json!({"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "1", "positionSide": "LONG", "reduceOnly": "true"}),
        "reduceOnly cannot be sent in hedge mode",
    );
    rejects(
        Futures,
        "order.place",
        json!({"symbol": "BTCUSDT", "side": "BUY", "type": "LIMIT", "timeInForce": "GTC", "price": "100", "priceMatch": "QUEUE", "quantity": "1"}),
        "price, priceMatch are mutually exclusive",
    );
    rejects(
        Spot,
        "order.place",
        json!({"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "1", "quoteOrderQty": "10"}),
        "quantity, quoteOrderQty are mutually exclusive",
    );
    rejects(
        Spot,
        "order.cancelReplace",
        json!({"symbol": "BTCUSDT", "cancelReplaceMode": "ALWAYS", "cancelOrderId": 1, "side": "BUY", "type": "MARKET", "quantity": "1"}),
        "invalid cancelReplaceMode",
    );
    rejects(
        Futures,
        "algoOrder.place",
        json!({"algoType": "CONDITIONAL", "symbol": "BTCUSDT", "side": "SELL", "type": "STOP_MARKET", "quantity": "1", "triggerPrice": "90", "workingType": "LIMIT"}),
        "invalid workingType",
    );
    rejects(
        Futures,
        "algoOrder.place",
        json!({"algoType": "CONDITIONAL", "symbol": "BTCUSDT", "side": "SELL", "type": "STOP_MARKET", "quantity": "1", "triggerPrice": "90", "priceProtect": "true"}),
        "invalid priceProtect",
    );
}

#[test]
fn identifiers_each_method_needs() {
    rejects(
        Spot,
        "order.status",
        json!({"symbol": "BTCUSDT"}),
        "one of orderId, origClientOrderId is required",
    );
    rejects(
        Spot,
        "order.cancel",
        json!({"symbol": "BTCUSDT"}),
        "one of orderId, origClientOrderId is required",
    );
    rejects(
        Spot,
        "orderList.status",
        json!({}),
        "one of orderListId, listClientOrderId, origClientOrderId is required",
    );
    rejects(
        Spot,
        "order.cancelReplace",
        json!({"symbol": "BTCUSDT", "cancelReplaceMode": "STOP_ON_FAILURE", "side": "BUY", "type": "MARKET", "quantity": "1"}),
        "one of cancelOrderId, cancelOrigClientOrderId is required",
    );
    rejects(
        Futures,
        "algoOrder.cancel",
        json!({}),
        "one of algoId, clientAlgoId is required",
    );
    rejects(
        Futures,
        "order.modify",
        json!({"symbol": "BTCUSDT", "side": "BUY", "quantity": "1", "orderId": 1}),
        "one of price, priceMatch is required",
    );
    check(
        Futures,
        "order.modify",
        json!({"symbol": "BTCUSDT", "side": "BUY", "quantity": "1", "orderId": 1, "price": "100"}),
    )
    .unwrap();
}

#[test]
fn order_shapes_follow_each_type() {
    let order = |extra: Value| {
        let mut params = json!({"symbol": "BTCUSDT", "side": "BUY"});
        params
            .as_object_mut()
            .unwrap()
            .extend(extra.as_object().unwrap().clone());
        params
    };
    rejects(
        Spot,
        "order.place",
        order(json!({"type": "OCO", "quantity": "1"})),
        "unsupported order type",
    );
    rejects(
        Futures,
        "order.place",
        order(json!({"type": "STOP_MARKET", "quantity": "1"})),
        "USD-M conditional orders use algoOrder.place",
    );
    rejects(
        CoinFutures,
        "order.place",
        order(json!({"type": "STOP", "quantity": "1"})),
        "COIN-M conditional orders use place_coin_futures_algo_order",
    );
    rejects(
        Spot,
        "sor.order.place",
        order(json!({"type": "LIMIT_MAKER", "quantity": "1"})),
        "unsupported order type",
    );
    rejects(
        Spot,
        "order.place",
        order(json!({"type": "MARKET"})),
        "one of quantity, quoteOrderQty is required",
    );
    rejects(
        Spot,
        "order.place",
        order(json!({"type": "LIMIT", "timeInForce": "GTC", "price": "1", "quoteOrderQty": "10"})),
        "quoteOrderQty is only valid for MARKET orders",
    );
    rejects(
        Spot,
        "order.place",
        order(json!({"type": "LIMIT", "timeInForce": "GTC", "quantity": "1"})),
        "one of price, priceMatch, pegPriceType is required",
    );
    rejects(
        Spot,
        "order.place",
        order(json!({"type": "LIMIT", "price": "1", "quantity": "1"})),
        "one of timeInForce is required",
    );
    rejects(
        Spot,
        "order.place",
        order(json!({"type": "TAKE_PROFIT", "quantity": "1"})),
        "one of stopPrice, trailingDelta is required",
    );
    rejects(
        Spot,
        "order.place",
        order(
            json!({"type": "LIMIT", "timeInForce": "IOC", "price": "1", "quantity": "1", "icebergQty": "0.1"}),
        ),
        "iceberg orders require GTC",
    );
    rejects(
        Spot,
        "order.place",
        order(
            json!({"type": "LIMIT", "timeInForce": "GTC", "pegPriceType": "PRIMARY_PEG", "pegOffsetValue": 1, "quantity": "1"}),
        ),
        "pegOffsetValue and pegOffsetType must be supplied together",
    );
    rejects(
        Futures,
        "order.place",
        order(json!({"type": "LIMIT", "timeInForce": "GTD", "price": "1", "quantity": "1"})),
        "one of goodTillDate is required",
    );
    let mut no_type = order(json!({"quantity": "1"}));
    no_type["type"] = json!(1);
    rejects(
        Spot,
        "order.place",
        no_type,
        "invalid JSON type or value for type",
    );
}

#[test]
fn conditional_algo_orders() {
    let algo = |extra: Value| {
        let mut params = json!({"algoType": "CONDITIONAL", "symbol": "BTCUSDT", "side": "SELL"});
        params
            .as_object_mut()
            .unwrap()
            .extend(extra.as_object().unwrap().clone());
        params
    };
    rejects(
        Futures,
        "algoOrder.place",
        algo(
            json!({"algoType": "VP", "type": "STOP_MARKET", "quantity": "1", "triggerPrice": "1"}),
        ),
        "invalid algoType",
    );
    rejects(
        Futures,
        "algoOrder.place",
        algo(json!({"type": "LIMIT", "quantity": "1", "triggerPrice": "1"})),
        "invalid type",
    );
    rejects(
        Futures,
        "algoOrder.place",
        algo(json!({"type": "STOP", "closePosition": "true", "triggerPrice": "1", "price": "1"})),
        "closePosition requires STOP_MARKET/TAKE_PROFIT_MARKET",
    );
    rejects(
        Futures,
        "algoOrder.place",
        algo(
            json!({"type": "STOP_MARKET", "closePosition": "true", "quantity": "1", "triggerPrice": "1"}),
        ),
        "closePosition requires STOP_MARKET/TAKE_PROFIT_MARKET",
    );
    rejects(
        Futures,
        "algoOrder.place",
        algo(json!({"type": "STOP_MARKET", "triggerPrice": "1"})),
        "one of quantity is required",
    );
    rejects(
        Futures,
        "algoOrder.place",
        algo(json!({"type": "TRAILING_STOP_MARKET", "quantity": "1"})),
        "one of callbackRate is required",
    );
    rejects(
        Futures,
        "algoOrder.place",
        algo(json!({"type": "TRAILING_STOP_MARKET", "quantity": "1", "callbackRate": "11"})),
        "callbackRate must be 0.1..=10",
    );
    rejects(
        Futures,
        "algoOrder.place",
        algo(json!({"type": "TAKE_PROFIT_MARKET", "quantity": "1"})),
        "one of triggerPrice is required",
    );
    rejects(
        Futures,
        "algoOrder.place",
        algo(json!({"type": "TAKE_PROFIT", "quantity": "1", "triggerPrice": "1"})),
        "one of price, priceMatch is required",
    );
}

#[test]
fn order_lists_reuse_the_rest_rules() {
    let oco = json!({
        "symbol": "BTCUSDT", "side": "SELL", "quantity": "1",
        "aboveType": "LIMIT_MAKER", "abovePrice": "110",
        "belowType": "STOP_LOSS", "belowStopPrice": "90",
    });
    check(Spot, "orderList.place.oco", oco.clone()).unwrap();
    let mut broken = oco;
    broken.as_object_mut().unwrap().remove("belowStopPrice");
    rejects(
        Spot,
        "orderList.place.oco",
        broken,
        "belowStopPrice or belowTrailingDelta is required",
    );
}
