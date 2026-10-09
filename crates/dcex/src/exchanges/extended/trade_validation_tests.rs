//! Pre-signed order bodies: each local rule rejects exactly the field it guards, matched by
//! its message so an unrelated rule cannot make a case pass.

use serde_json::{Value, json};

use super::super::client::signing_domain_for_base_url;
use super::validate_order_body;

fn now_ms() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_millis() as u64
}

fn settlement() -> Value {
    json!({"signature": {"r": "0x1", "s": "0x2"}, "starkKey": "0x3", "collateralPosition": "4"})
}

fn limit() -> Value {
    json!({
        "id": "order-1", "market": "BTC-USD", "type": "LIMIT", "side": "BUY",
        "qty": "0.001", "price": "10000", "reduceOnly": false, "postOnly": false,
        "timeInForce": "GTT", "expiryEpochMillis": now_ms() + 3_600_000, "fee": "0.00025",
        "nonce": "1", "selfTradeProtectionLevel": "ACCOUNT", "settlement": settlement(),
    })
}

fn tpsl_trigger() -> Value {
    json!({
        "triggerPrice": "11000", "triggerPriceType": "LAST", "price": "11000",
        "priceType": "LIMIT", "settlement": settlement(),
    })
}

fn with(mut body: Value, changes: Value) -> Value {
    for (key, value) in changes.as_object().unwrap() {
        if value.is_null() {
            body.as_object_mut().unwrap().remove(key);
        } else {
            body[key] = value.clone();
        }
    }
    body
}

fn check(body: &Value) -> Result<(), String> {
    let domain = signing_domain_for_base_url("https://api.starknet.extended.exchange");
    validate_order_body(body, domain).map_err(|error| error.to_string())
}

#[track_caller]
fn rejects(body: Value, reason: &str) {
    let error = check(&body).expect_err(reason);
    assert!(error.contains(reason), "expected {reason:?}, got {error:?}");
}

#[test]
fn valid_bodies_of_every_order_type_pass() {
    check(&limit()).unwrap();
    check(&with(
        limit(),
        json!({"type": "MARKET", "timeInForce": "IOC", "rfqStartPrice": "9000"}),
    ))
    .unwrap();
    check(&with(
        limit(),
        json!({"builderFee": "0.0001", "builderId": 7}),
    ))
    .unwrap();
    check(&with(
        limit(),
        json!({
            "type": "CONDITIONAL",
            "trigger": {"triggerPrice": "9500", "triggerPriceType": "MARK",
                        "direction": "DOWN", "executionPriceType": "LIMIT"},
        }),
    ))
    .unwrap();
    check(&with(
        limit(),
        json!({
            "type": "TPSL", "reduceOnly": true, "qty": "0", "price": "0",
            "tpSlType": "POSITION", "takeProfit": tpsl_trigger(), "settlement": null,
        }),
    ))
    .unwrap();
}

#[test]
fn common_fields_are_validated() {
    rejects(
        with(limit(), json!({"postOnly": true, "timeInForce": "IOC"})),
        "cannot use IOC",
    );
    rejects(
        with(limit(), json!({"selfTradeProtectionLevel": "NONE"})),
        "selfTradeProtectionLevel",
    );
    rejects(
        with(limit(), json!({"nonce": "0"})),
        "nonce must be between 1 and 2147483648",
    );
    rejects(with(limit(), json!({"fee": "2"})), "fee must not exceed 1");
    rejects(
        with(limit(), json!({"builderFee": "0.1"})),
        "builderFee and builderId must be provided together",
    );
    rejects(
        with(limit(), json!({"builderFee": "2", "builderId": 1})),
        "builderFee must not exceed 1",
    );
    rejects(
        with(limit(), json!({"rfqStartPrice": "1"})),
        "rfqStartPrice is only valid for MARKET orders",
    );
    rejects(
        with(
            limit(),
            json!({"expiryEpochMillis": now_ms() + 100 * 86_400_000}),
        ),
        "no more than 90 days away",
    );
    rejects(
        with(limit(), json!({"expiryEpochMillis": 1})),
        "must be in the future",
    );
    rejects(
        with(limit(), json!({"market": ""})),
        "market must not be empty",
    );
    rejects(
        with(limit(), json!({"qty": 1})),
        "qty must be a decimal string",
    );
}

#[test]
fn order_types_enforce_their_shapes() {
    rejects(
        with(limit(), json!({"qty": "0"})),
        "LIMIT order qty must be greater than zero",
    );
    rejects(
        with(
            limit(),
            json!({"type": "MARKET", "timeInForce": "IOC", "qty": "0"}),
        ),
        "MARKET order qty must be greater than zero",
    );
    let trigger = json!({"triggerPrice": "9500", "triggerPriceType": "MARK",
                         "direction": "SIDEWAYS", "executionPriceType": "LIMIT"});
    rejects(
        with(
            limit(),
            json!({"type": "CONDITIONAL", "qty": "0", "trigger": trigger}),
        ),
        "CONDITIONAL order qty must be greater than zero",
    );
    rejects(
        with(limit(), json!({"type": "CONDITIONAL", "trigger": trigger})),
        "direction",
    );

    let tpsl = |changes: Value| {
        with(
            with(
                limit(),
                json!({"type": "TPSL", "reduceOnly": true, "qty": "1", "price": "0",
                       "tpSlType": "ORDER", "takeProfit": tpsl_trigger(), "settlement": null}),
            ),
            changes,
        )
    };
    check(&tpsl(json!({}))).unwrap();
    rejects(
        tpsl(json!({"reduceOnly": false})),
        "must be reduce-only and cannot be post-only",
    );
    rejects(
        tpsl(json!({"qty": "0"})),
        "ORDER qty must be positive and POSITION qty must be zero",
    );
    rejects(
        tpsl(json!({"price": "5"})),
        "TPSL price must be zero when provided",
    );
    rejects(
        tpsl(json!({"takeProfit": null})),
        "require takeProfit or stopLoss",
    );
    rejects(
        tpsl(json!({"stopLoss": with(tpsl_trigger(), json!({"priceType": "STOP"}))})),
        "priceType",
    );
}

#[test]
fn settlements_must_be_well_formed() {
    let bad = |field: &str, value: Value| {
        let mut body = limit();
        body["settlement"][field] = value;
        body
    };
    rejects(
        bad("signature", json!({"r": "zz", "s": "0x2"})),
        "settlement.signature.r must be hexadecimal",
    );
    rejects(
        bad("starkKey", json!("key")),
        "settlement.starkKey must be hexadecimal",
    );
    rejects(
        bad("collateralPosition", json!("x")),
        "settlement.collateralPosition",
    );
}
