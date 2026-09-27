//! Additional V3 endpoints from https://github.com/asterdex/api-docs.
use super::{AsterClient, AsterMarket, params::AsterParams};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};
impl AsterClient {
    pub(super) async fn additional_request(
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
            "get_asset_logos" => (
                "/fapi/v3/common/asset/all-asset-logo",
                HttpMethod::Get,
                true,
                false,
                &[],
                &[],
            ),
            "exchange_futures_assets" => (
                "/fapi/v3/assetExchange",
                HttpMethod::Post,
                false,
                false,
                &[],
                &[],
            ),
            "get_sub_accounts" => (
                "/fapi/v3/getSubAccountList",
                HttpMethod::Get,
                false,
                false,
                &[],
                &[],
            ),
            "get_direct_announcements" => (
                "/fapi/v3/announcement/direct",
                HttpMethod::Get,
                false,
                false,
                &["page", "size"],
                &[],
            ),
            "get_direct_announcement" => (
                "/fapi/v3/announcement/directById",
                HttpMethod::Get,
                false,
                false,
                &["id"],
                &["id"],
            ),
            "create_sub_account_signed" => (
                "/fapi/v3/createSubAccount",
                HttpMethod::Post,
                false,
                true,
                &[
                    "subAccountName",
                    "subSourceAddr",
                    "nonce",
                    "user",
                    "signer",
                    "childSignature",
                    "signature",
                ],
                &[
                    "subAccountName",
                    "subSourceAddr",
                    "nonce",
                    "user",
                    "signer",
                    "childSignature",
                    "signature",
                ],
            ),
            "update_sub_account_signed" => (
                "/fapi/v3/updateSubAccount",
                HttpMethod::Post,
                false,
                true,
                &[
                    "subSourceAddr",
                    "nonce",
                    "user",
                    "signer",
                    "subAccountName",
                    "status",
                    "signature",
                ],
                &["subSourceAddr", "nonce", "user", "signer", "signature"],
            ),
            "bind_sub_account_signed" => (
                "/fapi/v3/sub-accounts/bind",
                HttpMethod::Post,
                false,
                true,
                &[
                    "childAddress",
                    "name",
                    "nonce",
                    "user",
                    "childSignature",
                    "signature",
                ],
                &[
                    "childAddress",
                    "name",
                    "nonce",
                    "user",
                    "childSignature",
                    "signature",
                ],
            ),
            "register_agent_signed" => (
                "/fapi/v3/registerAndApproveAgent",
                HttpMethod::Post,
                false,
                true,
                &[
                    "user",
                    "nonce",
                    "agentName",
                    "agentAddress",
                    "expired",
                    "signatureChainId",
                    "canSpotTrade",
                    "canPerpTrade",
                    "canWithdraw",
                    "ipWhitelist",
                    "signature",
                ],
                &[
                    "user",
                    "nonce",
                    "agentName",
                    "agentAddress",
                    "expired",
                    "signatureChainId",
                    "canSpotTrade",
                    "canPerpTrade",
                    "canWithdraw",
                    "signature",
                ],
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
        if presigned {
            if name == "update_sub_account_signed" {
                p.required_any(&["subAccountName", "status"])?;
                p.optional_one_of("status", &["NORMAL", "FROZEN"])?;
            }
            for key in ["canSpotTrade", "canPerpTrade", "canWithdraw"] {
                p.optional_one_of(key, &["true", "false"])?;
            }
            if name == "register_agent_signed" {
                p.required_one_of("signatureChainId", &["56", "101"])?;
                if p.get("canWithdraw") == Some("true") {
                    p.required("ipWhitelist")?;
                }
            }
            // A wallet signature is supplied by the caller. Never re-sign with the agent
            // or replace the nonce: either would invalidate the wallet authorization.
            for key in ["signature", "childSignature"] {
                if let Some(value) = p.get(key) {
                    let hex = value.strip_prefix("0x").is_some_and(|v| {
                        v.len() == 130 && v.bytes().all(|b| b.is_ascii_hexdigit())
                    });
                    let base58 = bs58::decode(value).into_vec().is_ok_and(|v| v.len() == 64);
                    if !hex && !base58 {
                        return Err(DcexError::InvalidInput(format!(
                            "invalid Aster {key} encoding"
                        )));
                    }
                }
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
                super::client::validate_response(&response)?
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
