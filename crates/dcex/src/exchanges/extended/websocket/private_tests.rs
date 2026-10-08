//! The account stream authenticates in the handshake: path, API key and user agent.

use std::time::Duration;

use super::{ExtendedPrivateWebSocket, USER_AGENT};
use crate::ws::test_peer::TestPeer;

#[tokio::test]
async fn account_stream_sends_key_and_user_agent_in_the_handshake() {
    let mut peer = TestPeer::start().await;
    let mut client = ExtendedPrivateWebSocket::with_url(
        "  extended-key  ".into(),
        peer.url.clone(),
        Duration::from_secs(5),
    )
    .unwrap();
    client.subscribe_account().await.unwrap();
    let handshake = peer.next_handshake().await;
    assert!(handshake.path.ends_with("/account"), "{}", handshake.path);
    assert_eq!(handshake.header("X-Api-Key"), Some("extended-key"));
    assert_eq!(handshake.header("User-Agent"), Some(USER_AGENT));
    assert!(client.is_connected());
    client.ping().await.unwrap();
    peer.push("{\"type\":\"SNAPSHOT\"}");
    assert_eq!(
        client.recv_bytes().await.unwrap(),
        b"{\"type\":\"SNAPSHOT\"}"
    );
    client.close().await.unwrap();
    assert!(!client.is_connected());
}

#[test]
fn empty_keys_and_non_websocket_urls_are_rejected() {
    assert!(
        ExtendedPrivateWebSocket::with_url("  ".into(), "ws://127.0.0.1:9", Duration::from_secs(1))
            .is_err()
    );
    assert!(
        ExtendedPrivateWebSocket::with_url(
            "key".into(),
            "https://127.0.0.1:9",
            Duration::from_secs(1)
        )
        .is_err()
    );
}
