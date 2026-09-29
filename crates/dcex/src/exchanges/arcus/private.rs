use super::client::ArcusClient;
use crate::Result;
use crate::exchange::ValidatedResponse;

impl ArcusClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        crate::exchanges::input_contracts::pairs("arcus", method_name, &params)?;
        if matches!(
            method_name,
            "create_withdrawal" | "create_withdrawal_signed"
        ) {
            return self.withdrawal_schema_request(method_name, params).await;
        }
        if super::schema_requests::field_schemas::handles(method_name, false) {
            return self.field_schema_request(method_name, params).await;
        }
        if super::metadata::handles(method_name, false) {
            return self.metadata_request(method_name, params).await;
        }
        if matches!(
            method_name,
            "create_api_key_signed" | "revoke_api_key_signed"
        ) {
            return self.api_keys_request(method_name, params).await;
        }
        if method_name == "submit_internal_transfer" {
            return self.submit_internal_transfer_request(params).await;
        }
        let request = self.build_private_request(method_name, params).await?;
        self.execute(request).await
    }
}

mod spot {
    use super::super::client::{
        ArcusSpotClient,
        spot::{ensure_allowed, required},
    };
    use crate::exchange::ValidatedResponse;
    use crate::{DcexError, Result};
    use std::collections::BTreeMap;

    impl ArcusSpotClient {
        pub async fn private_request(
            &self,
            method_name: &str,
            params: Vec<(String, String)>,
        ) -> Result<ValidatedResponse> {
            crate::exchanges::input_contracts::pairs("arcus", method_name, &params)?;
            if method_name != "submit_signed_quote" {
                return Err(DcexError::InvalidInput(format!(
                    "unknown Arcus spot private method: {method_name}"
                )));
            }
            let values: BTreeMap<_, _> = params.into_iter().collect();
            ensure_allowed(&values, &["signed_quote_json"])?;
            let signed_quote = serde_json::from_str(required(&values, "signed_quote_json")?)
                .map_err(|error| {
                    DcexError::InvalidInput(format!("invalid signed quote JSON: {error}"))
                })?;
            self.submit_signed_quote(signed_quote).await
        }
    }
}

mod legacy {
    use crate::exchanges::arcus::trade::*;
    impl ArcusClient {
        pub(in crate::exchanges::arcus) async fn legacy_private_request(
            &self,
            method_name: &str,
            params: Vec<(String, String)>,
        ) -> Result<HttpRequest> {
            let address = self.address.as_deref().ok_or_else(|| {
                DcexError::InvalidInput("Arcus wallet address is required for trading".into())
            })?;
            let key = self.signing_key.as_ref().ok_or_else(|| {
                DcexError::InvalidInput("Arcus API signing key is required for trading".into())
            })?;
            let values: BTreeMap<_, _> = params.into_iter().collect();
            let mut body: BTreeMap<String, Value> = BTreeMap::new();
            body.insert("address".into(), json!(address));
            body.insert("accountIndex".into(), json!(self.account_index));
            let (action, path) = match method_name {
                "cancel_all_orders" => {
                    if let Some(market) = values.get("product_symbol") {
                        let info = self.market_info(market).await?;
                        let market_id = info["marketId"]
                            .as_u64()
                            .ok_or_else(|| DcexError::Decode("Arcus marketId is missing".into()))?;
                        body.insert("marketId".into(), json!(market_id));
                    }
                    if let Some(valid_until) = values.get("valid_until") {
                        let millis = valid_until.parse::<u64>().map_err(|_| {
                            DcexError::InvalidInput("invalid Arcus valid_until epoch ms".into())
                        })?;
                        body.insert("validUntil".into(), json!(millis));
                    }
                    if values
                        .keys()
                        .any(|key| key != "product_symbol" && key != "valid_until")
                    {
                        return Err(DcexError::InvalidInput(
                            "unknown Arcus cancel_all_orders parameter".into(),
                        ));
                    }
                    ("cancelAllOrders", "/v1/cancelAllOrders")
                }
                "schedule_cancel" | "disarm_scheduled_cancel" => {
                    if values
                        .keys()
                        .any(|key| key != "product_symbol" && key != "time")
                    {
                        return Err(DcexError::InvalidInput(
                            "unknown Arcus schedule_cancel parameter".into(),
                        ));
                    }
                    if let Some(market) = values.get("product_symbol") {
                        let info = self.market_info(market).await?;
                        let market_id = info["marketId"]
                            .as_u64()
                            .ok_or_else(|| DcexError::Decode("Arcus marketId is missing".into()))?;
                        body.insert("marketId".into(), json!(market_id));
                    }
                    if method_name == "schedule_cancel" {
                        let deadline = required(&values, "time")?.parse::<u64>().map_err(|_| {
                            DcexError::InvalidInput(
                                "invalid Arcus deadline epoch microseconds".into(),
                            )
                        })?;
                        let now = timestamp_ns()? / 1_000;
                        let remaining = deadline.checked_sub(now).ok_or_else(|| {
                            DcexError::InvalidInput("Arcus deadline must be in the future".into())
                        })?;
                        if !(5_000_000..=300_000_000).contains(&remaining) {
                            return Err(DcexError::InvalidInput(
                                "Arcus deadline must be 5 seconds to 5 minutes in the future"
                                    .into(),
                            ));
                        }
                        body.insert("time".into(), json!(deadline));
                    } else if values.contains_key("time") {
                        return Err(DcexError::InvalidInput(
                            "Arcus disarm_scheduled_cancel must omit time".into(),
                        ));
                    }
                    ("scheduleCancel", "/v1/scheduleCancel")
                }
                "adjust_isolated_margin" => {
                    if values
                        .keys()
                        .any(|key| key != "product_symbol" && key != "amount")
                    {
                        return Err(DcexError::InvalidInput(
                            "unknown Arcus adjust_isolated_margin parameter".into(),
                        ));
                    }
                    let info = self
                        .market_info(required(&values, "product_symbol")?)
                        .await?;
                    let market_id = info["marketId"]
                        .as_u64()
                        .ok_or_else(|| DcexError::Decode("Arcus marketId is missing".into()))?;
                    let amount = required(&values, "amount")?;
                    let absolute = amount.strip_prefix('-').unwrap_or(amount);
                    if decimal_parts(absolute)?.0 == 0 {
                        return Err(DcexError::InvalidInput(
                            "Arcus isolated margin amount must be nonzero".into(),
                        ));
                    }
                    body.insert("marketId".into(), json!(market_id));
                    body.insert("amount".into(), json!(amount));
                    ("adjustIsolatedMargin", "/v1/adjustIsolatedMargin")
                }
                "set_leverage" => {
                    if values.keys().any(|key| {
                        key != "product_symbol" && key != "leverage" && key != "isolated"
                    }) {
                        return Err(DcexError::InvalidInput(
                            "unknown Arcus set_leverage parameter".into(),
                        ));
                    }
                    let info = self
                        .market_info(required(&values, "product_symbol")?)
                        .await?;
                    let market_id = info["marketId"]
                        .as_u64()
                        .ok_or_else(|| DcexError::Decode("Arcus marketId is missing".into()))?;
                    let leverage = required(&values, "leverage")?
                        .parse::<u16>()
                        .map_err(|_| DcexError::InvalidInput("invalid Arcus leverage".into()))?;
                    if !(1..=1000).contains(&leverage) {
                        return Err(DcexError::InvalidInput(
                            "Arcus leverage must be in 1..=1000".into(),
                        ));
                    }
                    body.insert("marketId".into(), json!(market_id));
                    body.insert("leverage".into(), json!(leverage));
                    if let Some(isolated) = values.get("isolated") {
                        let enabled = match isolated.as_str() {
                            "true" => true,
                            "false" => false,
                            _ => {
                                return Err(DcexError::InvalidInput(
                                    "Arcus isolated must be true or false".into(),
                                ));
                            }
                        };
                        body.insert("isolated".into(), json!(enabled));
                    }
                    ("setLeverage", "/v1/setLeverage")
                }
                _ => unreachable!("legacy method dispatch is restricted"),
            };
            let timestamp = timestamp_ns()?;
            let message = legacy_signing_message(timestamp, action, &body)?;
            let signature = hex::encode(key.sign(&message).to_bytes());
            let request = HttpRequest::new(HttpMethod::Post, &self.base_url, path)
                .query("address", address)
                .header("X-API-Key", self.api_key.clone().unwrap_or_default())
                .header("X-Timestamp", timestamp.to_string())
                .header("X-Signature", signature)
                .json(json!(body));
            Ok(request)
        }
    }
}
