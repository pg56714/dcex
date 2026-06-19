use super::msgpack::{encode_msgpack, OrderedValue};
use super::*;

#[test]
fn signature_matches_python_vector() {
    let action = hex::decode("82a474797065a56f72646572a16101").expect("msgpack");
    assert_eq!(
        hyperliquid_signature(&action, 1_700_000_000_000, None, None, false, &[0x11; 32],)
            .expect("signature"),
        HyperliquidSignature {
            r: "193f5e88d621ca384beca6146a4c059b8716d5ad3da0404f6cd36f020fc87671".to_string(),
            s: "0c3767a2287482caef8a77be7b5c76eac08d9d8fb3080c53033e394bbb35d047".to_string(),
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
