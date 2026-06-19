use serde_json::json;

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::HyperliquidClient;
use super::params::HyperliquidParams;

impl HyperliquidClient {
    pub(super) async fn asset_public_request(
        &self,
        method_name: &str,
        params: &HyperliquidParams,
    ) -> Result<Option<ValidatedResponse>> {
        let payload = match method_name {
            "user_vault_equities" => json!({
                "type": "userVaultEquities",
                "user": params.required("user")?,
            }),
            _ => return Ok(None),
        };
        Ok(Some(self.info_payload(payload).await?))
    }
}
