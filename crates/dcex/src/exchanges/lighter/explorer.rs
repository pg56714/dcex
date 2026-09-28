//! Public explorer and historical export routes from the official OpenAPI schemas.
use super::{LighterClient, market::auth_header_required, params::LighterParams};
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};
impl LighterClient {
    pub(super) async fn explorer_request(
        &self,
        name: &str,
        p: &LighterParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let mut query = Vec::new();
        let (path, explorer, private) = match name {
            "get_pnl_leaderboard" => {
                p.ensure_allowed(&[
                    "time_window",
                    "sort_by",
                    "sort_dir",
                    "limit",
                    "offset",
                    "search",
                ])?;
                p.required("time_window")?;
                p.optional_one_of("time_window", &["24h", "7d", "30d", "all"])?;
                query.extend(p.query(&["time_window"]));
                p.required("sort_by")?;
                p.optional_one_of("sort_by", &["pnl", "roi", "volume", "account_value"])?;
                query.extend(p.query(&["sort_by"]));
                p.required("sort_dir")?;
                p.optional_one_of("sort_dir", &["asc", "desc"])?;
                query.extend(p.query(&["sort_dir"]));
                p.required("limit")?;
                p.optional_u64_range("limit", 1, 100)?;
                query.extend(p.query(&["limit"]));
                p.required("offset")?;
                p.optional_u64_range("offset", 0, 100000)?;
                query.extend(p.query(&["offset"]));
                query.extend(p.query(&["search"]));
                let path = "/api/v1/pnlLeaderboard".to_string();
                (path, false, false)
            }
            "export_historical_trades" => {
                p.ensure_allowed(&["authorization", "l1_address", "date"])?;
                p.required("l1_address")?;
                query.extend(p.query(&["l1_address"]));
                p.required("date")?;
                query.extend(p.query(&["date"]));
                let path = "/api/v1/export/historicalTrades".to_string();
                (path, false, true)
            }
            "get_explorer_account_logs" => {
                p.ensure_allowed(&["param", "pub_data_type", "limit", "offset"])?;
                p.required("param")?;
                let segment = url::form_urlencoded::byte_serialize(p.required("param")?.as_bytes())
                    .collect::<String>();
                let path = "/accounts/{param}/logs".replace("{param}", &segment);
                if let Some(value) = p.get("pub_data_type") {
                    let values: Vec<String> = serde_json::from_str(value).map_err(|_| {
                        DcexError::InvalidInput("pub_data_type must be a JSON string array".into())
                    })?;
                    for value in values {
                        if ![
                            "Empty",
                            "L1Deposit",
                            "L1CreateMarket",
                            "L1UpdateMarket",
                            "L2CreateSubAccount",
                            "L2CreatePublicPool",
                            "L2UpdatePublicPool",
                            "L2MintShares",
                            "L2UpdateLeverage",
                            "L2UpdateMargin",
                            "L2Transfer",
                            "Withdraw",
                            "Trade",
                            "TradeWithFunding",
                            "LiquidationTrade",
                            "LiquidationTradeWithFunding",
                            "BurnedShares",
                            "ExitPosition",
                            "ExitPositionWithFunding",
                            "Deleverage",
                            "DeleverageWithFunding",
                            "L1RegisterAsset",
                            "L1UpdateAsset",
                            "L1CreateSpotMarket",
                            "L1UpdateSpotMarket",
                            "WithdrawV2",
                            "L1CreateMarketV2",
                            "L1DepositV2",
                            "L1UpdateMarketV2",
                            "L2TransferV2",
                            "L2CreateStakingPool",
                            "L2UpdateStakingPool",
                            "L2StakeAssets",
                            "UnstakeAssets",
                            "L1SetSystemConfig",
                            "ExecutedPendingUnlock",
                            "L2UpdateAccountConfig",
                            "L2UpdateMarketConfig",
                        ]
                        .contains(&value.as_str())
                        {
                            return Err(DcexError::InvalidInput("invalid pub_data_type".into()));
                        }
                        query.push(("pub_data_type".into(), value));
                    }
                }
                p.required("limit")?;
                p.optional_u64_range("limit", 0, 100)?;
                query.extend(p.query(&["limit"]));
                p.required("offset")?;
                query.extend(p.query(&["offset"]));
                (path, true, false)
            }
            "get_explorer_account_positions" => {
                p.ensure_allowed(&["param"])?;
                p.required("param")?;
                let segment = url::form_urlencoded::byte_serialize(p.required("param")?.as_bytes())
                    .collect::<String>();
                let path = "/accounts/{param}/positions".replace("{param}", &segment);
                (path, true, false)
            }
            "get_explorer_account_assets" => {
                p.ensure_allowed(&["param"])?;
                p.required("param")?;
                let segment = url::form_urlencoded::byte_serialize(p.required("param")?.as_bytes())
                    .collect::<String>();
                let path = "/accounts/{param}/assets".replace("{param}", &segment);
                (path, true, false)
            }
            "get_explorer_batches" => {
                p.ensure_allowed(&[])?;
                let path = "/batches".to_string();
                (path, true, false)
            }
            "get_explorer_batch" => {
                p.ensure_allowed(&["batchId"])?;
                p.required("batchId")?;
                p.optional_u64_range("batchId", 0, 18446744073709551615)?;
                let segment =
                    url::form_urlencoded::byte_serialize(p.required("batchId")?.as_bytes())
                        .collect::<String>();
                let path = "/batches/{batchId}".replace("{batchId}", &segment);
                (path, true, false)
            }
            "get_explorer_blocks" => {
                p.ensure_allowed(&[])?;
                let path = "/blocks".to_string();
                (path, true, false)
            }
            "get_explorer_block" => {
                p.ensure_allowed(&["blockId"])?;
                p.required("blockId")?;
                p.optional_u64_range("blockId", 0, 18446744073709551615)?;
                let segment =
                    url::form_urlencoded::byte_serialize(p.required("blockId")?.as_bytes())
                        .collect::<String>();
                let path = "/blocks/{blockId}".replace("{blockId}", &segment);
                (path, true, false)
            }
            "get_explorer_log" => {
                p.ensure_allowed(&["hash"])?;
                p.required("hash")?;
                let segment = url::form_urlencoded::byte_serialize(p.required("hash")?.as_bytes())
                    .collect::<String>();
                let path = "/logs/{hash}".replace("{hash}", &segment);
                (path, true, false)
            }
            "get_explorer_markets" => {
                p.ensure_allowed(&[])?;
                let path = "/markets".to_string();
                (path, true, false)
            }
            "get_explorer_market_logs" => {
                p.ensure_allowed(&["symbol", "limit", "offset"])?;
                p.required("symbol")?;
                let segment =
                    url::form_urlencoded::byte_serialize(p.required("symbol")?.as_bytes())
                        .collect::<String>();
                let path = "/markets/{symbol}/logs".replace("{symbol}", &segment);
                p.optional_u64_range("limit", 0, 100)?;
                query.extend(p.query(&["limit"]));
                query.extend(p.query(&["offset"]));
                (path, true, false)
            }
            "search_explorer" => {
                p.ensure_allowed(&["q"])?;
                p.required("q")?;
                query.extend(p.query(&["q"]));
                let path = "/search".to_string();
                (path, true, false)
            }
            "get_explorer_transaction_stats" => {
                p.ensure_allowed(&["aggregation_period"])?;
                p.required("aggregation_period")?;
                query.extend(p.query(&["aggregation_period"]));
                let path = "/stats/tx".to_string();
                (path, true, false)
            }
            "get_explorer_total" => {
                p.ensure_allowed(&[])?;
                let path = "/total".to_string();
                (path, true, false)
            }
            _ => return Ok(None),
        };
        if public == private {
            return Ok(None);
        }
        let headers = if private {
            auth_header_required(self, p)?
        } else {
            Default::default()
        };
        let mut client = self.clone();
        if explorer {
            client.base_url = self.explorer_base_url.clone().ok_or_else(|| crate::DcexError::InvalidInput("explorer_base_url must be configured for this network; no documented default is available".into()))?;
        }
        client.get_path(&path, query, headers).await.map(Some)
    }
}
