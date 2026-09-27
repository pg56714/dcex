//! Prediction REST API: native prediction symbols, a separate host, and V3 agent signing.
use super::{AsterClient, params::AsterParams};
use crate::{DcexError, Result, exchange::ValidatedResponse, http::HttpMethod};
impl AsterClient {
    pub(super) async fn prediction_dispatch(
        &self,
        name: &str,
        p: &AsterParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, verb, is_public, fields, required, integers, decimals): (
            &str,
            HttpMethod,
            bool,
            &[&str],
            &[&str],
            &[&str],
            &[&str],
        ) = match name {
            "get_prediction_ping" => ("/api/v3/ping", HttpMethod::Get, true, &[], &[], &[], &[]),
            "get_prediction_time" => ("/api/v3/time", HttpMethod::Get, true, &[], &[], &[], &[]),
            "get_prediction_exchange_info" => (
                "/api/v3/prediction/exchangeInfo",
                HttpMethod::Get,
                true,
                &[],
                &[],
                &[],
                &[],
            ),
            "get_prediction_depth" => (
                "/api/v3/depth",
                HttpMethod::Get,
                true,
                &["symbol", "limit"],
                &["symbol"],
                &["limit"],
                &[],
            ),
            "get_prediction_trades" => (
                "/api/v3/trades",
                HttpMethod::Get,
                true,
                &["symbol", "limit"],
                &["symbol"],
                &["limit"],
                &[],
            ),
            "get_prediction_historical_trades" => (
                "/api/v3/historicalTrades",
                HttpMethod::Get,
                true,
                &["symbol", "limit", "fromId"],
                &["symbol"],
                &["limit", "fromId"],
                &[],
            ),
            "get_prediction_agg_trades" => (
                "/api/v3/aggTrades",
                HttpMethod::Get,
                true,
                &["symbol", "fromId", "startTime", "endTime", "limit"],
                &["symbol"],
                &["fromId", "startTime", "endTime", "limit"],
                &[],
            ),
            "get_prediction_klines" => (
                "/api/v3/klines",
                HttpMethod::Get,
                true,
                &["symbol", "interval", "startTime", "endTime", "limit"],
                &["symbol", "interval"],
                &["startTime", "endTime", "limit"],
                &[],
            ),
            "get_prediction_ticker_24hr" => (
                "/api/v3/ticker/24hr",
                HttpMethod::Get,
                true,
                &["symbol"],
                &[],
                &[],
                &[],
            ),
            "get_prediction_ticker_price" => (
                "/api/v3/ticker/price",
                HttpMethod::Get,
                true,
                &["symbol"],
                &[],
                &[],
                &[],
            ),
            "get_prediction_ticker_book_ticker" => (
                "/api/v3/ticker/bookTicker",
                HttpMethod::Get,
                true,
                &["symbol"],
                &[],
                &[],
                &[],
            ),
            "get_prediction_commission_rate" => (
                "/api/v3/commissionRate",
                HttpMethod::Get,
                false,
                &["symbol"],
                &["symbol"],
                &[],
                &[],
            ),
            "create_prediction_order" => (
                "/api/v3/order",
                HttpMethod::Post,
                false,
                &[
                    "symbol",
                    "side",
                    "type",
                    "timeInForce",
                    "quantity",
                    "quoteOrderQty",
                    "price",
                    "newClientOrderId",
                    "stopPrice",
                ],
                &["symbol", "side", "type"],
                &[],
                &["quantity", "quoteOrderQty", "price", "stopPrice"],
            ),
            "cancel_prediction_order" => (
                "/api/v3/order",
                HttpMethod::Delete,
                false,
                &["symbol", "orderId", "origClientOrderId"],
                &["symbol"],
                &["orderId"],
                &[],
            ),
            "get_prediction_order" => (
                "/api/v3/order",
                HttpMethod::Get,
                false,
                &["symbol", "orderId", "origClientOrderId"],
                &["symbol"],
                &["orderId"],
                &[],
            ),
            "get_prediction_open_order" => (
                "/api/v3/openOrder",
                HttpMethod::Get,
                false,
                &["symbol", "orderId", "origClientOrderId"],
                &["symbol"],
                &["orderId"],
                &[],
            ),
            "get_prediction_open_orders" => (
                "/api/v3/openOrders",
                HttpMethod::Get,
                false,
                &["symbol"],
                &[],
                &[],
                &[],
            ),
            "get_prediction_all_orders" => (
                "/api/v3/allOrders",
                HttpMethod::Get,
                false,
                &["symbol", "orderId", "startTime", "endTime", "limit"],
                &["symbol"],
                &["orderId", "startTime", "endTime", "limit"],
                &[],
            ),
            "create_prediction_asset_wallet_transfer" => (
                "/api/v3/asset/wallet/transfer",
                HttpMethod::Post,
                false,
                &["amount", "asset", "clientTranId", "kindType"],
                &["amount", "asset", "clientTranId", "kindType"],
                &[],
                &["amount"],
            ),
            "create_prediction_mint" => (
                "/api/v3/prediction/mint",
                HttpMethod::Post,
                false,
                &["symbol", "quantity", "newClientOrderId"],
                &["symbol", "quantity"],
                &[],
                &["quantity"],
            ),
            "create_prediction_burn" => (
                "/api/v3/prediction/burn",
                HttpMethod::Post,
                false,
                &["symbol", "quantity", "newClientOrderId"],
                &["symbol", "quantity"],
                &[],
                &["quantity"],
            ),
            "create_prediction_split" => (
                "/api/v3/prediction/split",
                HttpMethod::Post,
                false,
                &["event", "symbol", "quantity", "newClientOrderId"],
                &["event", "symbol", "quantity"],
                &[],
                &["quantity"],
            ),
            "create_prediction_merge" => (
                "/api/v3/prediction/merge",
                HttpMethod::Post,
                false,
                &["event", "quantity", "newClientOrderId"],
                &["event", "quantity"],
                &[],
                &["quantity"],
            ),
            "get_prediction_positions" => (
                "/api/v3/prediction/positions",
                HttpMethod::Get,
                false,
                &["symbol"],
                &[],
                &[],
                &[],
            ),
            "get_prediction_position_histories" => (
                "/api/v3/prediction/positionHistories",
                HttpMethod::Get,
                false,
                &["symbol", "startTime", "endTime", "limit"],
                &[],
                &["startTime", "endTime", "limit"],
                &[],
            ),
            "get_prediction_settlement_histories" => (
                "/api/v3/prediction/settlementHistories",
                HttpMethod::Get,
                false,
                &["symbol", "startTime", "endTime", "limit"],
                &[],
                &["startTime", "endTime", "limit"],
                &[],
            ),
            "get_prediction_account" => (
                "/api/v3/account",
                HttpMethod::Get,
                false,
                &[],
                &[],
                &[],
                &[],
            ),
            "get_prediction_user_trades" => (
                "/api/v3/userTrades",
                HttpMethod::Get,
                false,
                &[
                    "symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "fromId",
                    "limit",
                ],
                &[],
                &["orderId", "startTime", "endTime", "fromId", "limit"],
                &[],
            ),
            "create_prediction_listen_key" => (
                "/api/v3/listenKey",
                HttpMethod::Post,
                false,
                &[],
                &[],
                &[],
                &[],
            ),
            "update_prediction_listen_key" => (
                "/api/v3/listenKey",
                HttpMethod::Put,
                false,
                &["listenKey"],
                &["listenKey"],
                &[],
                &[],
            ),
            "cancel_prediction_listen_key" => (
                "/api/v3/listenKey",
                HttpMethod::Delete,
                false,
                &["listenKey"],
                &["listenKey"],
                &[],
                &[],
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
        for key in integers {
            if p.get(key).is_some() {
                p.required_u64_range(key, if *key == "limit" { 1 } else { 0 }, u64::MAX)?;
            }
        }
        for key in decimals {
            if let Some(v) = p.get(key) {
                if !v.parse::<f64>().is_ok_and(|n| n.is_finite() && n > 0.0) {
                    return Err(DcexError::InvalidInput(format!("{key} must be positive")));
                }
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
        if let (Some(a), Some(b)) = (p.get("startTime"), p.get("endTime")) {
            if a.parse::<u64>().unwrap() > b.parse::<u64>().unwrap() {
                return Err(DcexError::InvalidInput("startTime exceeds endTime".into()));
            }
        }
        if matches!(
            name,
            "get_prediction_position_histories" | "get_prediction_settlement_histories"
        ) {
            if p.get("limit").is_some() {
                p.required_u64_range("limit", 1, 1000)?;
            }
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
