//! Subaccount operations.
use crate::exchange::ValidatedResponse;
use crate::exchanges::aster::{AsterClient, AsterMarket, params::AsterParams};
use crate::{DcexError, Result};
impl AsterClient {
    pub(in crate::exchanges::aster) async fn subaccount_schema_request(
        &self,
        name: &str,
        p: &AsterParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        static ROUTES: std::sync::OnceLock<Vec<crate::exchanges::schema::Route>> =
            std::sync::OnceLock::new();
        let Some(route) = crate::exchanges::schema::route(
            &ROUTES,
            include_str!("schemas/routes_subaccount.json"),
            name,
        ) else {
            return Ok(None);
        };
        let (path, method, is_public, presigned, fields, required) = (
            route.path,
            route.method,
            route.is_public,
            route.presigned,
            route.fields,
            route.required,
        );
        if public != is_public {
            return Ok(None);
        }
        route.validate(|key| p.get(key))?;
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
