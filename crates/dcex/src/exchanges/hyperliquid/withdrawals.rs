// Transfers operations.
use serde_json::{Value, json};

use crate::exchange::ValidatedResponse;
use crate::exchanges::hyperliquid::client::HyperliquidClient;
use crate::exchanges::hyperliquid::params::HyperliquidParams;
use crate::exchanges::hyperliquid::trade::user_signed_fields;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl HyperliquidClient {
    pub(in crate::exchanges::hyperliquid) async fn transfers_schema_request(
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

mod signed_requests {
    use crate::exchanges::hyperliquid::trade::*;
    impl HyperliquidClient {
        pub(in crate::exchanges::hyperliquid) async fn dispatch_withdraw_staking_signed(
            &self,
            params: &HyperliquidParams,
        ) -> Result<ValidatedResponse> {
            self.additional_user_action("cWithdraw", params).await
        }
    }
}

mod wrappers {
    use crate::exchanges::hyperliquid::HyperliquidClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; HyperliquidClient;
     public [

     ];
     private [
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
    withdraw_staking_signed(
                wei => "wei",
                nonce => "nonce",
                signature => "signature",
                signature_chain_id => "signatureChainId"
            ),
    send_asset_signed(destination => "destination", source_dex => "sourceDex", destination_dex => "destinationDex", token => "token", amount => "amount", from_sub_account => "fromSubAccount", nonce => "nonce", signature => "signature", signature_chain_id => "signatureChainId"),
    send_usd_signed(destination => "destination", amount => "amount", nonce => "nonce", signature => "signature", signature_chain_id => "signatureChainId"),
    send_spot_signed(destination => "destination", token => "token", amount => "amount", nonce => "nonce", signature => "signature", signature_chain_id => "signatureChainId"),

            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
    withdraw_from_bridge_signed(destination => "destination", amount => "amount", nonce => "nonce", signature => "signature", signature_chain_id => "signatureChainId"),
    send_to_evm_with_data_signed(action => "action", nonce => "nonce", signature => "signature", signature_chain_id => "signatureChainId")
     ];
    }
}

impl super::client::HyperliquidClient {
    pub(in crate::exchanges::hyperliquid) async fn withdrawals_catalog_request(
        &self,
        name: &str,
        params: &super::params::HyperliquidParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        debug_assert!(
            crate::exchanges::schema::fund_domain(name)
                == Some(crate::exchanges::schema::FundDomain::Withdrawals)
        );
        self.catalog_request_transport(name, params, public).await
    }
}
