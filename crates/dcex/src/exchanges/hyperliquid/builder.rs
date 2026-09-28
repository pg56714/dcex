//! Builder operations.
use serde_json::json;

use crate::exchange::ValidatedResponse;
use crate::exchanges::hyperliquid::client::HyperliquidClient;
use crate::exchanges::hyperliquid::params::HyperliquidParams;
use crate::exchanges::hyperliquid::trade::user_signed_fields;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl HyperliquidClient {
    pub(in crate::exchanges::hyperliquid) async fn builder_schema_request(
        &self,
        method: &str,
        params: &HyperliquidParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (kind, fields): (&str, &[&str]) = match method {
            "approve_builder_fee_signed" => ("approveBuilderFee", &["builder", "maxFeeRate"]),
            _ => return Ok(None),
        };
        let mut allowed = fields.to_vec();
        allowed.extend(["nonce", "signature", "signatureChainId"]);
        params.ensure_allowed(&allowed)?;
        let (nonce, chain, signature) = user_signed_fields(params)?;
        let network = if self.is_testnet() {
            "Testnet"
        } else {
            "Mainnet"
        };
        let mut action = json!({"type":kind, "hyperliquidChain":network, "signatureChainId":chain});
        {
            for key in fields {
                let raw = params.get(key).ok_or_else(|| {
                    DcexError::InvalidInput(format!("missing required parameter: {key}"))
                })?;
                if raw.is_empty() {
                    return Err(DcexError::InvalidInput(format!("{key} must not be empty")));
                }
                if *key == "builder" {
                    params.address(key)?;
                }
                // EIP-712 uses strings for some addresses: never lowercase or
                // otherwise rewrite a caller-signed value.
                action[*key] = raw.into();
            }
            action["nonce"] = nonce.into();
        }
        {
            let rate = params.required("maxFeeRate")?;
            let number = rate.strip_suffix('%').ok_or_else(|| {
                DcexError::InvalidInput("maxFeeRate must be a percent string".into())
            })?;
            let zero = !number.is_empty()
                && number.bytes().any(|b| b == b'0')
                && number.bytes().all(|b| b == b'0' || b == b'.')
                && number.bytes().filter(|b| *b == b'.').count() <= 1;
            if !zero && !crate::common::is_positive_plain_decimal(number) {
                return Err(DcexError::InvalidInput(
                    "maxFeeRate must be a nonnegative percent string".into(),
                ));
            }
        }
        let payload = json!({"action":action,"nonce":nonce,"signature":signature});
        self.request(
            HttpMethod::Post,
            crate::exchanges::hyperliquid::endpoints::EXCHANGE,
            serde_json::to_vec(&payload).map_err(|e| DcexError::Decode(e.to_string()))?,
            None,
            false,
        )
        .await
        .map(Some)
    }
}
