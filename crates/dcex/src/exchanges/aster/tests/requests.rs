use super::helpers::*;

#[test]
fn raw_auto_routes_spot_paths_to_spot_base_url() {
    let (spot_base_url, handle) = recording_server();
    let client = AsterClient::with_base_urls(
        None,
        None,
        None,
        Duration::from_secs(2),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    let response = client
        .request_raw_auto_blocking(HttpMethod::Get, "/api/v3/time", Vec::new(), false)
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /api/v3/time HTTP/1.1".to_string())
    );
}

#[test]
fn raw_auto_routes_futures_paths_to_futures_base_url() {
    let (futures_base_url, handle) = recording_server();
    let client = AsterClient::with_base_urls(
        None,
        None,
        None,
        Duration::from_secs(2),
        "http://127.0.0.1:9".to_string(),
        futures_base_url,
    )
    .expect("client");

    let response = client
        .request_raw_auto_blocking(HttpMethod::Get, "/fapi/v3/time", Vec::new(), false)
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /fapi/v3/time HTTP/1.1".to_string())
    );
}
