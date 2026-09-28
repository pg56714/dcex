use super::helpers::*;

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
