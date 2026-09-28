use serde_json::{Value, json};

use super::client::HyperliquidClient;
use super::params::HyperliquidParams;
use super::trade::user_signed_fields;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl HyperliquidClient {
    pub(super) async fn completion_private_request(
        &self,
        method: &str,
        params: &HyperliquidParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (kind, fields): (&str, &[&str]) = match method {
            "send_asset_signed" => (
                "sendAsset",
                &[
                    "destination",
                    "sourceDex",
                    "destinationDex",
                    "token",
                    "amount",
                    "fromSubAccount",
                ],
            ),
            "send_usd_signed" => ("usdSend", &["destination", "amount"]),
            "send_spot_signed" => ("spotSend", &["destination", "token", "amount"]),
            "withdraw_from_bridge_signed" => ("withdraw3", &["destination", "amount"]),
            "approve_builder_fee_signed" => ("approveBuilderFee", &["builder", "maxFeeRate"]),
            "send_to_evm_with_data_signed" => ("sendToEvmWithData", &["action"]),
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
        if kind == "sendToEvmWithData" {
            action = serde_json::from_str(params.required("action")?)
                .map_err(|_| DcexError::InvalidInput("action must be a JSON object".into()))?;
            let object = action
                .as_object()
                .ok_or_else(|| DcexError::InvalidInput("action must be a JSON object".into()))?;
            let expected = [
                "type",
                "hyperliquidChain",
                "signatureChainId",
                "token",
                "amount",
                "sourceDex",
                "destinationRecipient",
                "addressEncoding",
                "destinationChainId",
                "gasLimit",
                "data",
                "nonce",
            ];
            if object.len() != expected.len()
                || expected.iter().any(|k| !object.contains_key(*k))
                || action["type"] != kind
                || action["hyperliquidChain"] != network
                || action["signatureChainId"] != chain
                || action["nonce"].as_u64() != Some(nonce)
            {
                return Err(DcexError::InvalidInput("sendToEvmWithData requires the documented action fields and matching network, chain ID and nonce".into()));
            }
            for key in [
                "token",
                "amount",
                "sourceDex",
                "destinationRecipient",
                "addressEncoding",
            ] {
                if action[key]
                    .as_str()
                    .is_none_or(|s| s.is_empty() && key != "sourceDex")
                {
                    return Err(DcexError::InvalidInput(format!("{key} must be a string")));
                }
            }
            if !matches!(action["addressEncoding"].as_str(), Some("hex" | "base58"))
                || action["destinationChainId"]
                    .as_u64()
                    .is_none_or(|n| n > u32::MAX as u64)
                || action["gasLimit"].as_u64().is_none()
            {
                return Err(DcexError::InvalidInput(
                    "invalid addressEncoding, destinationChainId or gasLimit".into(),
                ));
            }
            // Preserve caller-signed data; the API table describes bytes but does
            // not specify a JSON encoding or publish an SDK signer for this action.
        } else {
            for key in fields {
                let raw = params.get(key).ok_or_else(|| {
                    DcexError::InvalidInput(format!("missing required parameter: {key}"))
                })?;
                if raw.is_empty()
                    && !["sourceDex", "destinationDex", "fromSubAccount"].contains(key)
                {
                    return Err(DcexError::InvalidInput(format!("{key} must not be empty")));
                }
                if ["destination", "builder", "fromSubAccount"].contains(key) && !raw.is_empty() {
                    params.address(key)?;
                }
                // EIP-712 uses strings for some addresses: never lowercase or
                // otherwise rewrite a caller-signed value.
                action[*key] = raw.into();
            }
            let timestamp_key = if matches!(kind, "usdSend" | "spotSend" | "withdraw3") {
                "time"
            } else {
                "nonce"
            };
            action[timestamp_key] = nonce.into();
        }
        if let Some(amount) = action.get("amount").and_then(Value::as_str)
            && !crate::common::is_positive_plain_decimal(amount)
        {
            return Err(DcexError::InvalidInput(
                "amount must be a positive plain decimal string".into(),
            ));
        }
        if kind == "approveBuilderFee" {
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
            super::endpoints::EXCHANGE,
            serde_json::to_vec(&payload).map_err(|e| DcexError::Decode(e.to_string()))?,
            None,
            false,
        )
        .await
        .map(Some)
    }
}
