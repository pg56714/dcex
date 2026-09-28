use super::helpers::*;

#[test]
fn spot_cancel_replace_uses_official_path_and_required_fields() {
    let (url, server) = recording_server();
    let client = BingxClient::with_base_url(
        Some("api-key".into()),
        Some("secret".into()),
        Duration::from_secs(2),
        url,
    )
    .expect("client");
    block_on(async move {
        client
            .private_request(
                "replace_spot_order",
                vec![
                    ("product_symbol".into(), "BTC-USDT-SPOT".into()),
                    ("cancelOrderId".into(), "123".into()),
                    ("cancelReplaceMode".into(), "STOP_ON_FAILURE".into()),
                    ("side".into(), "BUY".into()),
                    ("type_".into(), "LIMIT".into()),
                    ("quantity".into(), "0.1".into()),
                    ("price".into(), "50000".into()),
                ],
            )
            .await
    })
    .expect("replace");
    let line = server.join().expect("server");
    assert!(
        line.starts_with("POST /openApi/spot/v1/trade/order/cancelReplace?"),
        "{line}"
    );
    assert!(line.contains("cancelOrderId=123"), "{line}");
    assert!(line.contains("cancelReplaceMode=STOP_ON_FAILURE"), "{line}");
    assert!(line.contains("symbol=BTC-USDT"), "{line}");
}

#[test]
fn spot_cancel_all_after_validates_timeout_and_uses_signed_route() {
    let (url, server) = recording_server();
    let client = BingxClient::with_base_url(
        Some("api-key".into()),
        Some("secret".into()),
        Duration::from_secs(2),
        url,
    )
    .expect("client");
    block_on(async move {
        client
            .private_request(
                "set_spot_cancel_all_after",
                vec![
                    ("type_".into(), "ACTIVATE".into()),
                    ("timeOut".into(), "30".into()),
                ],
            )
            .await
    })
    .expect("activate");
    let line = server.join().expect("server");
    assert!(
        line.starts_with("POST /openApi/spot/v1/trade/cancelAllAfter?"),
        "{line}"
    );
    assert!(line.contains("type=ACTIVATE"), "{line}");
    assert!(line.contains("timeOut=30"), "{line}");
    assert!(line.contains("signature="), "{line}");

    let client = BingxClient::public(Duration::from_secs(1)).expect("client");
    assert!(
        block_on(async move {
            client
                .private_request(
                    "set_spot_cancel_all_after",
                    vec![
                        ("type_".into(), "ACTIVATE".into()),
                        ("timeOut".into(), "9".into()),
                    ],
                )
                .await
        })
        .is_err()
    );
}
