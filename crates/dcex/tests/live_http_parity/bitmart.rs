use std::time::Duration;

use dcex::exchange::ValidatedResponse;
use dcex::exchanges::bitmart::{
    BitmartClient, BitmartContractsDetailsParams, BitmartFundingRateHistoryParams,
    BitmartSpotKlineParams,
};

use super::common::{
    live_http_enabled, now_ms, require_env, run_cases, Case, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bitmart_public_live_parity() -> dcex::Result<()> {
    let client = BitmartClient::public(Duration::from_secs(20))?;
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
            async move { bitmart_public_case(&client, case).await }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
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
        match request_case!(
            client,
            case,
            [
                get_account_balance => get_account_balance_with,
                get_account_currencies => get_account_currencies_with,
                get_contract_assets => get_contract_assets_with,
                get_contract_open_order => get_contract_open_order_with,
                get_contract_order_history => get_contract_order_history_with,
                get_contract_position => get_contract_position_with,
                get_contract_trade => get_contract_trade_with,
                get_contract_transaction_history => get_contract_transaction_history_with,
                get_contract_transfer_list => get_contract_transfer_list_with,
                get_deposit_address => get_deposit_address_with,
                get_spot_account_orders => get_spot_account_orders_with,
                get_spot_account_trade_list => get_spot_account_trade_list_with,
                get_spot_open_orders => get_spot_open_orders_with,
                get_spot_wallet => get_spot_wallet_with,
            ]
        ) {
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

async fn bitmart_public_case(
    client: &BitmartClient,
    case: Case,
) -> dcex::Result<ValidatedResponse> {
    let params = Params(case.params);
    match case.method {
        "get_spot_currencies" => client.get_spot_currencies().await,
        "get_trading_pairs" => client.get_trading_pairs().await,
        "get_trading_pairs_details" => client.get_trading_pairs_details().await,
        "get_ticker_of_all_pairs" => client.get_ticker_of_all_pairs().await,
        "get_ticker_of_a_pair" => {
            client
                .get_ticker_of_a_pair(params.required("product_symbol")?)
                .await
        }
        "get_spot_kline" => {
            client
                .get_spot_kline_with(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    BitmartSpotKlineParams {
                        before: params.get("before"),
                        after: params.get("after"),
                        limit: params.get("limit"),
                    },
                )
                .await
        }
        "get_contracts_details" => {
            client
                .get_contracts_details_with(BitmartContractsDetailsParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
        }
        "get_depth" => client.get_depth(params.required("product_symbol")?).await,
        "get_contract_kline" => {
            client
                .get_contract_kline(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.required("start_time")?,
                    params.required("end_time")?,
                )
                .await
        }
        "get_open_interest" => {
            client
                .get_open_interest(params.required("product_symbol")?)
                .await
        }
        "get_mark_price_kline" => {
            client
                .get_mark_price_kline(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.required("start_time")?,
                    params.required("end_time")?,
                )
                .await
        }
        "get_leverage_bracket" => {
            client
                .get_leverage_bracket(params.required("product_symbol")?)
                .await
        }
        "get_current_funding_rate" => {
            client
                .get_current_funding_rate(params.required("product_symbol")?)
                .await
        }
        "get_funding_rate_history" => {
            client
                .get_funding_rate_history_with(
                    params.required("product_symbol")?,
                    BitmartFundingRateHistoryParams {
                        limit: params.get("limit"),
                    },
                )
                .await
        }
        method => Err(dcex::DcexError::InvalidInput(format!(
            "unsupported BitMart public test method: {method}",
        ))),
    }
}

struct Params(Vec<(String, String)>);

impl Params {
    fn get(&self, key: &str) -> Option<&str> {
        self.0
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    fn required(&self, key: &str) -> dcex::Result<&str> {
        self.get(key)
            .ok_or_else(|| dcex::DcexError::InvalidInput(format!("missing {key}")))
    }
}
