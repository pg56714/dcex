//! Frames the private client sends, checked against the documented message shapes.

use std::time::Duration;

use serde_json::json;

use super::HyperliquidPrivateWebSocket;
use crate::ws::test_peer::TestPeer;

const USER: &str = "0xABCDEF0123456789abcdef0123456789ABCDEF01";
const USER_LOWER: &str = "0xabcdef0123456789abcdef0123456789abcdef01";
const SIGNATURE_PART: &str = "0x1111111111111111111111111111111111111111111111111111111111111111";

async fn connected() -> (HyperliquidPrivateWebSocket, TestPeer) {
    let peer = TestPeer::start().await;
    let mut client = HyperliquidPrivateWebSocket::with_url(
        USER.into(),
        peer.url.clone(),
        Duration::from_secs(5),
    )
    .expect("client");
    client.connect().await.expect("connect");
    (client, peer)
}

#[tokio::test]
async fn user_channels_subscribe_with_the_normalized_address() {
    let (mut client, mut peer) = connected().await;
    assert_eq!(client.user(), USER_LOWER);
    assert!(client.is_connected());
    client.subscribe_notifications().await.unwrap();
    client.subscribe_web_data3().await.unwrap();
    client.subscribe_clearinghouse_state().await.unwrap();
    client.subscribe_open_orders().await.unwrap();
    client.subscribe_order_updates().await.unwrap();
    client.subscribe_user_events().await.unwrap();
    client.subscribe_user_fills().await.unwrap();
    client.subscribe_user_fundings().await.unwrap();
    client
        .subscribe_user_non_funding_ledger_updates()
        .await
        .unwrap();
    client.subscribe_twap_states().await.unwrap();
    client.subscribe_user_twap_slice_fills().await.unwrap();
    client.subscribe_user_twap_history().await.unwrap();
    for channel in [
        "notification",
        "webData3",
        "clearinghouseState",
        "openOrders",
        "orderUpdates",
        "userEvents",
        "userFills",
        "userFundings",
        "userNonFundingLedgerUpdates",
        "twapStates",
        "userTwapSliceFills",
        "userTwapHistory",
    ] {
        assert_eq!(
            peer.next_json().await,
            json!({"method": "subscribe", "subscription": {"type": channel, "user": USER_LOWER}}),
            "{channel}"
        );
    }
}

#[tokio::test]
async fn dex_scoped_channels_and_fill_aggregation_carry_their_fields() {
    let (mut client, mut peer) = connected().await;
    client
        .subscribe_clearinghouse_state_for_dex("xyz")
        .await
        .unwrap();
    client.subscribe_open_orders_for_dex("xyz").await.unwrap();
    client.subscribe_twap_states_for_dex("xyz").await.unwrap();
    for channel in ["clearinghouseState", "openOrders", "twapStates"] {
        assert_eq!(
            peer.next_json().await["subscription"],
            json!({"type": channel, "user": USER_LOWER, "dex": "xyz"})
        );
    }
    client
        .subscribe_user_fills_with_aggregate_by_time(true)
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await["subscription"],
        json!({"type": "userFills", "user": USER_LOWER, "aggregateByTime": true})
    );
    client
        .unsubscribe_user_subscription("orderUpdates")
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"method": "unsubscribe", "subscription": {"type": "orderUpdates", "user": USER_LOWER}})
    );
    client
        .unsubscribe_user_subscription_for_dex("openOrders", "xyz")
        .await
        .unwrap();
    assert_eq!(peer.next_json().await["subscription"]["dex"], "xyz");
}

#[tokio::test]
async fn active_asset_data_names_the_coin_and_user() {
    let (mut client, mut peer) = connected().await;
    client.subscribe_active_asset_data("BTC").await.unwrap();
    assert_eq!(
        peer.next_json().await["subscription"],
        json!({"type": "activeAssetData", "coin": "BTC", "user": USER_LOWER})
    );
}

#[tokio::test]
async fn post_requests_wrap_info_and_signed_actions() {
    let (mut client, mut peer) = connected().await;
    client
        .post_info(7, json!({"type": "clearinghouseState", "user": USER_LOWER}))
        .await
        .unwrap();
    let frame = peer.next_json().await;
    assert_eq!(frame["method"], "post");
    assert_eq!(frame["id"], 7);
    assert_eq!(frame["request"]["type"], "info");
    assert_eq!(frame["request"]["payload"]["type"], "clearinghouseState");

    let signed = json!({
        "action": {"type": "cancel", "cancels": [{"a": 0, "o": 1}]},
        "nonce": 1_700_000_000_000_u64,
        "signature": {"r": SIGNATURE_PART, "s": SIGNATURE_PART, "v": 27},
    });
    client.post_action(8, signed.clone()).await.unwrap();
    let frame = peer.next_json().await;
    assert_eq!(frame["id"], 8);
    assert_eq!(frame["request"]["type"], "action");
    assert_eq!(frame["request"]["payload"], signed);
}

#[tokio::test]
async fn invalid_requests_are_rejected_before_sending() {
    let (mut client, mut peer) = connected().await;
    assert!(
        client
            .post_info(1, json!({"type": "explorer"}))
            .await
            .is_err()
    );
    assert!(
        client
            .post_action(2, json!({"action": {"type": "withdraw3"}, "nonce": 1}))
            .await
            .is_err()
    );
    let bad_signature = json!({
        "action": {"type": "cancel", "cancels": []},
        "nonce": 1,
        "signature": {"r": "0x12", "s": SIGNATURE_PART, "v": 27},
    });
    assert!(client.post_action(3, bad_signature).await.is_err());
    assert!(
        client
            .subscribe_user_subscription("bad type!")
            .await
            .is_err()
    );
    assert!(peer.quiet(Duration::from_millis(200)).await);
    assert!(
        HyperliquidPrivateWebSocket::with_url(
            "0x12".into(),
            peer.url.clone(),
            Duration::from_secs(1)
        )
        .is_err()
    );
}

#[tokio::test]
async fn pushed_messages_are_received_and_close_disconnects() {
    let (mut client, peer) = connected().await;
    peer.push_json(&json!({"channel": "userFills", "data": {"isSnapshot": true, "fills": []}}));
    assert_eq!(client.recv().await.unwrap()["channel"], "userFills");
    peer.push("{\"channel\":\"pong\"}");
    assert_eq!(
        client.recv_bytes().await.unwrap(),
        b"{\"channel\":\"pong\"}"
    );
    client.close().await.unwrap();
    assert!(!client.is_connected());
}

const KEY: &str = "0x1111111111111111111111111111111111111111111111111111111111111111";

fn expected_signature(
    action: &crate::exchanges::hyperliquid::msgpack::OrderedValue,
) -> serde_json::Value {
    use crate::exchanges::hyperliquid::{msgpack::encode_msgpack, signing::hyperliquid_signature};
    let signature = hyperliquid_signature(
        &encode_msgpack(action),
        1_700_000_000_000,
        Some("0x2222222222222222222222222222222222222222"),
        Some(1_700_000_060_000),
        true,
        &[0x11; 32],
    )
    .unwrap();
    json!({"r": signature.r, "s": signature.s, "v": signature.v})
}

#[tokio::test]
async fn offline_signed_cancels_and_orders_post_unchanged() {
    use crate::exchanges::hyperliquid::msgpack::OrderedValue;
    let vault = Some("0x2222222222222222222222222222222222222222");
    let cancel = HyperliquidPrivateWebSocket::sign_cancel(
        r#"[{"a": 3, "o": 77}]"#,
        1_700_000_000_000,
        KEY,
        true,
        vault,
        Some(1_700_000_060_000),
    )
    .unwrap();
    let action = OrderedValue::Object(vec![
        ("type".into(), OrderedValue::String("cancel".into())),
        (
            "cancels".into(),
            OrderedValue::Array(vec![OrderedValue::Object(vec![
                ("a".into(), OrderedValue::Uint(3)),
                ("o".into(), OrderedValue::Uint(77)),
            ])]),
        ),
    ]);
    assert_eq!(cancel["action"], action.to_json());
    assert_eq!(cancel["signature"], expected_signature(&action));
    assert_eq!(cancel["nonce"], 1_700_000_000_000_u64);
    assert_eq!(
        cancel["vaultAddress"],
        "0x2222222222222222222222222222222222222222"
    );
    assert_eq!(cancel["expiresAfter"], 1_700_000_060_000_u64);

    let order = HyperliquidPrivateWebSocket::sign_order(
        r#"[{"a": 0, "b": true, "p": "100", "s": "0.01", "r": false, "t": {"limit": {"tif": "Gtc"}}}]"#,
        "na",
        1_700_000_000_000,
        KEY,
        true,
        vault,
        Some(1_700_000_060_000),
    )
    .unwrap();
    assert_eq!(order["action"]["type"], "order");
    assert_eq!(order["action"]["grouping"], "na");
    let keys: Vec<&String> = order["action"]["orders"][0]
        .as_object()
        .unwrap()
        .keys()
        .collect();
    assert_eq!(keys, ["a", "b", "p", "s", "r", "t"]);

    let (mut client, mut peer) = connected().await;
    client.post_action(9, cancel.clone()).await.unwrap();
    assert_eq!(peer.next_json().await["request"]["payload"], cancel);
}

#[test]
fn offline_signing_rejects_malformed_input() {
    let sign_order = |orders: &str, grouping: &str| {
        HyperliquidPrivateWebSocket::sign_order(orders, grouping, 1, KEY, false, None, None)
    };
    let order = r#"[{"a": 0, "b": true, "p": "100", "s": "1", "r": false, "t": {"limit": {"tif": "Gtc"}}}]"#;
    assert!(sign_order(order, "bogus").is_err());
    assert!(sign_order("[]", "na").is_err());
    assert!(sign_order("{}", "na").is_err());
    assert!(sign_order(r#"[{"a": 0}]"#, "na").is_err());
    assert!(
        HyperliquidPrivateWebSocket::sign_order(order, "na", 1, "0x12", false, None, None).is_err()
    );
    let sign_cancel = |cancels: &str| {
        HyperliquidPrivateWebSocket::sign_cancel(cancels, 1, KEY, false, None, None)
    };
    assert!(sign_cancel("[]").is_err());
    assert!(sign_cancel(r#"[{"a": 1}]"#).is_err());
    assert!(sign_cancel(r#"[{"a": 1, "o": -2}]"#).is_err());
    assert!(sign_cancel(r#"[{"a": 1, "o": 2, "x": 3}]"#).is_err());
}

#[tokio::test]
async fn raw_and_dex_user_subscriptions() {
    let (mut client, mut peer) = connected().await;
    client
        .subscribe_user_subscription_for_dex("openOrders", "xyz")
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await["subscription"],
        json!({"type": "openOrders", "user": USER_LOWER, "dex": "xyz"})
    );
    client
        .subscribe(json!({"type": "userFills", "user": USER_LOWER}))
        .await
        .unwrap();
    client
        .unsubscribe(json!({"type": "userFills", "user": USER_LOWER}))
        .await
        .unwrap();
    assert_eq!(peer.next_json().await["method"], "subscribe");
    assert_eq!(peer.next_json().await["method"], "unsubscribe");
}
