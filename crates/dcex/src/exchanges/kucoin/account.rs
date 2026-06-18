use serde_json::{Map, Value};

use crate::exchange::unix_timestamp_ms;
use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::{KucoinClient, KucoinMarket};
use super::endpoints::*;
use super::params::{insert_optional_string, insert_required_string, KucoinParams};

impl KucoinClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &KucoinParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_account_balance" => {
                self.private_get(
                    KucoinMarket::Spot,
                    SPOT_ACCOUNT_BALANCE,
                    params.only(&["currency", "type"]),
                )
                .await
            }
            "get_transfer_quotas" => {
                let mut query = Vec::new();
                query.push((
                    "currency".to_string(),
                    params.required("currency")?.to_string(),
                ));
                query.push((
                    "type".to_string(),
                    params.required_any(&["account_type", "type"])?.to_string(),
                ));
                if let Some(tag) = params.get("tag") {
                    query.push(("tag".to_string(), tag.to_string()));
                }
                self.private_get(KucoinMarket::Spot, SPOT_TRANSFER_QUOTAS, query)
                    .await
            }
            "flex_transfer" => {
                let mut body = Map::new();
                let client_oid = params
                    .get("clientOid")
                    .map(str::to_string)
                    .unwrap_or_else(|| {
                        let timestamp = unix_timestamp_ms().unwrap_or_default();
                        format!("dcex-{timestamp}")
                    });
                insert_required_string(&mut body, "clientOid", &client_oid);
                insert_required_string(
                    &mut body,
                    "type",
                    params.get("transfer_type").unwrap_or("INTERNAL"),
                );
                insert_required_string(&mut body, "currency", params.required("currency")?);
                insert_required_string(&mut body, "amount", params.required("amount")?);
                insert_required_string(
                    &mut body,
                    "fromAccountType",
                    params.required("fromAccountType")?,
                );
                insert_required_string(
                    &mut body,
                    "toAccountType",
                    params.required("toAccountType")?,
                );
                insert_optional_string(&mut body, "fromUserId", params.get("fromUserId"));
                insert_optional_string(&mut body, "toUserId", params.get("toUserId"));
                self.private_post(KucoinMarket::Spot, SPOT_FLEX_TRANSFER, Value::Object(body))
                    .await
            }
            "get_futures_account" => {
                self.private_get(
                    KucoinMarket::Futures,
                    FUTURES_ACCOUNT_OVERVIEW,
                    params.only(&["currency"]),
                )
                .await
            }
            "get_futures_positions" => {
                self.private_get(
                    KucoinMarket::Futures,
                    FUTURES_POSITIONS,
                    params.only(&["currency"]),
                )
                .await
            }
            "get_futures_position" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_POSITION, query)
                    .await
            }
            "get_futures_position_mode" => {
                self.private_get(KucoinMarket::Futures, FUTURES_POSITION_MODE, Vec::new())
                    .await
            }
            "get_futures_cross_margin_leverage" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_CROSS_MARGIN_LEVERAGE, query)
                    .await
            }
            "modify_futures_cross_margin_leverage" => {
                let mut body = Map::new();
                body.insert(
                    "symbol".to_string(),
                    Value::String(self.exchange_symbol(
                        params.required_any(&["product_symbol", "symbol"])?,
                        true,
                    )?),
                );
                insert_required_string(&mut body, "leverage", params.required("leverage")?);
                self.private_post(
                    KucoinMarket::Futures,
                    FUTURES_MODIFY_CROSS_MARGIN_LEVERAGE,
                    Value::Object(body),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
