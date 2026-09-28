use super::helpers::*;

#[tokio::test]
async fn unknown_dispatch_names_are_rejected_without_network() {
    let client = BybitClient::public(5_000, false, Duration::from_secs(1)).expect("client");
    let error = client
        .public_request("get_not_a_bybit_endpoint", Vec::new())
        .await
        .expect_err("public");
    assert!(
        error
            .to_string()
            .contains("unsupported Bybit public method")
    );
    let error = client
        .private_request("get_not_a_bybit_endpoint", Vec::new())
        .await
        .expect_err("private");
    assert!(
        error
            .to_string()
            .contains("unsupported Bybit private method")
    );
}
