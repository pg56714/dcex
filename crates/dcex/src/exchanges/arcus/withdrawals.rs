//! Fund movement and batch request implementations.

use super::ArcusClient;
use crate::{Result, exchange::ValidatedResponse};
impl ArcusClient {
    pub(super) async fn withdrawal_schema_request(
        &self,
        name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.field_schema_request(name, params).await
    }
}

use crate::exchanges::arcus::params::invalid;
use serde_json::{Value, json};
use std::collections::BTreeMap;
impl ArcusClient {
    pub(super) fn validate_withdrawal(&self, value: &Value, signed: bool) -> Result<()> {
        let amount = value["amount"].as_str().expect("validated string");
        if !amount.bytes().all(|b| b.is_ascii_digit())
            || !amount.parse::<i64>().is_ok_and(|n| n > 0)
        {
            return Err(invalid(
                "withdrawal amount must be a positive int64 quantum string",
            ));
        }
        if let Some(asset) = value.get("spotAssetId")
            && asset.as_u64().is_none_or(|n| n > u16::MAX as u64)
        {
            return Err(invalid("spotAssetId must be uint16"));
        }
        if signed {
            let configured = self
                .address
                .as_deref()
                .ok_or_else(|| invalid("configure the API key's master address"))?;
            let address = value["ethereumAddress"]
                .as_str()
                .expect("validated address");
            if !address.eq_ignore_ascii_case(configured)
                || value
                    .get("accountIndex")
                    .and_then(Value::as_u64)
                    .unwrap_or(0)
                    != self.account_index as u64
            {
                return Err(invalid(
                    "API withdrawal must match the configured address and account index",
                ));
            }
        } else {
            for key in ["r", "s"] {
                let raw = value["signature"][key]
                    .as_str()
                    .expect("validated signature");
                let digits = raw.strip_prefix("0x").unwrap_or(raw);
                if digits.bytes().all(|b| b == b'0') {
                    return Err(invalid("signature r/s must be nonzero"));
                }
            }
        }

        Ok(())
    }
}
pub(super) fn withdrawal_message(value: &Value, timestamp: u64) -> Result<Vec<u8>> {
    let typed = BTreeMap::from([
        (
            "ad",
            json!(
                value["ethereumAddress"]
                    .as_str()
                    .expect("address")
                    .to_ascii_lowercase()
            ),
        ),
        (
            "ai",
            json!(
                value
                    .get("accountIndex")
                    .and_then(Value::as_u64)
                    .unwrap_or(0)
            ),
        ),
        ("ct", json!(timestamp)),
        ("n", value["nonce"].clone()),
        ("op", json!(5)),
        (
            "q",
            json!(
                value["amount"]
                    .as_str()
                    .expect("amount")
                    .parse::<i64>()
                    .expect("validated")
            ),
        ),
        ("v", json!(1)),
    ]);
    serde_json::to_vec(&typed).map_err(invalid)
}

impl super::client::ArcusClient {
    pub(in crate::exchanges::arcus) async fn withdrawals_field_schema_request(
        &self,
        name: &str,
        params: Vec<(String, String)>,
    ) -> crate::Result<crate::exchange::ValidatedResponse> {
        if crate::exchanges::schema::fund_domain(name)
            != Some(crate::exchanges::schema::FundDomain::Withdrawals)
        {
            return Err(crate::DcexError::InvalidInput(
                "fund operation routed to the wrong owner".into(),
            ));
        }
        self.field_schema_request_transport(name, params).await
    }
}
