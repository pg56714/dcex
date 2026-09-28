//! Asset operations.
use crate::Result;
use crate::exchange::ValidatedResponse;
use crate::exchanges::aster::{AsterClient, AsterMarket, params::AsterParams};
use crate::http::HttpMethod;
impl AsterClient {
    pub(in crate::exchanges::aster) async fn asset_schema_request(
        &self,
        name: &str,
        p: &AsterParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, method, is_public, presigned, fields, required): (
            &str,
            HttpMethod,
            bool,
            bool,
            &[&str],
            &[&str],
        ) = match name {
            "exchange_futures_assets" => (
                "/fapi/v3/assetExchange",
                HttpMethod::Post,
                false,
                false,
                &[],
                &[],
            ),
            "get_asset_migration_history" => (
                "/fapi/v3/asset/migrateUser/history",
                HttpMethod::Get,
                false,
                false,
                &["batchId"],
                &["batchId"],
            ),
            _ => return Ok(None),
        };
        if public != is_public {
            return Ok(None);
        }
        p.ensure_allowed(fields, &[])?;
        for key in required {
            p.required(key)?;
        }
        for key in ["page", "size", "id", "nonce", "expired"] {
            if p.get(key).is_some() {
                p.required_u64_range(key, 1, u64::MAX)?;
            }
        }

        if name == "exchange_futures_assets" {
            let response = self
                .request_raw_auto(method, path, p.only(fields), true)
                .await?;
            response.ensure_success()?;
            let data = if response.body.is_empty() {
                serde_json::json!({})
            } else {
                crate::exchanges::aster::client::validate_response(&response)?
            };
            return Ok(Some(ValidatedResponse {
                status: response.status,
                headers: response.headers,
                data,
            }));
        }
        self.request(
            method,
            AsterMarket::Futures,
            path,
            p.only(fields),
            !is_public && !presigned,
        )
        .await
        .map(Some)
    }
}
