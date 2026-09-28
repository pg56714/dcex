//! Named deployment and administration actions from the official API and SDK.
use crate::exchanges::hyperliquid::{
    HyperliquidClient, msgpack::parse_ordered_json, params::HyperliquidParams,
};
use crate::{DcexError, Result, exchange::ValidatedResponse, http::HttpMethod};
use serde::Deserialize;
use serde_json::{Value, json};
use std::sync::OnceLock;

#[derive(Deserialize)]
struct Operation {
    name: String,
    #[serde(rename = "type")]
    kind: String,
    variant: String,
    public: bool,
    user: bool,
    signed: bool,
    testnet_only: bool,
    required_fields: Vec<String>,
}

fn invalid(message: impl std::fmt::Display) -> DcexError {
    DcexError::InvalidInput(format!("Hyperliquid: {message}"))
}

impl HyperliquidClient {
    pub(in crate::exchanges::hyperliquid) async fn catalog_request(
        &self,
        name: &str,
        params: &HyperliquidParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        static OPERATIONS: OnceLock<Vec<Operation>> = OnceLock::new();
        let operations = OPERATIONS.get_or_init(load_schemas);
        let Some(op) = operations
            .iter()
            .find(|op| op.name == name && op.public == public)
        else {
            return Ok(None);
        };
        if public {
            params.ensure_allowed(if op.user { &["user"] } else { &[] })?;
            let mut payload = json!({"type":op.kind});
            if op.user {
                payload["user"] = params.address("user")?.into();
            }
            return self.info_payload(payload).await.map(Some);
        }
        if op.testnet_only && !self.is_testnet() {
            return Err(invalid("this action is documented for testnet only"));
        }
        let mut allowed = vec!["action", "nonce", "vaultAddress", "expiresAfter"];
        if op.signed {
            allowed.push("signature");
        }
        let requires_confirmation = matches!(
            name,
            "perp_deploy_disable_dex" | "convert_to_multi_sig_user_signed"
        );
        if requires_confirmation {
            allowed.push("confirm");
            if params.get("confirm") != Some("true") {
                return Err(invalid("this irreversible operation requires confirm=true"));
            }
        }
        params.ensure_allowed(&allowed)?;
        let action = parse_ordered_json(params.required("action")?, "action")?;
        let value = action.to_json();
        let object = value
            .as_object()
            .ok_or_else(|| invalid("action must be an object"))?;
        if value.get("type").and_then(Value::as_str) != Some(op.kind.as_str()) {
            return Err(invalid(format!("action.type must be {}", op.kind)));
        }
        let variants = crate::exchanges::hyperliquid::administration::action_variants(&op.kind);
        crate::exchanges::hyperliquid::deployment::validate_action_shape(
            object,
            variants,
            &op.required_fields,
            &op.variant,
        )?;
        if !op.signed {
            return self.submit_action(action, params).await.map(Some);
        }
        let nonce = params.required_u64("nonce")?;
        crate::exchanges::hyperliquid::administration::validate_multisig_nonce(
            &op.kind, &value, nonce,
        )?;
        let signature = crate::exchanges::hyperliquid::trade::signature_param(params)?;
        let mut payload = json!({"action":value,"nonce":nonce,"signature":signature});
        if let Some(vault) = params.get("vaultAddress") {
            params.address("vaultAddress")?;
            payload["vaultAddress"] = vault.into();
        }
        if let Some(expiry) = params.optional_u64("expiresAfter")? {
            payload["expiresAfter"] = expiry.into();
        }
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

fn load_schemas() -> Vec<Operation> {
    [
        include_str!("../schemas/administration.json"),
        include_str!("../schemas/deployment.json"),
        include_str!("../schemas/market.json"),
        include_str!("../schemas/account.json"),
    ]
    .into_iter()
    .flat_map(|raw| serde_json::from_str::<Vec<Operation>>(raw).expect("checked endpoint schemas"))
    .collect()
}
