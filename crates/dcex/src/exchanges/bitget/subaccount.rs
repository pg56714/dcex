//! Subaccount operations.
use serde_json::Value;

use crate::Result;
use crate::exchange::ValidatedResponse;
use crate::exchanges::bitget::client::BitgetClient;
use crate::exchanges::bitget::params::BitgetParams;

impl BitgetClient {
    pub(in crate::exchanges::bitget) async fn subaccount_schema_request(
        &self,
        name: &str,
        params: &BitgetParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, fields, required) = match name {
            "create_uta_agent_sub_account" => (
                "/api/v3/user/sub-account/agent-create",
                &["username", "passphrase", "note"][..],
                &["username", "passphrase"][..],
            ),
            _ => return Ok(None),
        };
        params.ensure_allowed(fields, false)?;
        for key in required {
            nonempty(params, key)?;
        }
        {
            let username = nonempty(params, "username")?;
            if username.len() > 20 || !username.bytes().all(|b| b.is_ascii_lowercase()) {
                return Err(invalid("username requires 1..20 lowercase ASCII letters"));
            }
            let passphrase = nonempty(params, "passphrase")?;
            if !(8..=32).contains(&passphrase.len())
                || !passphrase.bytes().all(|b| b.is_ascii_alphanumeric())
            {
                return Err(invalid(
                    "passphrase requires 8..32 ASCII letters and digits",
                ));
            }
        }
        self.post_private(path, Value::Object(params.body(fields)))
            .await
            .map(Some)
    }
}

use crate::exchanges::bitget::params::invalid;
use crate::exchanges::bitget::params::nonempty;
