use super::helpers::*;

#[test]
fn futures_dead_mans_switch_rejects_invalid_timeout_before_network() {
    let client = KrakenClient::public(Duration::from_secs(1)).expect("client");
    let error = crate::http::block_on(async move {
        client
            .private_request(
                "cancel_futures_all_orders_after",
                vec![("timeout".into(), "-1".into())],
            )
            .await
    })
    .expect_err("negative timeout");
    assert!(error.to_string().contains("non-negative"));
}

#[test]
fn xstock_symbol_infers_tokenized_asset_class() {
    let client = KrakenClient::public(Duration::from_secs(1)).expect("client");
    assert_eq!(
        client
            .spot_asset_class("AAPLx-USD-SPOT")
            .expect("asset class"),
        Some("tokenized_asset".to_string())
    );
    assert_eq!(
        client
            .spot_asset_class("BTC-USD-SPOT")
            .expect("asset class"),
        None
    );
}

type Pairs = Vec<(&'static str, &'static str)>;

fn with_base(
    base: &[(&'static str, &'static str)],
    extra: &[(&'static str, &'static str)],
) -> Pairs {
    base.iter().chain(extra).copied().collect()
}

#[test]
fn single_orders_reject_inconsistent_fields_before_network() {
    let spot_base = [
        ("product_symbol", "BTC-USD-SPOT"),
        ("side", "buy"),
        ("volume", "1"),
    ];
    let futures_base = [
        ("product_symbol", "BTC-USD-SWAP"),
        ("side", "buy"),
        ("size", "1"),
    ];
    let spot = |extra: &[(&'static str, &'static str)]| with_base(&spot_base, extra);
    let futures = |extra: &[(&'static str, &'static str)]| with_base(&futures_base, extra);
    let long_id: &'static str = Box::leak("x".repeat(101).into_boxed_str());
    let cases: Vec<(&str, Pairs, &str)> = vec![
        (
            "amend_spot_order",
            vec![("txid", "T1"), ("post_only", "yes")],
            "post_only must be true or false",
        ),
        (
            "edit_futures_order",
            vec![("orderId", "1"), ("size", "1"), ("qtyMode", "SOME")],
            "qtyMode must be ABSOLUTE or RELATIVE",
        ),
        (
            "place_spot_order",
            spot(&[
                ("ordertype", "market"),
                ("userref", "1"),
                ("cl_ord_id", "c"),
            ]),
            "mutually exclusive",
        ),
        (
            "place_spot_order",
            spot(&[("ordertype", "limit")]),
            "price is required for Kraken Spot limit orders",
        ),
        (
            "place_spot_order",
            spot(&[("ordertype", "stop-loss-limit"), ("price", "1")]),
            "price2 is required",
        ),
        (
            "place_spot_order",
            spot(&[("ordertype", "iceberg"), ("price", "1")]),
            "displayvol is required",
        ),
        (
            "place_spot_order",
            spot(&[("ordertype", "market"), ("timeinforce", "DAY")]),
            "unsupported Kraken Spot timeinforce",
        ),
        (
            "place_spot_order",
            spot(&[
                ("ordertype", "limit"),
                ("price", "1"),
                ("timeinforce", "GTD"),
            ]),
            "expiretm is required",
        ),
        (
            "place_spot_order",
            spot(&[("ordertype", "market"), ("asset_class", "crypto")]),
            "unsupported Kraken Spot asset_class",
        ),
        (
            "place_spot_order",
            spot(&[
                ("ordertype", "stop-loss"),
                ("price", "1"),
                ("trigger", "mark"),
            ]),
            "unsupported Kraken Spot trigger",
        ),
        (
            "place_spot_order",
            spot(&[("ordertype", "market"), ("stptype", "none")]),
            "unsupported Kraken Spot stptype",
        ),
        (
            "place_futures_limit_order",
            futures(&[("limitPrice", "1"), ("price", "1")]),
            "pass either limitPrice or price",
        ),
        (
            "place_futures_order",
            futures(&[("orderType", "gtc")]),
            "unsupported Kraken Futures order type",
        ),
        (
            "place_futures_order",
            futures(&[("orderType", "take_profit")]),
            "stopPrice is required",
        ),
        (
            "place_futures_order",
            futures(&[("orderType", "fok")]),
            "limitPrice is required for Kraken Futures fok",
        ),
        (
            "place_futures_order",
            futures(&[
                ("orderType", "trailing_stop"),
                ("trailingStopMaxDeviation", "1"),
                ("trailingStopDeviationUnit", "PERCENT"),
                ("stopPrice", "1"),
            ]),
            "must not include stopPrice or limitPrice",
        ),
        (
            "place_futures_order",
            futures(&[
                ("orderType", "stp"),
                ("stopPrice", "1"),
                ("limitPriceOffsetValue", "1"),
            ]),
            "must be provided together",
        ),
        (
            "place_futures_order",
            futures(&[
                ("orderType", "mkt"),
                ("limitPriceOffsetValue", "1"),
                ("limitPriceOffsetUnit", "PERCENT"),
            ]),
            "only valid for trigger orders",
        ),
        (
            "place_futures_order",
            futures(&[
                ("orderType", "stp"),
                ("stopPrice", "1"),
                ("triggerSignal", "spot"),
            ]),
            "unsupported Kraken Futures triggerSignal",
        ),
        (
            "place_futures_order",
            futures(&[
                ("orderType", "trailing_stop"),
                ("trailingStopMaxDeviation", "80"),
                ("trailingStopDeviationUnit", "PERCENT"),
            ]),
            "trailingStopMaxDeviation must be between",
        ),
        (
            "place_futures_order",
            futures(&[
                ("orderType", "stp"),
                ("stopPrice", "1"),
                ("limitPriceOffsetValue", "1"),
                ("limitPriceOffsetUnit", "TICKS"),
            ]),
            "unsupported Kraken Futures limitPriceOffsetUnit",
        ),
        (
            "place_futures_order",
            futures(&[("orderType", "mkt"), ("cliOrdId", long_id)]),
            "at most 100 characters",
        ),
    ];
    for (method, params, expected) in cases {
        let params = params
            .into_iter()
            .map(|(key, value)| (key.to_string(), value.to_string()))
            .collect();
        let client = KrakenClient::public(Duration::from_secs(1)).expect("client");
        let error =
            crate::http::block_on(async move { client.private_request(method, params).await })
                .expect_err(expected)
                .to_string();
        assert!(error.contains(expected), "{method}: {error}");
    }
}

#[test]
fn batch_instructions_are_validated_field_by_field() {
    use super::super::trading_controls::{validate_batch_order, validate_futures_instruction};
    use serde_json::{Value, json};

    fn with(base: &Value, changes: Value) -> Value {
        let mut value = base.clone();
        for (key, change) in changes.as_object().unwrap() {
            if change.is_null() {
                value.as_object_mut().unwrap().remove(key);
            } else {
                value[key] = change.clone();
            }
        }
        value
    }
    let spot = json!({"ordertype": "limit", "type": "buy", "volume": "1", "price": "10"});
    validate_batch_order(&spot).expect("valid spot order");
    for (changes, expected) in [
        (json!({"bogus": 1}), "unsupported batch order field"),
        (
            json!({"volume": ""}),
            "ordertype, type and volume are required strings",
        ),
        (json!({"type": "hold"}), "invalid order side"),
        (json!({"ordertype": "oco"}), "unsupported ordertype"),
        (json!({"volume": "x"}), "invalid volume"),
        (json!({"volume": "0"}), "zero volume is reserved"),
        (
            json!({"userref": 1, "cl_ord_id": "c"}),
            "mutually exclusive",
        ),
        (
            json!({"reduce_only": "true"}),
            "reduce_only must be a JSON boolean",
        ),
        (
            json!({"price": null}),
            "price is required for this order type",
        ),
        (
            json!({"ordertype": "take-profit-limit"}),
            "price2 is required",
        ),
        (
            json!({"ordertype": "iceberg", "displayvol": "0.01"}),
            "displayvol must be between",
        ),
        (json!({"timeinforce": "GTD"}), "GTD requires expiretm"),
    ] {
        let error = validate_batch_order(&with(&spot, changes)).expect_err(expected);
        assert!(error.to_string().contains(expected), "{error}");
    }

    let send = json!({"order": "send", "order_tag": "t", "orderType": "lmt", "symbol": "PF_XBTUSD",
                      "side": "buy", "size": 1, "limitPrice": 10});
    validate_futures_instruction(&send).expect("valid send");
    let edit = json!({"order": "edit", "order_id": "1", "size": 2});
    validate_futures_instruction(&edit).expect("valid edit");
    let long_id = "x".repeat(101);
    for (base, changes, expected) in [
        (
            &send,
            json!({"order": "replace"}),
            "order must be send, edit or cancel",
        ),
        (
            &send,
            json!({"qtyMode": "ABSOLUTE"}),
            "unsupported batch instruction field",
        ),
        (&send, json!({"size": "1"}), "positive JSON numbers"),
        (&send, json!({"symbol": " "}), "must be nonempty strings"),
        (
            &send,
            json!({"cliOrdId": long_id}),
            "cliOrdId exceeds 100 characters",
        ),
        (
            &send,
            json!({"reduceOnly": "true"}),
            "reduceOnly must be a JSON boolean",
        ),
        (&send, json!({"side": "hold"}), "unsupported batch enum"),
        (
            &send,
            json!({"order_tag": null}),
            "missing a required field",
        ),
        (
            &send,
            json!({"limitPrice": null}),
            "limit order requires limitPrice",
        ),
        (
            &send,
            json!({"orderType": "stp", "stopPrice": 9, "limitPrice": null}),
            "stp also requires limitPrice",
        ),
        (
            &send,
            json!({"orderType": "trailing_stop", "trailingStopMaxDeviation": 1}),
            "trailing_stop requires deviation fields",
        ),
        (
            &send,
            json!({"orderType": "trailing_stop", "limitPrice": null,
                   "trailingStopMaxDeviation": 60, "trailingStopDeviationUnit": "PERCENT"}),
            "trailing percentage must be 0.1..=50",
        ),
        (
            &edit,
            json!({"cliOrdId": "c"}),
            "provide exactly one of order_id and cliOrdId",
        ),
        (
            &edit,
            json!({"size": null}),
            "edit requires at least one change",
        ),
    ] {
        let error = validate_futures_instruction(&with(base, changes)).expect_err(expected);
        assert!(error.to_string().contains(expected), "{error}");
    }
}
