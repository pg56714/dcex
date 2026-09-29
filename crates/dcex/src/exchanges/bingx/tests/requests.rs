use super::helpers::*;

#[test]
fn new_swap_market_routes_use_official_paths() {
    let cases = [
        (
            "get_swap_premium_index",
            "/openApi/swap/v2/quote/premiumIndex",
        ),
        (
            "get_swap_funding_rate",
            "/openApi/swap/v2/quote/fundingRate",
        ),
        ("get_swap_book_ticker", "/openApi/swap/v2/quote/bookTicker"),
        ("get_swap_trading_rules", "/openApi/swap/v1/tradingRules"),
    ];
    for (method, path) in cases {
        let (url, server) = recording_server();
        let client =
            BingxClient::with_base_url(None, None, Duration::from_secs(10), url).expect("client");
        block_on(async move {
            client
                .public_request(
                    method,
                    vec![("product_symbol".into(), "BTC-USDT-SWAP".into())],
                )
                .await
        })
        .expect("request");
        let line = server.join().expect("server");
        assert!(
            line.starts_with(&format!("GET {path}?symbol=BTC-USDT")),
            "{line}"
        );
        if method == "get_swap_trading_rules" {
            assert!(line.contains("&timestamp="), "{line}");
        }
    }
}
