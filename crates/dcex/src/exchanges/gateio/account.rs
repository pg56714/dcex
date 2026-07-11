use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::GateioClient;
use super::endpoints::*;
use super::params::GateioParams;

impl GateioClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &GateioParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_spot_fee_rates" => {
                let mut query = Vec::new();
                self.push_optional_currency_pair(&mut query, params)?;
                self.private_get(SPOT_FEE, query).await
            }
            "get_futures_fee_rates" => {
                let path = fill_settle(FUTURES_FEE, params.settle());
                let mut query = Vec::new();
                self.push_optional_contract(&mut query, params)?;
                self.private_get(&path, query).await
            }

            "get_total_balance" => {
                self.private_get(WALLET_TOTAL_BALANCE, params.only(&["currency"]))
                    .await
            }
            "wallet_transfer" => {
                let body = Value::Object(params.body(
                    &[
                        "currency",
                        "from",
                        "to",
                        "amount",
                        "currency_pair",
                        "settle",
                    ],
                    &[],
                    &[],
                ));
                self.private_post_json(WALLET_TRANSFERS, body).await
            }
            "get_unified_accounts" => {
                self.private_get(UNIFIED_ACCOUNTS, params.only(&["currency", "sub_uid"]))
                    .await
            }
            "get_futures_account" => {
                let path = fill_settle(FUTURES_ACCOUNT, params.settle());
                self.private_get(&path, Vec::new()).await
            }
            "get_futures_account_book" => {
                let path = fill_settle(FUTURES_ACCOUNT_BOOK, params.settle());
                let mut query = params.only_renamed(&[
                    ("limit", "limit"),
                    ("offset", "offset"),
                    ("from_time", "from"),
                    ("from_timestamp", "from"),
                    ("from", "from"),
                    ("to_time", "to"),
                    ("to_timestamp", "to"),
                    ("to", "to"),
                    ("change_type", "type"),
                    ("type", "type"),
                    ("type_", "type"),
                ]);
                self.push_optional_contract(&mut query, params)?;
                self.private_get(&path, query).await
            }
            "get_delivery_account" => {
                let path = fill_settle(DELIVERY_ACCOUNT, params.settle());
                self.private_get(&path, Vec::new()).await
            }
            "get_delivery_account_book" => {
                let path = fill_settle(DELIVERY_ACCOUNT_BOOK, params.settle());
                let query = params.only_renamed(&[
                    ("limit", "limit"),
                    ("offset", "offset"),
                    ("from_time", "from"),
                    ("from_timestamp", "from"),
                    ("from", "from"),
                    ("to_time", "to"),
                    ("to_timestamp", "to"),
                    ("to", "to"),
                    ("change_type", "type"),
                    ("type", "type"),
                    ("type_", "type"),
                ]);
                self.private_get(&path, query).await
            }
            "get_spot_account" => {
                let mut query = Vec::new();
                if let Some(currency) = params.get("currency").or_else(|| params.get("ccy")) {
                    query.push(("currency".to_string(), currency.to_string()));
                }
                self.private_get(SPOT_ACCOUNTS, query).await
            }
            "get_spot_account_book" => {
                let mut query = params.only_renamed(&[
                    ("ccy", "currency"),
                    ("currency", "currency"),
                    ("from_timestamp", "from"),
                    ("from", "from"),
                    ("to_timestamp", "to"),
                    ("to", "to"),
                    ("page", "page"),
                    ("limit", "limit"),
                    ("code", "code"),
                ]);
                if !query.iter().any(|(key, _)| key == "code") {
                    if let Some(kind) = params.get("type_").or_else(|| params.get("type")) {
                        query.push(("type".to_string(), kind.to_string()));
                    }
                }
                self.private_get(SPOT_ACCOUNT_BOOK, query).await
            }
            "get_spot_fee" => {
                let mut query = Vec::new();
                self.push_optional_currency_pair(&mut query, params)?;
                self.private_get(SPOT_FEE, query).await
            }
            "get_spot_batch_fee" => {
                let currency_pairs = if let Some(currency_pairs) = params.get("currency_pairs") {
                    currency_pairs.to_string()
                } else {
                    self.currency_pairs_from_products(params.required("product_symbols")?)?
                };
                self.private_get(
                    SPOT_BATCH_FEE,
                    vec![("currency_pairs".to_string(), currency_pairs)],
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
