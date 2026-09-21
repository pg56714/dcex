use std::collections::BTreeMap;
use std::time::Duration;

use serde_json::json;

use super::client::{ArcusClient, ArcusSpotClient};
use super::params::{decimal_product_below, exact_units};
use super::signing::legacy_signing_message;

#[test]
fn decimal_to_engine_units_is_exact() {
    assert_eq!(exact_units("0.001", "0.0001").unwrap(), 10);
    assert!(exact_units("0.0015", "0.001").is_err());
    assert!(decimal_product_below("100", "0.01", "5").unwrap());
}

#[test]
fn secret_must_match_public_key() {
    let secret = "00".repeat(32);
    assert!(ArcusClient::new(
        Some("ff".repeat(32)),
        Some(secret),
        None,
        0,
        true,
        Duration::from_secs(1)
    )
    .is_err());
}

#[test]
fn legacy_signing_message_sorts_json_keys() {
    let mut body = BTreeMap::new();
    body.insert("marketId".to_string(), json!(7));
    body.insert("address".to_string(), json!("0xabc"));
    body.insert("accountIndex".to_string(), json!(0));
    assert_eq!(
        legacy_signing_message(123, "cancelAllOrders", &body).unwrap(),
        br#"123cancelAllOrders{"accountIndex":0,"address":"0xabc","marketId":7}"#
    );
}

#[test]
fn spot_status_wrapper_sets_arcus_venue() {
    let client = ArcusSpotClient::new(None, false, Duration::from_secs(1)).unwrap();
    let request = client.get_status(format!("0x{}", "11".repeat(32)));
    assert_eq!(request.method_name, "get_status");
    assert!(request.params.contains(&("venue".into(), "arcus".into())));
}
