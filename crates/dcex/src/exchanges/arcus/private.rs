use super::client::ArcusClient;
use crate::Result;
use crate::exchange::ValidatedResponse;

impl ArcusClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
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
