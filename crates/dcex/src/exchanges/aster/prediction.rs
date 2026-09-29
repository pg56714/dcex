//! Prediction REST API: native prediction symbols, a separate host, and V3 agent signing.
use super::{AsterClient, params::AsterParams};
use crate::{DcexError, Result, exchange::ValidatedResponse};
impl AsterClient {
    pub(super) async fn prediction_dispatch(
        &self,
        name: &str,
        p: &AsterParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        match crate::exchanges::schema::fund_domain(name) {
            Some(crate::exchanges::schema::FundDomain::Withdrawals) => {
                self.withdrawals_prediction_dispatch(name, p, public).await
            }
            Some(crate::exchanges::schema::FundDomain::Transfers) => {
                self.transfers_prediction_dispatch(name, p, public).await
            }
            None => self.prediction_dispatch_transport(name, p, public).await,
        }
    }

    pub(in crate::exchanges::aster) async fn prediction_dispatch_transport(
        &self,
        name: &str,
        p: &AsterParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        if name == "noop_prediction" && !public {
            p.ensure_allowed(&["nonce"], &[])?;
            let nonce = p
                .required("nonce")?
                .parse::<u64>()
                .map_err(|_| DcexError::InvalidInput("nonce must be an unsigned integer".into()))?;
            return self.prediction_noop(nonce).await.map(Some);
        }
        static ROUTES: std::sync::OnceLock<Vec<crate::exchanges::schema::Route>> =
            std::sync::OnceLock::new();
        let Some(route) = crate::exchanges::schema::route(
            &ROUTES,
            include_str!("schemas/routes_prediction.json"),
            name,
        ) else {
            return Ok(None);
        };
        let (path, verb, is_public, fields, required, integers, decimals) = (
            route.path,
            route.method,
            route.is_public,
            route.fields,
            route.required,
            route.integers,
            route.decimals,
        );
        if public != is_public {
            return Ok(None);
        }
        route.validate(|key| p.get(key))?;
        p.ensure_allowed(fields, &[])?;
        for key in required {
            p.required(key)?;
        }
        for key in integers {
            if p.get(key).is_some() {
                p.required_u64_range(key, if *key == "limit" { 1 } else { 0 }, u64::MAX)?;
            }
        }
        for key in decimals {
            if let Some(v) = p.get(key)
                && !crate::common::is_positive_plain_decimal(v)
            {
                return Err(DcexError::InvalidInput(format!("{key} must be positive")));
            }
        }
        if name.ends_with("_split") || name.ends_with("_merge") {
            let v = p.required("quantity")?;
            if !v.bytes().all(|b| b.is_ascii_digit()) || v.bytes().all(|b| b == b'0') {
                return Err(DcexError::InvalidInput(
                    "quantity must be a positive whole integer".into(),
                ));
            }
        }
        if let (Some(a), Some(b)) = (p.get("startTime"), p.get("endTime"))
            && a.parse::<u64>().unwrap() > b.parse::<u64>().unwrap()
        {
            return Err(DcexError::InvalidInput("startTime exceeds endTime".into()));
        }
        if matches!(
            name,
            "get_prediction_position_histories" | "get_prediction_settlement_histories"
        ) && p.get("limit").is_some()
        {
            p.required_u64_range("limit", 1, 1000)?;
        }
        if matches!(
            name,
            "get_prediction_order" | "get_prediction_open_order" | "cancel_prediction_order"
        ) {
            p.required_any(&["orderId", "origClientOrderId"])?;
        }
        if name == "create_prediction_order" {
            p.required_one_of("side", &["BUY", "SELL"])?;
            p.required_one_of(
                "type",
                &[
                    "LIMIT",
                    "MARKET",
                    "STOP",
                    "STOP_MARKET",
                    "TAKE_PROFIT",
                    "TAKE_PROFIT_MARKET",
                ],
            )?;
            p.optional_one_of("timeInForce", &["GTC", "IOC", "FOK", "GTX"])?;
            let kind = p.required("type")?;
            let keys: &[&str] = match kind {
                "LIMIT" => &["timeInForce", "quantity", "price"],
                "STOP" | "TAKE_PROFIT" => &["quantity", "price", "stopPrice"],
                "STOP_MARKET" | "TAKE_PROFIT_MARKET" => &["quantity", "stopPrice"],
                _ => &[],
            };
            for k in keys {
                p.required(k)?;
            }
            if kind == "MARKET" {
                p.required_any(&["quantity", "quoteOrderQty"])?;
            }
            if p.get("quantity").is_some() && p.get("quoteOrderQty").is_some() {
                return Err(DcexError::InvalidInput(
                    "quantity and quoteOrderQty are mutually exclusive".into(),
                ));
            }
        }
        if name == "create_prediction_asset_wallet_transfer" {
            p.required_one_of("kindType", &["FUTURE_SPOT", "SPOT_FUTURE"])?;
        }
        self.prediction_request(verb, path, p.only(fields), !public)
            .await
            .map(Some)
    }
}
