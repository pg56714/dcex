use super::msgpack::{encode_msgpack, OrderedValue};
use super::*;

#[test]
fn signature_matches_python_vector() {
    let action = hex::decode("82a474797065a56f72646572a16101").expect("msgpack");
    assert_eq!(
        hyperliquid_signature(&action, 1_700_000_000_000, None, None, false, &[0x11; 32],)
            .expect("signature"),
        HyperliquidSignature {
            r: "0x193f5e88d621ca384beca6146a4c059b8716d5ad3da0404f6cd36f020fc87671".to_string(),
            s: "0x0c3767a2287482caef8a77be7b5c76eac08d9d8fb3080c53033e394bbb35d047".to_string(),
            v: 27,
        }
    );
}

#[test]
fn msgpack_encoder_matches_existing_order_vector() {
    let action = OrderedValue::Object(vec![
        (
            "type".to_string(),
            OrderedValue::String("order".to_string()),
        ),
        ("a".to_string(), OrderedValue::Uint(1)),
    ]);
    assert_eq!(
        hex::encode(encode_msgpack(&action)),
        "82a474797065a56f72646572a16101"
    );
}

#[test]
fn action_json_preserves_signed_field_order() {
    let action = OrderedValue::Object(vec![
        (
            "type".to_string(),
            OrderedValue::String("order".to_string()),
        ),
        (
            "orders".to_string(),
            OrderedValue::Array(vec![OrderedValue::Object(vec![
                ("a".to_string(), OrderedValue::Uint(0)),
                ("b".to_string(), OrderedValue::Bool(true)),
                ("p".to_string(), OrderedValue::String("100".to_string())),
            ])]),
        ),
        (
            "grouping".to_string(),
            OrderedValue::String("na".to_string()),
        ),
    ]);

    let json = serde_json::to_string(&action.to_json()).expect("json");
    let type_index = json.find("\"type\"").expect("type key");
    let orders_index = json.find("\"orders\"").expect("orders key");
    let grouping_index = json.find("\"grouping\"").expect("grouping key");

    assert!(type_index < orders_index);
    assert!(orders_index < grouping_index);
}
