use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::{KrakenAuth, KrakenClient};
use super::endpoints::*;
use super::params::{push_optional, KrakenParams};

impl KrakenClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &KrakenParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_spot_account_balance" => {
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_BALANCE,
                    params.only(&["rebase_multiplier"]),
                )
                .await
            }
            "get_spot_trade_balance" => {
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_TRADE_BALANCE,
                    params.only(&["asset"]),
                )
                .await
            }
            "get_spot_open_positions" => {
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_OPEN_POSITIONS,
                    params.only(&["txid", "docalcs", "consolidation", "rebase_multiplier"]),
                )
                .await
            }
            "get_spot_ledgers" => {
                let mut query =
                    params.only(&["asset", "aclass", "start", "end", "ofs", "without_count"]);
                push_optional(
                    &mut query,
                    "type",
                    params.get("type").or_else(|| params.get("type_")),
                );
                self.private_post(KrakenAuth::Spot, SPOT_LEDGERS, query)
                    .await
            }
            "get_spot_trade_volume" => {
                let mut query = params.only(&["pair"]);
                push_optional(
                    &mut query,
                    "fee-info",
                    params.get("fee-info").or_else(|| params.get("fee_info")),
                );
                self.private_post(KrakenAuth::Spot, SPOT_TRADE_VOLUME, query)
                    .await
            }
            "wallet_transfer_to_futures" => {
                let mut query = params.only(&["asset", "to", "amount"]);
                push_optional(
                    &mut query,
                    "from",
                    params.get("from").or_else(|| params.get("from_")),
                );
                self.private_post(KrakenAuth::Spot, SPOT_WALLET_TRANSFER, query)
                    .await
            }
            "get_futures_accounts" => {
                self.private_get(KrakenAuth::Futures, FUTURES_ACCOUNTS, Vec::new())
                    .await
            }
            "get_futures_open_positions" => {
                self.private_get(KrakenAuth::Futures, FUTURES_OPEN_POSITIONS, Vec::new())
                    .await
            }
            "get_futures_fills" => {
                self.private_get(
                    KrakenAuth::Futures,
                    FUTURES_FILLS,
                    params.only(&["lastFillTime"]),
                )
                .await
            }
            "futures_wallet_transfer" => {
                let mut query = params.only(&["amount", "fromAccount", "toAccount"]);
                push_lowercase(&mut query, "unit", params.get("unit"));
                self.private_post(KrakenAuth::Futures, FUTURES_TRANSFER, query)
                    .await
            }
            "withdraw_futures_to_spot_wallet" => {
                let mut query = params.only(&["amount", "sourceWallet"]);
                push_lowercase(&mut query, "currency", params.get("currency"));
                self.private_post(KrakenAuth::Futures, FUTURES_WITHDRAWAL, query)
                    .await
            }
            _ => return Ok(None),
        };

        Ok(Some(result?))
    }
}

fn push_lowercase(query: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        query.push((key.to_string(), value.to_lowercase()));
    }
}
