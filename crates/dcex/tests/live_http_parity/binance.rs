use std::time::Duration;

use dcex::exchange::ValidatedResponse;
use dcex::exchanges::binance::{
    BinanceClient, BinanceFundingRateParams, BinanceFundingWalletParams, BinanceFuturesBasisParams,
    BinanceFuturesPeriodParams, BinanceIncomeHistoryParams, BinanceKlinesParams,
    BinanceLimitParams, BinanceOptionalSymbolParams, BinanceSymbolListParams,
    BinanceUniversalTransferHistoryParams, BinanceWalletBalanceParams,
};

use super::common::{
    require_env, run_cases, run_private_cases, Case, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn binance_public_live_parity() -> dcex::Result<()> {
    let client = BinanceClient::public(Duration::from_secs(20))?;
    run_cases(
        vec![
            Case::new(
                "get_spot_exchange_info",
                &[("product_symbol", BTC_USDT_SPOT)],
            ),
            Case::new(
                "get_spot_orderbook",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new(
                "get_spot_trades",
                &[("product_symbol", BTC_USDT_SPOT), ("limit", "5")],
            ),
            Case::new("get_server_time", &[("market_type", "spot")]),
            Case::new("get_server_time", &[("market_type", "swap")]),
            Case::new("get_futures_exchange_info", &[]),
            Case::new("get_futures_ticker", &[("product_symbol", BTC_USDT_SWAP)]),
            Case::new(
                "get_klines",
                &[("product_symbol", BTC_USDT_SWAP), ("interval", "1m")],
            ),
            Case::new(
                "get_futures_premium_index",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_futures_funding_rate",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_futures_open_interest",
                &[("product_symbol", BTC_USDT_SWAP)],
            ),
            Case::new(
                "get_futures_open_interest_history",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_global_long_short_account_ratio",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_top_long_short_account_ratio",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_top_long_short_position_ratio",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_taker_buy_sell_volume",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
            Case::new(
                "get_futures_basis",
                &[
                    ("product_symbol", BTC_USDT_SWAP),
                    ("contractType", "PERPETUAL"),
                    ("period", "5m"),
                    ("limit", "5"),
                ],
            ),
        ],
        |case| {
            let client = client.clone();
            async move { binance_public_case(&client, case).await }
        },
    )
    .await
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn binance_private_read_live_parity() -> dcex::Result<()> {
    let Some(keys) = require_env(&["BINANCE_API_KEY", "BINANCE_API_SECRET"]) else {
        return Ok(());
    };
    let client = BinanceClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;
    run_private_cases(
        &["BINANCE_API_KEY", "BINANCE_API_SECRET"],
        vec![
            Case::new("get_account_balance", &[("market_type", "spot")]),
            Case::new("get_account_balance", &[("market_type", "swap")]),
            Case::new("get_futures_account_info", &[]),
            Case::new("get_wallet_balance", &[("quoteAsset", "USDT")]),
            Case::new(
                "get_funding_wallet",
                &[("asset", "USDT"), ("needBtcValuation", "true")],
            ),
            Case::new(
                "get_universal_transfer_history",
                &[("type", "FUNDING_MAIN"), ("size", "1")],
            ),
            Case::new("get_income_history", &[]),
        ],
        |case| {
            let client = client.clone();
            async move { binance_private_case(&client, case).await }
        },
    )
    .await
}

async fn binance_public_case(
    client: &BinanceClient,
    case: Case,
) -> dcex::Result<ValidatedResponse> {
    let params = Params(case.params);
    match case.method {
        "get_spot_exchange_info" => {
            client
                .get_spot_exchange_info_with(BinanceSymbolListParams {
                    product_symbol: params.get("product_symbol"),
                    ..Default::default()
                })
                .await
        }
        "get_spot_orderbook" => {
            client
                .get_spot_orderbook_with(
                    params.required("product_symbol")?,
                    BinanceLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
        }
        "get_spot_trades" => {
            client
                .get_spot_trades_with(
                    params.required("product_symbol")?,
                    BinanceLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
        }
        "get_server_time" => {
            client
                .get_server_time(params.get("market_type").unwrap_or("spot"))
                .await
        }
        "get_futures_exchange_info" => client.get_futures_exchange_info().await,
        "get_futures_ticker" => {
            client
                .get_futures_ticker_with(BinanceOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
        }
        "get_klines" => {
            client
                .get_klines_with(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    BinanceKlinesParams {
                        start_time: params.u64("start_time")?,
                        limit: params.u64("limit")?,
                    },
                )
                .await
        }
        "get_futures_premium_index" => {
            client
                .get_futures_premium_index_with(BinanceOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
        }
        "get_futures_funding_rate" => {
            client
                .get_futures_funding_rate_with(BinanceFundingRateParams {
                    product_symbol: params.get("product_symbol"),
                    start_time: params.u64("startTime")?,
                    end_time: params.u64("endTime")?,
                    limit: params.u64("limit")?,
                })
                .await
        }
        "get_futures_open_interest" => {
            client
                .get_futures_open_interest(params.required("product_symbol")?)
                .await
        }
        "get_futures_open_interest_history" => {
            client
                .get_futures_open_interest_history_with(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesPeriodParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
        }
        "get_futures_global_long_short_account_ratio" => {
            client
                .get_futures_global_long_short_account_ratio_with(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesPeriodParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
        }
        "get_futures_top_long_short_account_ratio" => {
            client
                .get_futures_top_long_short_account_ratio_with(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesPeriodParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
        }
        "get_futures_top_long_short_position_ratio" => {
            client
                .get_futures_top_long_short_position_ratio_with(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesPeriodParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
        }
        "get_futures_taker_buy_sell_volume" => {
            client
                .get_futures_taker_buy_sell_volume_with(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesPeriodParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
        }
        "get_futures_basis" => {
            client
                .get_futures_basis_with(
                    params.required("product_symbol")?,
                    params.get("contractType").unwrap_or("PERPETUAL"),
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesBasisParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
        }
        method => Err(dcex::DcexError::InvalidInput(format!(
            "unsupported Binance public test method: {method}",
        ))),
    }
}

async fn binance_private_case(
    client: &BinanceClient,
    case: Case,
) -> dcex::Result<ValidatedResponse> {
    let params = Params(case.params);
    match case.method {
        "get_account_balance" => {
            client
                .get_account_balance(params.get("market_type").unwrap_or("spot"))
                .await
        }
        "get_futures_account_info" => client.get_futures_account_info().await,
        "get_wallet_balance" => {
            client
                .get_wallet_balance_with(BinanceWalletBalanceParams {
                    quote_asset: params.get("quoteAsset"),
                })
                .await
        }
        "get_funding_wallet" => {
            client
                .get_funding_wallet_with(BinanceFundingWalletParams {
                    asset: params.get("asset"),
                    need_btc_valuation: params.get("needBtcValuation"),
                })
                .await
        }
        "get_universal_transfer_history" => {
            client
                .get_universal_transfer_history_with(
                    params.required("type")?,
                    BinanceUniversalTransferHistoryParams {
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                        current: params.u64("current")?,
                        size: params.u64("size")?,
                        from_symbol: params.get("fromSymbol"),
                        to_symbol: params.get("toSymbol"),
                    },
                )
                .await
        }
        "get_income_history" => {
            client
                .get_income_history_with(BinanceIncomeHistoryParams {
                    product_symbol: params.get("product_symbol"),
                    income_type: params.get("incomeType"),
                    start_time: params.u64("startTime")?,
                    end_time: params.u64("endTime")?,
                    page: params.u64("page")?,
                    limit: params.u64("limit")?,
                })
                .await
        }
        method => Err(dcex::DcexError::InvalidInput(format!(
            "unsupported Binance private test method: {method}",
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

    fn u64(&self, key: &str) -> dcex::Result<Option<u64>> {
        self.get(key)
            .map(|value| {
                value.parse::<u64>().map_err(|error| {
                    dcex::DcexError::InvalidInput(format!("invalid {key}: {error}"))
                })
            })
            .transpose()
    }
}
