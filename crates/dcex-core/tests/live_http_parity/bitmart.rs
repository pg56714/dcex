use std::time::Duration;

use dcex::exchanges::bitmart::BitmartClient;

use super::common::{
    live_http_enabled, now_ms, require_env, run_cases, Case, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
async fn bitmart_public_live_parity() -> dcex::Result<()> {
    let client = BitmartClient::new(None, None, None, Duration::from_secs(20))?;
    let end_time = (now_ms() / 1000).to_string();
    let start_time = ((now_ms() / 1000) - 24 * 60 * 60).to_string();
    run_cases(
        vec![
            Case::new("get_spot_currencies", &[]),
            Case::new("get_trading_pairs", &[]),
            Case::new("get_trading_pairs_details", &[]),
            Case::new("get_ticker_of_all_pairs", &[]),
            Case::new("get_ticker_of_a_pair", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_spot_kline",
                &[("product_symbol", BTC_USDT_SPOT), ("interval", "5m")],
            ),
            Case::new(
                "get_contracts_details",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new("get_depth", &[("product_symbol", BTC_USDT_SWAP)]),
            Case {
                method: "get_contract_kline",
                params: vec![
                    ("product_symbol".to_string(), BTC_USDT_SWAP.to_string()),
                    ("interval".to_string(), "5m".to_string()),
                    ("start_time".to_string(), start_time.clone()),
                    ("end_time".to_string(), end_time.clone()),
                ],
            },
            Case::new("get_open_interest", &[("product_symbol", BTC_USDT_SWAP)]),
            Case {
                method: "get_mark_price_kline",
                params: vec![
                    ("product_symbol".to_string(), BTC_USDT_SWAP.to_string()),
                    ("interval".to_string(), "5m".to_string()),
                    ("start_time".to_string(), start_time),
                    ("end_time".to_string(), end_time),
                ],
            },
            Case::new("get_leverage_bracket", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new(
                "get_current_funding_rate",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_funding_rate_history",
                &[("product_symbol", BTC_USDT_SWAP), ("limit", "10")],
            ),
        ],
        |case| {
            let client = client.clone();
            async move { client.public_request(case.method, case.params).await }
        },
    )
    .await
}

#[tokio::test]
async fn bitmart_private_read_live_parity() -> dcex::Result<()> {
    if !live_http_enabled() {
        eprintln!("skipping live private parity test; set RUN_LIVE_HTTP_TESTS=1");
        return Ok(());
    }
    let Some(keys) = require_env(&["BITMART_API_KEY", "BITMART_API_SECRET", "BITMART_MEMO"]) else {
        return Ok(());
    };
    let client = BitmartClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;
    let cases = vec![
        Case::new("get_account_balance", &[]),
        Case::new("get_account_currencies", &[]),
        Case::new("get_spot_wallet", &[]),
        Case::new("get_deposit_address", &[("currency", "BTC")]),
        Case::new("get_contract_assets", &[]),
        Case::new(
            "get_spot_open_orders",
            &[("product_symbol", BTC_USDT_SPOT), ("limit", "20")],
        ),
        Case::new(
            "get_spot_account_orders",
            &[("product_symbol", BTC_USDT_SPOT), ("limit", "20")],
        ),
        Case::new(
            "get_spot_account_trade_list",
            &[("product_symbol", BTC_USDT_SPOT), ("limit", "20")],
        ),
        Case::new(
            "get_contract_order_history",
            &[("product_symbol", BTC_USDT_SWAP)],
        ),
        Case::new(
            "get_contract_open_order",
            &[("product_symbol", BTC_USDT_SWAP), ("limit", "20")],
        ),
        Case::new(
            "get_contract_position",
            &[("product_symbol", BTC_USDT_SWAP)],
        ),
        Case::new("get_contract_trade", &[("product_symbol", BTC_USDT_SWAP)]),
        Case::new(
            "get_contract_transaction_history",
            &[("product_symbol", BTC_USDT_SWAP), ("page_size", "20")],
        ),
        Case::new(
            "get_contract_transfer_list",
            &[("page", "1"), ("limit", "20")],
        ),
    ];
    for case in cases {
        let method = case.method;
        match client.private_request(method, case.params).await {
            Ok(response) => {
                assert!((200..300).contains(&response.status), "{response:?}");
                assert!(!response.data.is_null(), "{response:?}");
                eprintln!("ok {method}");
            }
            Err(error) if is_bitmart_account_restriction(&error) => {
                eprintln!("skipping BitMart private read parity: {error}");
                return Ok(());
            }
            Err(error) => return Err(error),
        }
    }
    Ok(())
}

fn is_bitmart_account_restriction(error: &dcex::DcexError) -> bool {
    let message = error.to_string();
    message.contains("33136")
        || message.contains("60052")
        || message.to_lowercase().contains("personal verification")
}
