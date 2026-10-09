//! Frames the private client sends: channel names, auth tokens and transaction envelopes.

use std::time::Duration;

use serde_json::{Value, json};

use super::LighterPrivateWebSocket;
use crate::ws::test_peer::TestPeer;

const ACCOUNT: u64 = 12;
const API_KEY: u64 = 3;

fn private_key() -> String {
    "01".to_string() + &"00".repeat(39)
}

async fn connected() -> (LighterPrivateWebSocket, TestPeer) {
    let peer = TestPeer::start().await;
    let mut client = LighterPrivateWebSocket::with_urls(
        ACCOUNT,
        API_KEY,
        private_key(),
        peer.url.clone(),
        "http://127.0.0.1:9".to_string(),
        Duration::from_secs(5),
    )
    .expect("client");
    client.connect().await.expect("connect");
    (client, peer)
}

fn tx_info(account: u64) -> String {
    json!({"AccountIndex": account, "ApiKeyIndex": API_KEY, "Nonce": 5, "ExpiredAt": 6, "Sig": "signed"})
        .to_string()
}

#[tokio::test]
async fn public_account_channels_have_no_auth() {
    let (mut client, mut peer) = connected().await;
    assert_eq!(client.account_index(), ACCOUNT);
    client.subscribe_account_all().await.unwrap();
    client.subscribe_user_stats().await.unwrap();
    for channel in ["account_all/12", "user_stats/12"] {
        assert_eq!(
            peer.next_json().await,
            json!({"type": "subscribe", "channel": channel})
        );
    }
    client.unsubscribe("account_all/12").await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"type": "unsubscribe", "channel": "account_all/12"})
    );
}

#[tokio::test]
async fn authenticated_channels_carry_a_fresh_auth_token() {
    let (mut client, mut peer) = connected().await;
    client.subscribe_account_market(3).await.unwrap();
    client.subscribe_account_tx().await.unwrap();
    client.subscribe_account_all_orders().await.unwrap();
    client.subscribe_pool_data().await.unwrap();
    client.subscribe_pool_info().await.unwrap();
    client.subscribe_notifications().await.unwrap();
    client.subscribe_account_orders(3).await.unwrap();
    client.subscribe_account_all_trades().await.unwrap();
    client.subscribe_account_all_positions().await.unwrap();
    client.subscribe_account_all_assets().await.unwrap();
    client
        .subscribe_account_spot_avg_entry_prices()
        .await
        .unwrap();
    client.subscribe_rfq().await.unwrap();
    client
        .subscribe_private_market_channel("trade", 4)
        .await
        .unwrap();
    for channel in [
        "account_market/3/12",
        "account_tx/12",
        "account_all_orders/12",
        "pool_data/12",
        "pool_info/12",
        "notification/12",
        "account_orders/3/12",
        "account_all_trades/12",
        "account_all_positions/12",
        "account_all_assets/12",
        "account_spot_avg_entry_prices/12",
        "rfq",
        "trade/4",
    ] {
        let frame = peer.next_json().await;
        assert_eq!(frame["type"], "subscribe", "{channel}");
        assert_eq!(frame["channel"], channel);
        let auth = frame["auth"].as_str().expect("auth token");
        assert!(!auth.is_empty());
    }
    // The deadline is a validity window in seconds (1..=28800), not a timestamp.
    assert!(client.create_auth_token_with_deadline(600).is_ok());
    for out_of_range in [0, 28_801] {
        assert!(
            client
                .create_auth_token_with_deadline(out_of_range)
                .is_err()
        );
    }
    assert!(client.create_auth_token_with_api_key_index(API_KEY).is_ok());
    assert!(
        client
            .create_auth_token_with_deadline_and_api_key_index(600, API_KEY)
            .is_ok()
    );
}

#[tokio::test]
async fn transactions_keep_their_signed_payloads() {
    let (mut client, mut peer) = connected().await;
    client
        .send_tx("req-1", 14, &tx_info(ACCOUNT))
        .await
        .unwrap();
    let frame = peer.next_json().await;
    assert_eq!(frame["type"], "jsonapi/sendtx");
    assert_eq!(frame["data"]["id"], "req-1");
    assert_eq!(frame["data"]["tx_type"], 14);
    assert_eq!(frame["data"]["tx_info"]["Sig"], "signed");

    client
        .send_tx_batch(
            "req-2",
            vec![14, 15],
            vec![tx_info(ACCOUNT), tx_info(ACCOUNT)],
        )
        .await
        .unwrap();
    let frame = peer.next_json().await;
    assert_eq!(frame["type"], "jsonapi/sendtxbatch");
    let types: Vec<u64> =
        serde_json::from_str(frame["data"]["tx_types"].as_str().unwrap()).unwrap();
    assert_eq!(types, vec![14, 15]);
    let infos: Vec<String> =
        serde_json::from_str(frame["data"]["tx_infos"].as_str().unwrap()).unwrap();
    assert_eq!(infos.len(), 2);
}

#[tokio::test]
async fn foreign_or_unsigned_transactions_are_rejected_before_sending() {
    let (mut client, mut peer) = connected().await;
    assert!(
        client
            .send_tx("x", 14, &tx_info(ACCOUNT + 1))
            .await
            .is_err()
    );
    assert!(client.send_tx("x", 99, &tx_info(ACCOUNT)).await.is_err());
    assert!(client.send_tx("", 14, &tx_info(ACCOUNT)).await.is_err());
    let unsigned: Value =
        json!({"AccountIndex": ACCOUNT, "ApiKeyIndex": 1, "Nonce": 1, "ExpiredAt": 1});
    assert!(
        client
            .send_tx("x", 14, &unsigned.to_string())
            .await
            .is_err()
    );
    assert!(client.send_tx_batch("x", vec![], vec![]).await.is_err());
    assert!(client.subscribe("not a channel!").await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn pings_and_pushed_messages_flow_until_close() {
    let (mut client, peer) = connected().await;
    client.ping().await.unwrap();
    peer.push_json(&json!({"type": "update/account_all", "account": ACCOUNT}));
    assert_eq!(client.recv().await.unwrap()["type"], "update/account_all");
    peer.push("{\"type\":\"pong\"}");
    assert_eq!(client.recv_bytes().await.unwrap(), b"{\"type\":\"pong\"}");
    assert!(client.is_connected());
    client.close().await.unwrap();
    assert!(!client.is_connected());
}

#[tokio::test]
async fn constructors_auth_tokens_and_transaction_fields() {
    use crate::exchanges::lighter::chains::LighterNetwork;
    use crate::exchanges::lighter::credentials::LighterCredentials;

    let timeout = Duration::from_secs(1);
    assert!(
        LighterPrivateWebSocket::with_network(
            ACCOUNT,
            API_KEY,
            private_key(),
            LighterNetwork::Mainnet,
            timeout
        )
        .is_ok()
    );
    let credentials = LighterCredentials::new(ACCOUNT, API_KEY, private_key()).unwrap();
    assert!(
        LighterPrivateWebSocket::with_credentials(credentials, LighterNetwork::Mainnet, timeout)
            .is_ok()
    );
    assert!(super::LighterPublicWebSocket::with_network(LighterNetwork::Testnet, timeout).is_ok());

    let (mut client, mut peer) = connected().await;
    let error = client
        .subscribe_with_auth("account_tx/12", " ".into())
        .await
        .unwrap_err()
        .to_string();
    assert!(error.contains("auth token must not be empty"), "{error}");
    let error = client
        .subscribe("account_all/abc")
        .await
        .unwrap_err()
        .to_string();
    assert!(
        error.contains("unsupported Lighter WebSocket channel"),
        "{error}"
    );
    let unsigned_nonce = json!({"AccountIndex": ACCOUNT, "ApiKeyIndex": API_KEY, "Nonce": "5", "ExpiredAt": 6, "Sig": "s"});
    let error = client
        .send_tx("x", 14, &unsigned_nonce.to_string())
        .await
        .unwrap_err()
        .to_string();
    assert!(
        error.contains("Nonce must be an unsigned integer"),
        "{error}"
    );
    assert!(peer.quiet(Duration::from_millis(200)).await);
}
