//! Local checks for Spot v2 trading requests. Each rejection is matched by its message, so a
//! test cannot pass because some unrelated rule fired first.

use serde_json::{Value, json};

use super::trading::validate;

#[track_caller]
fn rejects(method: &str, params: Value, reason: &str) {
    let error = validate(method, &params).expect_err(reason).to_string();
    assert!(error.contains(reason), "expected {reason:?}, got {error:?}");
}

fn limit() -> Value {
    json!({"symbol": "BTC/USD", "side": "buy", "order_type": "limit", "order_qty": 1, "limit_price": 100})
}

fn with(mut base: Value, extra: Value) -> Value {
    base.as_object_mut()
        .unwrap()
        .extend(extra.as_object().unwrap().clone());
    base
}

#[test]
fn valid_requests_pass() {
    let ok = |method: &str, params: Value| validate(method, &params).unwrap();
    ok("add_order", limit());
    ok(
        "add_order",
        json!({"symbol": "BTC/USD", "side": "buy", "order_type": "market", "cash_order_qty": 50}),
    );
    ok(
        "add_order",
        with(
            limit(),
            json!({"order_type": "iceberg", "order_qty": 10, "display_qty": 1}),
        ),
    );
    ok(
        "add_order",
        json!({"symbol": "BTC/USD", "side": "sell", "order_type": "stop-loss", "order_qty": 1, "triggers": {"reference": "index", "price": 90, "price_type": "static"}}),
    );
    ok(
        "add_order",
        with(
            limit(),
            json!({"time_in_force": "gtd", "expire_time": "2030-01-01T00:00:00Z", "post_only": true, "cl_ord_id": "c1", "fee_preference": "quote", "stp_type": "cancel_both"}),
        ),
    );
    ok(
        "add_order",
        with(
            limit(),
            json!({"conditional": {"order_type": "take-profit", "trigger_price": 120, "trigger_price_type": "static"}}),
        ),
    );
    ok(
        "amend_order",
        json!({"cl_ord_id": "c1", "limit_price": 101, "post_only": true}),
    );
    ok("cancel_order", json!({"order_userref": [7]}));
    ok("cancel_all", json!({}));
    ok("cancel_after", json!({"timeout": 0}));
    ok(
        "batch_add",
        json!({"symbol": "BTC/USD", "validate": true, "orders": [
            {"side": "buy", "order_type": "limit", "order_qty": 1, "limit_price": 100},
            {"side": "sell", "order_type": "market", "order_qty": 1},
        ]}),
    );
    ok(
        "batch_cancel",
        json!({"orders": ["O1"], "cl_ord_id": ["c1"]}),
    );
}

#[test]
fn methods_parameters_and_scalar_types() {
    rejects("withdraw", json!({}), "unsupported trading method");
    rejects("add_order", json!([]), "params must be a JSON object");
    rejects(
        "add_order",
        with(limit(), json!({"leverage": 2})),
        "unsupported or deprecated trading parameter",
    );
    rejects(
        "add_order",
        with(limit(), json!({"order_qty": -1})),
        "quantity must be a positive JSON number",
    );
    rejects(
        "add_order",
        with(limit(), json!({"limit_price": "100"})),
        "price must be a JSON number",
    );
    rejects(
        "add_order",
        with(limit(), json!({"post_only": "true"})),
        "boolean fields require JSON booleans",
    );
    rejects(
        "add_order",
        with(limit(), json!({"cl_ord_id": ""})),
        "cl_ord_id cannot be empty",
    );
    rejects(
        "add_order",
        with(limit(), json!({"order_userref": 3_000_000_000_u64})),
        "order_userref must be int32",
    );
    for (key, value) in [
        ("time_in_force", "day"),
        ("fee_preference", "usd"),
        ("stp_type", "none"),
        ("limit_price_type", "abs"),
    ] {
        rejects(
            "add_order",
            with(limit(), json!({key: value})),
            &format!("unsupported {key}"),
        );
    }
    rejects(
        "amend_order",
        json!({"order_id": "O1", "trigger_price_type": "abs", "trigger_price": 1}),
        "unsupported trigger_price_type",
    );
}

#[test]
fn order_shapes_follow_each_type() {
    rejects(
        "add_order",
        with(limit(), json!({"order_type": "oco"})),
        "unsupported order_type",
    );
    rejects(
        "add_order",
        with(limit(), json!({"side": "long"})),
        "side must be buy or sell",
    );
    let mut no_symbol = limit();
    no_symbol.as_object_mut().unwrap().remove("symbol");
    rejects("add_order", no_symbol, "symbol is required");
    rejects(
        "add_order",
        with(limit(), json!({"cash_order_qty": 5})),
        "provide exactly one of order_qty, cash_order_qty",
    );
    rejects(
        "add_order",
        json!({"symbol": "BTC/USD", "side": "sell", "order_type": "market", "cash_order_qty": 5}),
        "cash_order_qty requires a buy market order without margin",
    );
    rejects(
        "add_order",
        json!({"symbol": "BTC/USD", "side": "buy", "order_type": "market", "cash_order_qty": 5, "margin": true}),
        "cash_order_qty requires a buy market order without margin",
    );
    let mut no_price = limit();
    no_price.as_object_mut().unwrap().remove("limit_price");
    rejects("add_order", no_price, "limit_price is required");
    rejects(
        "add_order",
        with(limit(), json!({"limit_price": -5})),
        "limit_price must be positive for non-trailing orders",
    );
    rejects(
        "add_order",
        with(limit(), json!({"order_type": "iceberg"})),
        "iceberg requires display_qty",
    );
    rejects(
        "add_order",
        with(
            limit(),
            json!({"order_type": "iceberg", "order_qty": 100, "display_qty": 1}),
        ),
        "display_qty must be between order_qty/15 and order_qty",
    );
    rejects(
        "add_order",
        with(
            limit(),
            json!({"order_type": "iceberg", "order_qty": 1, "display_qty": 2}),
        ),
        "display_qty must be between order_qty/15 and order_qty",
    );
    rejects(
        "add_order",
        with(limit(), json!({"post_only": true, "time_in_force": "ioc"})),
        "post_only is incompatible with ioc/fok",
    );
    rejects(
        "add_order",
        with(limit(), json!({"time_in_force": "gtd"})),
        "expire_time is required",
    );
    rejects(
        "add_order",
        with(limit(), json!({"cl_ord_id": "c1", "order_userref": 1})),
        "cl_ord_id and order_userref are mutually exclusive",
    );
    rejects(
        "add_order",
        with(limit(), json!({"triggers": {"price": 1}})),
        "triggers require a triggered order type",
    );
    rejects(
        "add_order",
        with(limit(), json!({"conditional": 1})),
        "conditional must be an object",
    );
    rejects(
        "add_order",
        with(limit(), json!({"conditional": {"order_type": "market"}})),
        "unsupported order_type",
    );
    rejects(
        "add_order",
        with(
            limit(),
            json!({"conditional": {"order_type": "limit", "size": 1}}),
        ),
        "unsupported or deprecated trading parameter",
    );
}

#[test]
fn triggered_orders_need_valid_triggers() {
    let stop = |triggers: Value| json!({"symbol": "BTC/USD", "side": "sell", "order_type": "stop-loss", "order_qty": 1, "triggers": triggers});
    rejects(
        "add_order",
        json!({"symbol": "BTC/USD", "side": "sell", "order_type": "take-profit", "order_qty": 1}),
        "triggered orders require triggers",
    );
    rejects(
        "add_order",
        stop(json!({"price": 90, "offset": 1})),
        "unsupported or deprecated trading parameter",
    );
    rejects(
        "add_order",
        stop(json!({"price": "90"})),
        "trigger price must be a JSON number",
    );
    rejects(
        "add_order",
        stop(json!({"price": 90, "reference": "mark"})),
        "unsupported reference",
    );
    rejects(
        "add_order",
        stop(json!({"price": 90, "price_type": "abs"})),
        "unsupported price_type",
    );
    rejects(
        "add_order",
        stop(json!({"price": -1})),
        "static trigger price must be positive",
    );
    // Percentage triggers may be negative offsets.
    validate(
        "add_order",
        &stop(json!({"price": -2, "price_type": "pct"})),
    )
    .unwrap();
}

#[test]
fn amend_cancel_and_batch_rules() {
    rejects(
        "amend_order",
        json!({"order_qty": 1}),
        "provide exactly one of order_id, cl_ord_id",
    );
    rejects(
        "amend_order",
        json!({"order_id": "O1", "cl_ord_id": "c1", "order_qty": 1}),
        "provide exactly one of order_id, cl_ord_id",
    );
    rejects(
        "amend_order",
        json!({"order_id": "O1", "post_only": true}),
        "amend requires a quantity or price change",
    );
    rejects(
        "cancel_after",
        json!({"timeout": -1}),
        "timeout must be an integer from 0 to 86399",
    );
    rejects(
        "cancel_order",
        json!({}),
        "cancel list is empty or exceeds batch limit 50",
    );
    rejects(
        "cancel_order",
        json!({"order_id": []}),
        "cancel identifiers must be nonempty arrays",
    );
    rejects(
        "cancel_order",
        json!({"order_id": "O1"}),
        "cancel identifiers must be nonempty arrays",
    );
    rejects(
        "cancel_order",
        json!({"order_id": [1]}),
        "invalid cancel identifier type",
    );
    rejects(
        "cancel_order",
        json!({"order_userref": [3_000_000_000_u64]}),
        "invalid cancel identifier type",
    );
    let many: Vec<String> = (0..51).map(|index| format!("O{index}")).collect();
    rejects(
        "batch_cancel",
        json!({"orders": many}),
        "cancel list is empty or exceeds batch limit 50",
    );

    let order = json!({"side": "buy", "order_type": "limit", "order_qty": 1, "limit_price": 100});
    rejects(
        "batch_add",
        json!({"orders": [order.clone(), order.clone()]}),
        "symbol is required",
    );
    rejects(
        "batch_add",
        json!({"symbol": "BTC/USD", "orders": [order.clone()]}),
        "batch_add requires 2..=15 orders",
    );
    rejects(
        "batch_add",
        json!({"symbol": "BTC/USD", "orders": [order.clone(), 1]}),
        "batch order must be an object",
    );
    rejects(
        "batch_add",
        json!({"symbol": "BTC/USD", "orders": [order.clone(), with(order.clone(), json!({"symbol": "ETH/USD"}))]}),
        "batch order cannot override batch-level parameters",
    );
    rejects(
        "batch_add",
        json!({"symbol": "BTC/USD", "orders": [order.clone(), with(order, json!({"order_type": "oco"}))]}),
        "unsupported order_type",
    );
}
