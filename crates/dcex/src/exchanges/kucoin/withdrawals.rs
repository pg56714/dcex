//! Classic V3 and UTA V2 withdrawal endpoints from their official request schemas.
use super::{
    client::{KucoinClient, KucoinMarket},
    params::{KucoinParams, validate_enum},
};
use crate::exchanges::kucoin::params::invalid;
use crate::{DcexError, Result, exchange::ValidatedResponse, http::HttpMethod};
use serde_json::Value;

impl KucoinClient {
    pub(super) async fn withdrawal_request(
        &self,
        name: &str,
        p: &KucoinParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, method, body) = match name {
            "create_withdrawal" | "create_uta_withdrawal" => {
                let strings = &[
                    "currency",
                    "amount",
                    "toAddress",
                    "withdrawType",
                    "chain",
                    "memo",
                    "remark",
                    "feeDeductType",
                ];
                p.ensure_allowed(&[
                    "currency",
                    "amount",
                    "toAddress",
                    "withdrawType",
                    "chain",
                    "memo",
                    "remark",
                    "feeDeductType",
                    "isInner",
                ])?;
                for field in ["currency", "amount", "toAddress", "withdrawType"] {
                    if p.required(field)?.trim().is_empty() {
                        return Err(invalid(format!("{field} is required")));
                    }
                }
                if !crate::common::is_positive_plain_decimal(p.required("amount")?) {
                    return Err(invalid("amount must be a positive plain decimal string"));
                }
                validate_enum(p, "withdrawType", &["ADDRESS", "UID", "MAIL", "PHONE"])?;
                validate_enum(p, "feeDeductType", &["INTERNAL", "EXTERNAL"])?;
                let body = Value::Object(p.body(strings, &[], &["isInner"])?);
                (
                    if name == "create_uta_withdrawal" {
                        "/api/ua/v2/asset/withdrawal"
                    } else {
                        "/api/v3/withdrawals"
                    }
                    .to_string(),
                    HttpMethod::Post,
                    Some(body),
                )
            }
            "cancel_uta_withdrawal" => {
                p.ensure_allowed(&["withdrawId"])?;
                let id = p.required("withdrawId")?;
                if id.trim().is_empty() {
                    return Err(invalid("withdrawId is required"));
                }
                (
                    "/api/ua/v2/asset/withdraw/cancel".to_string(),
                    HttpMethod::Post,
                    Some(serde_json::json!({"withdrawId": id})),
                )
            }
            "cancel_withdrawal" => {
                p.ensure_allowed(&["withdrawalId"])?;
                let id = p.required("withdrawalId")?;
                if id.is_empty()
                    || !id
                        .chars()
                        .all(|c| c.is_ascii_alphanumeric() || matches!(c, '-' | '_'))
                {
                    return Err(invalid("invalid withdrawalId path segment"));
                }
                (
                    format!("/api/v1/withdrawals/{id}"),
                    HttpMethod::Delete,
                    None,
                )
            }
            _ => return Ok(None),
        };
        let encoded = body
            .map(|body| serde_json::to_vec(&body))
            .transpose()
            .map_err(|e| DcexError::Decode(e.to_string()))?;
        self.request(method, KucoinMarket::Spot, path, vec![], encoded, true)
            .await
            .map(Some)
    }
}

mod wrappers {
    use crate::exchanges::kucoin::KucoinClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; KucoinClient;
     public [

     ];
     private [
    get_futures_max_withdraw_margin(product_symbol => "product_symbol")
     ];
    }
}

impl super::client::KucoinClient {
    pub(in crate::exchanges::kucoin) async fn withdrawals_table_request(
        &self,
        name: &str,
        params: &super::params::KucoinParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.table_request_transport(name, params, public).await
    }
}

impl super::client::KucoinClient {
    pub(in crate::exchanges::kucoin) async fn withdrawals_catalog_request(
        &self,
        name: &str,
        params: &super::params::KucoinParams,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.catalog_request_transport(name, params).await
    }
}
