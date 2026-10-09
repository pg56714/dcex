pub(in crate::exchanges::kraken) use crate::Result;
pub(in crate::exchanges::kraken) use crate::exchange::ValidatedResponse;

pub(in crate::exchanges::kraken) use super::client::{KrakenAuth, KrakenClient};
pub(in crate::exchanges::kraken) use super::endpoints::*;
pub(in crate::exchanges::kraken) use super::params::{KrakenParams, push_optional};

impl KrakenClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &KrakenParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_spot_account_balance" => {
                params.ensure_allowed(&["rebase_multiplier"])?;
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_BALANCE,
                    params.only(&["rebase_multiplier"]),
                )
                .await
            }
            "get_spot_trade_balance" => {
                params.ensure_allowed(&["asset", "rebase_multiplier"])?;
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_TRADE_BALANCE,
                    params.only(&["asset", "rebase_multiplier"]),
                )
                .await
            }
            "get_spot_open_positions" => {
                params.ensure_allowed(&[
                    "txid",
                    "docalcs",
                    "consolidation",
                    "rebase_multiplier",
                ])?;
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_OPEN_POSITIONS,
                    params.only(&["txid", "docalcs", "consolidation", "rebase_multiplier"]),
                )
                .await
            }
            "get_spot_ledgers" => {
                params.ensure_allowed(&[
                    "asset",
                    "aclass",
                    "start",
                    "end",
                    "ofs",
                    "without_count",
                    "rebase_multiplier",
                    "type",
                ])?;
                let mut query = params.only(&[
                    "asset",
                    "aclass",
                    "start",
                    "end",
                    "ofs",
                    "without_count",
                    "rebase_multiplier",
                ]);
                push_optional(&mut query, "type", params.get("type"));
                self.private_post(KrakenAuth::Spot, SPOT_LEDGERS, query)
                    .await
            }
            "get_spot_trade_volume" => {
                params.ensure_allowed(&[
                    "pair",
                    "fee_schedule",
                    "rebase_multiplier",
                    "fee-info",
                ])?;
                let mut query = params.only(&["pair", "fee_schedule", "rebase_multiplier"]);
                push_optional(&mut query, "fee-info", params.get("fee-info"));
                self.private_post(KrakenAuth::Spot, SPOT_TRADE_VOLUME, query)
                    .await
            }
            "wallet_transfer_to_futures" => {
                self.dispatch_wallet_transfer_to_futures(method_name, params)
                    .await
            }
            "get_futures_accounts" => {
                params.ensure_allowed(&[])?;
                self.private_get(KrakenAuth::Futures, FUTURES_ACCOUNTS, Vec::new())
                    .await
            }
            "get_futures_open_positions" => {
                params.ensure_allowed(&[])?;
                self.private_get(KrakenAuth::Futures, FUTURES_OPEN_POSITIONS, Vec::new())
                    .await
            }
            "get_futures_fills" => {
                params.ensure_allowed(&["lastFillTime"])?;
                self.private_get(
                    KrakenAuth::Futures,
                    FUTURES_FILLS,
                    params.only(&["lastFillTime"]),
                )
                .await
            }
            "futures_wallet_transfer" => {
                self.dispatch_futures_wallet_transfer(method_name, params)
                    .await
            }
            "withdraw_futures_to_spot_wallet" => {
                self.dispatch_withdraw_futures_to_spot_wallet(method_name, params)
                    .await
            }
            _ => return Ok(None),
        };

        Ok(Some(result?))
    }
}

pub(in crate::exchanges::kraken) fn push_lowercase(
    query: &mut Vec<(String, String)>,
    key: &str,
    value: Option<&str>,
) {
    if let Some(value) = value {
        query.push((key.to_string(), value.to_lowercase()));
    }
}
