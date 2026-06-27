use std::time::Duration;

use dcex::exchanges::bitget::BitgetClient;

use super::common::{
    is_bitget_unified_account_error, live_http_enabled, now_ms, require_env, run_cases, Case,
    BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bitget_public_live_parity() -> dcex::Result<()> {
    let client = BitgetClient::public(Duration::from_secs(20))?;
    let end_time = now_ms().to_string();
    let start_time = (now_ms() - 10 * 60 * 1000).to_string();
    run_cases(
        vec![
            Case::new("get_spot_coins", &[("coin", "USDT")]),
            Case::new("get_spot_symbols", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new("get_spot_tickers", &[("product_symbol", BTC_USDT_SPOT)]),
            Case::new(
                "get_spot_orderbook",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new(
                "get_spot_kline",
                &[
                    ("product_symbol", BTC_USDT_SPOT),
                    ("granularity", "1min"),
                    ("limit", "5"),
                ],
            ),
            Case {
                method: "get_spot_history_kline",
                params: vec![
                    ("product_symbol".to_string(), BTC_USDT_SPOT.to_string()),
                    ("granularity".to_string(), "1min".to_string()),
                    ("startTime".to_string(), start_time),
                    ("endTime".to_string(), end_time),
                    ("limit".to_string(), "5".to_string()),
                ],
            },
            Case::new(
                "get_spot_recent_trades",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new(
                "get_spot_market_trades",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new(
                "get_futures_contracts",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("productType", "USDT-FUTURES"),
                ],
            ),
            Case::new(
                "get_futures_ticker",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("productType", "USDT-FUTURES"),
                ],
            ),
            Case::new("get_futures_tickers", &[("productType", "USDT-FUTURES")]),
            Case::new(
                "get_futures_orderbook",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("productType", "USDT-FUTURES"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_kline",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("productType", "USDT-FUTURES"),
                    ("granularity", "1m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_history_kline",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("productType", "USDT-FUTURES"),
                    ("granularity", "1m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_recent_trades",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("productType", "USDT-FUTURES"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_current_funding_rate",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("productType", "USDT-FUTURES"),
                ],
            ),
            Case::new(
                "get_futures_history_funding_rate",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("productType", "USDT-FUTURES"),
                    ("pageSize", "5"),
                ],
            ),
            Case::new(
                "get_futures_open_interest",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("productType", "USDT-FUTURES"),
                ],
            ),
        ],
        |case| {
            let client = client.clone();
            async move {
                request_case!(
                    client,
                    case,
                    [
                        get_futures_contracts,
                        get_futures_current_funding_rate,
                        get_futures_history_funding_rate,
                        get_futures_history_kline,
                        get_futures_kline,
                        get_futures_open_interest,
                        get_futures_orderbook,
                        get_futures_recent_trades,
                        get_futures_ticker,
                        get_futures_tickers,
                        get_spot_coins,
                        get_spot_history_kline,
                        get_spot_kline,
                        get_spot_market_trades,
                        get_spot_orderbook,
                        get_spot_recent_trades,
                        get_spot_symbols,
                        get_spot_tickers,
                    ]
                )
            }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bitget_private_read_live_parity() -> dcex::Result<()> {
    if !live_http_enabled() {
        eprintln!("skipping live private parity test; set RUN_LIVE_HTTP_TESTS=1");
        return Ok(());
    }
    let Some(keys) = require_env(&["BITGET_API_KEY", "BITGET_API_SECRET", "BITGET_PASSPHRASE"])
    else {
        return Ok(());
    };
    let client = BitgetClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;
    let cases = vec![
        Case::new("get_all_account_balance", &[]),
        Case::new("get_funding_assets", &[("coin", "USDT")]),
        Case::new("get_spot_account_info", &[]),
        Case::new("get_spot_account_assets", &[("coin", "USDT")]),
        Case::new(
            "get_spot_account_bills",
            &[("coin", "USDT"), ("limit", "20")],
        ),
        Case::new(
            "get_transferable_coins",
            &[("fromType", "spot"), ("toType", "usdt_futures")],
        ),
        Case::new("get_transfer_records", &[("coin", "USDT"), ("limit", "20")]),
        Case::new("get_deposit_records", &[("coin", "USDT"), ("limit", "20")]),
        Case::new("get_futures_accounts", &[]),
        Case::new("get_futures_account", &[("product_symbol", BTC_USDT_SWAP)]),
        Case::new("get_futures_account_bills", &[("limit", "20")]),
        Case::new("get_futures_positions", &[]),
        Case::new("get_futures_position", &[("product_symbol", BTC_USDT_SWAP)]),
        Case::new(
            "get_spot_open_orders",
            &[("product_symbol", BTC_USDT_SPOT), ("limit", "20")],
        ),
        Case::new(
            "get_spot_history_orders",
            &[("product_symbol", BTC_USDT_SPOT), ("limit", "20")],
        ),
        Case::new(
            "get_spot_fills",
            &[("product_symbol", BTC_USDT_SPOT), ("limit", "20")],
        ),
        Case::new(
            "get_futures_open_orders",
            &[("product_symbol", BTC_USDT_SWAP), ("limit", "20")],
        ),
        Case::new(
            "get_futures_history_orders",
            &[("product_symbol", BTC_USDT_SWAP), ("limit", "20")],
        ),
        Case::new(
            "get_futures_fills",
            &[("product_symbol", BTC_USDT_SWAP), ("limit", "20")],
        ),
    ];
    for case in cases {
        let method = case.method;
        match request_case!(
            client,
            case,
            [
                get_all_account_balance,
                get_deposit_records,
                get_funding_assets,
                get_futures_account,
                get_futures_account_bills,
                get_futures_accounts,
                get_futures_fills,
                get_futures_history_orders,
                get_futures_open_orders,
                get_futures_position,
                get_futures_positions,
                get_spot_account_assets,
                get_spot_account_bills,
                get_spot_account_info,
                get_spot_fills,
                get_spot_history_orders,
                get_spot_open_orders,
                get_transfer_records,
                get_transferable_coins,
            ]
        ) {
            Ok(response) => {
                assert!((200..300).contains(&response.status), "{response:?}");
                assert!(!response.data.is_null(), "{response:?}");
                eprintln!("ok {method}");
            }
            Err(error) if is_bitget_unified_account_error(&error) => {
                eprintln!("skipping Bitget classic private read parity: {error}");
                return Ok(());
            }
            Err(error) => return Err(error),
        }
    }
    Ok(())
}
