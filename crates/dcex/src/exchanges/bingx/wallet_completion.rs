//! Wallet writes from the official BingX documentation request tables.
use super::{client::BingxClient, params::BingxParams};
use crate::{DcexError, Result, exchange::ValidatedResponse, http::HttpMethod};
use serde_json::{Map, Value};

impl BingxClient {
    pub(super) async fn wallet_completion_request(
        &self,
        name: &str,
        p: &BingxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, transfer, json_body) = match name {
            "transfer_master_internal" => (
                "/openApi/wallets/v1/capital/innerTransfer/apply",
                true,
                false,
            ),
            "transfer_sub_account_internal" => (
                "/openApi/wallets/v1/capital/subAccountInnerTransfer/apply",
                true,
                true,
            ),
            "create_withdrawal" => ("/openApi/wallets/v1/capital/withdraw/apply", false, false),
            _ => return Ok(None),
        };
        let fields: &[&str] = if transfer {
            &[
                "coin",
                "userAccountType",
                "userAccount",
                "amount",
                "callingCode",
                "walletType",
                "transferClientId",
                "recvWindow",
            ]
        } else {
            &[
                "coin",
                "network",
                "address",
                "addressTag",
                "amount",
                "walletType",
                "withdrawOrderId",
                "vaspEntityId",
                "recipientLastName",
                "recipientFirstName",
                "dateOfbirth",
                "recvWindow",
            ]
        };
        p.ensure_allowed(fields)?;
        for key in ["coin", "amount", "walletType"] {
            p.required(key)?;
        }
        if !crate::common::is_positive_plain_decimal(p.required("amount")?) {
            return Err(invalid("amount requires a positive plain decimal string"));
        }
        if transfer {
            p.required("userAccount")?;
            if !matches!(p.required("userAccountType")?, "1" | "2" | "3") {
                return Err(invalid("userAccountType must be 1, 2 or 3"));
            }
            if p.get("userAccountType") == Some("2") {
                p.required("callingCode")?;
            }
        } else {
            p.required("address")?;
        }
        for key in ["transferClientId", "withdrawOrderId"] {
            if p.get(key).is_some_and(|s| {
                s.is_empty() || s.len() >= 100 || !s.chars().all(|c| c.is_ascii_alphanumeric())
            }) {
                return Err(invalid(
                    "client transfer/withdrawal ID must be alphanumeric and shorter than 100 characters",
                ));
            }
        }
        let mut body = Map::new();
        for (key, value) in p.only(fields) {
            let encoded = if matches!(
                key.as_str(),
                "walletType" | "userAccountType" | "recvWindow"
            ) {
                let n = value
                    .parse::<u64>()
                    .map_err(|_| invalid("integer field must be unsigned"))?;
                Value::from(n)
            } else if key == "amount" {
                // arbitrary_precision preserves the caller's decimal digits in JSON.
                serde_json::from_str(&value).map_err(|_| invalid("invalid decimal amount"))?
            } else {
                Value::String(value)
            };
            body.insert(key, encoded);
        }
        if json_body {
            self.request(
                HttpMethod::Post,
                path,
                vec![],
                true,
                vec![],
                Some(Value::Object(body)),
            )
            .await
            .map(Some)
        } else {
            self.request(HttpMethod::Post, path, p.only(fields), true, vec![], None)
                .await
                .map(Some)
        }
    }
}
fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("BingX: {message}"))
}
