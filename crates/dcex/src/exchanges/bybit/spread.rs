use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{BybitParams, insert_optional_string};

impl BybitClient {
    pub(super) async fn spread_public_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, query) = match method_name {
            "get_spread_instruments" => {
                params.ensure_allowed(&["symbol", "baseCoin", "limit", "cursor"])?;
                limit(params, 500)?;
                (
                    SPREAD_INSTRUMENTS,
                    params.only(&["symbol", "baseCoin", "limit", "cursor"]),
                )
            }
            "get_spread_orderbook" => {
                params.ensure_allowed(&["symbol", "limit"])?;
                nonempty(params, "symbol")?;
                limit(params, 25)?;
                (SPREAD_ORDERBOOK, params.only(&["symbol", "limit"]))
            }
            "get_spread_tickers" => {
                params.ensure_allowed(&["symbol"])?;
                nonempty(params, "symbol")?;
                (SPREAD_TICKERS, params.only(&["symbol"]))
            }
            "get_spread_recent_trades" => {
                params.ensure_allowed(&["symbol", "limit"])?;
                nonempty(params, "symbol")?;
                limit(params, 1000)?;
                (SPREAD_RECENT_TRADES, params.only(&["symbol", "limit"]))
            }
            _ => return Ok(None),
        };
        Ok(Some(
            self.request(HttpMethod::Get, path, query, None, false)
                .await?,
        ))
    }

    pub(super) async fn spread_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_spread_order" => {
                params.ensure_allowed(&[
                    "orderType",
                    "symbol",
                    "side",
                    "qty",
                    "price",
                    "timeInForce",
                    "orderLinkId",
                ])?;
                nonempty(params, "symbol")?;
                choice(params, "side", &["Buy", "Sell"])?;
                choice(params, "orderType", &["Limit", "Market"])?;
                positive(params, "qty")?;
                if params.get("orderType") == Some("Limit") {
                    nonempty(params, "price")?;
                }
                choice_optional(params, "timeInForce", &["IOC", "FOK", "GTC", "PostOnly"])?;
                let mut body = Map::new();
                for key in [
                    "symbol",
                    "side",
                    "orderType",
                    "qty",
                    "price",
                    "orderLinkId",
                    "timeInForce",
                ] {
                    insert_optional_string(&mut body, key, params.get(key));
                }
                self.post_request(SPREAD_CREATE_ORDER, body).await
            }
            "amend_spread_order" => {
                params.ensure_allowed(&["qty", "price", "symbol", "orderId", "orderLinkId"])?;
                nonempty(params, "symbol")?;
                one_identifier(params)?;
                if params.get("qty").is_none() && params.get("price").is_none() {
                    return Err(DcexError::InvalidInput(
                        "Bybit spread amendment requires qty or price".into(),
                    ));
                }
                if params.get("qty").is_some() {
                    positive(params, "qty")?;
                }
                let mut body = Map::new();
                for key in ["symbol", "orderId", "orderLinkId", "qty", "price"] {
                    insert_optional_string(&mut body, key, params.get(key));
                }
                self.post_request(SPREAD_AMEND_ORDER, body).await
            }
            "cancel_spread_order" => {
                params.ensure_allowed(&["orderId", "orderLinkId"])?;
                one_identifier(params)?;
                let mut body = Map::new();
                for key in ["orderId", "orderLinkId"] {
                    insert_optional_string(&mut body, key, params.get(key));
                }
                self.post_request(SPREAD_CANCEL_ORDER, body).await
            }
            "cancel_all_spread_orders" => {
                params.ensure_allowed(&["symbol", "cancelAll"])?;
                let mut body = Map::new();
                insert_optional_string(&mut body, "symbol", params.get("symbol"));
                if let Some(cancel_all) = params.get("cancelAll") {
                    let value = cancel_all.parse::<bool>().map_err(|_| {
                        DcexError::InvalidInput(
                            "Bybit spread cancelAll must be true or false".into(),
                        )
                    })?;
                    body.insert("cancelAll".into(), Value::Bool(value));
                }
                if params.get("symbol").is_none()
                    && body.get("cancelAll") != Some(&Value::Bool(true))
                {
                    return Err(DcexError::InvalidInput(
                        "Bybit spread cancel-all requires symbol or cancelAll=true".into(),
                    ));
                }
                self.post_request(SPREAD_CANCEL_ALL_ORDERS, body).await
            }
            "get_spread_open_orders" | "get_spread_order_history" | "get_spread_trade_history" => {
                params.ensure_allowed(&["limit"])?;
                if let Some(limit) = params.get("limit") {
                    let limit = limit.parse::<u64>().map_err(|_| {
                        DcexError::InvalidInput("Bybit spread limit must be an integer".into())
                    })?;
                    if !(1..=50).contains(&limit) {
                        return Err(DcexError::InvalidInput(
                            "Bybit spread limit must be from 1 to 50".into(),
                        ));
                    }
                }
                let fields = match method_name {
                    "get_spread_open_orders" => &[
                        "symbol",
                        "baseCoin",
                        "orderId",
                        "orderLinkId",
                        "limit",
                        "cursor",
                    ][..],
                    "get_spread_order_history" => &[
                        "symbol",
                        "baseCoin",
                        "orderId",
                        "orderLinkId",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ][..],
                    _ => &[
                        "symbol",
                        "orderId",
                        "orderLinkId",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ][..],
                };
                let path = match method_name {
                    "get_spread_open_orders" => SPREAD_OPEN_ORDERS,
                    "get_spread_order_history" => SPREAD_ORDER_HISTORY,
                    _ => SPREAD_TRADE_HISTORY,
                };
                self.get_request(path, params.only(fields)).await
            }
            "get_spread_max_qty" => {
                params.ensure_allowed(&["symbol", "side", "orderPrice"])?;
                nonempty(params, "symbol")?;
                choice(params, "side", &["1", "2"])?;
                nonempty(params, "orderPrice")?;
                self.get_request(
                    SPREAD_MAX_QTY,
                    params.only(&["symbol", "side", "orderPrice"]),
                )
                .await
            }
            _ => return Ok(None),
        };
        result.map(Some)
    }
}

fn limit(params: &BybitParams, maximum: u64) -> Result<()> {
    if let Some(value) = params.get("limit") {
        let limit = value
            .parse::<u64>()
            .map_err(|_| DcexError::InvalidInput("Bybit spread limit must be an integer".into()))?;
        if !(1..=maximum).contains(&limit) {
            return Err(DcexError::InvalidInput(format!(
                "Bybit spread limit must be from 1 to {maximum}"
            )));
        }
    }
    Ok(())
}

fn nonempty<'a>(params: &'a BybitParams, key: &str) -> Result<&'a str> {
    params
        .get(key)
        .filter(|value| !value.trim().is_empty())
        .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
}

fn choice(params: &BybitParams, key: &str, allowed: &[&str]) -> Result<()> {
    let value = nonempty(params, key)?;
    if allowed.contains(&value) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(format!(
            "unsupported Bybit spread {key}: {value}"
        )))
    }
}

fn choice_optional(params: &BybitParams, key: &str, allowed: &[&str]) -> Result<()> {
    if params.get(key).is_some() {
        choice(params, key, allowed)?;
    }
    Ok(())
}

fn one_identifier(params: &BybitParams) -> Result<()> {
    let count = ["orderId", "orderLinkId"]
        .iter()
        .filter(|key| {
            params
                .get(key)
                .is_some_and(|value| !value.trim().is_empty())
        })
        .count();
    if count == 1 {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "Bybit spread requires exactly one of orderId or orderLinkId".into(),
        ))
    }
}

fn positive(params: &BybitParams, key: &str) -> Result<()> {
    let value = nonempty(params, key)?;
    if value
        .parse::<f64>()
        .is_ok_and(|number| number.is_finite() && number > 0.0)
    {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(format!(
            "Bybit spread {key} must be positive"
        )))
    }
}

#[cfg(test)]
mod tests {
    use std::{
        io::{Read, Write},
        net::TcpListener,
        thread,
        time::Duration,
    };

    use super::*;

    fn server() -> (String, thread::JoinHandle<String>) {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
        let address = listener.local_addr().expect("address");
        let handle = thread::spawn(move || {
            let (mut stream, _) = listener.accept().expect("accept");
            let mut buffer = [0u8; 4096];
            let size = stream.read(&mut buffer).expect("read");
            let mut request = String::from_utf8_lossy(&buffer[..size]).into_owned();
            let content_length = request
                .lines()
                .find_map(|line| {
                    line.to_ascii_lowercase()
                        .strip_prefix("content-length: ")
                        .and_then(|value| value.trim().parse::<usize>().ok())
                })
                .unwrap_or(0);
            while request.split("\r\n\r\n").nth(1).map_or(0, str::len) < content_length {
                let size = stream.read(&mut buffer).expect("read body");
                assert!(size > 0);
                request.push_str(&String::from_utf8_lossy(&buffer[..size]));
            }
            let body = r#"{"retCode":0,"retMsg":"OK","result":{}}"#;
            let response = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                body.len(),
                body
            );
            stream.write_all(response.as_bytes()).expect("write");
            request
        });
        (format!("http://{address}"), handle)
    }

    #[tokio::test]
    async fn place_spread_order_uses_signed_combo_symbol() {
        let (base_url, handle) = server();
        let client = BybitClient::with_base_url(
            Some("key".into()),
            Some("secret".into()),
            5000,
            false,
            Duration::from_secs(10),
            base_url,
        )
        .expect("client");
        client
            .place_spread_order("SOLUSDT_SOL/USDT", "Buy", "Limit", "0.1")
            .price("21")
            .await
            .expect("response");
        let request = handle.join().expect("server");
        assert!(request.starts_with("POST /v5/spread/order/create HTTP/1.1"));
        assert!(request.to_ascii_lowercase().contains("x-bapi-sign:"));
        let body: serde_json::Value =
            serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
        assert_eq!(body["symbol"], "SOLUSDT_SOL/USDT");
        assert_eq!(body["side"], "Buy");
        assert_eq!(body["price"], "21");
    }

    #[tokio::test]
    async fn spread_max_qty_uses_signed_risk_route() {
        let (base_url, handle) = server();
        let client = BybitClient::with_base_url(
            Some("key".into()),
            Some("secret".into()),
            5000,
            false,
            Duration::from_secs(10),
            base_url,
        )
        .expect("client");
        client
            .get_spread_max_qty("SOLUSDT_SOL/USDT", "1", "21")
            .await
            .expect("response");
        let request = handle.join().expect("server");
        assert!(request.starts_with("GET /v5/spread/max-qty?"));
        assert!(request.contains("symbol=SOLUSDT_SOL%2FUSDT"));
        assert!(request.contains("side=1"));
    }

    #[tokio::test]
    async fn spread_orderbook_uses_public_route_and_encoded_combo_symbol() {
        let (base_url, handle) = server();
        let client =
            BybitClient::with_base_url(None, None, 5000, false, Duration::from_secs(10), base_url)
                .expect("client");
        client
            .get_spread_orderbook("SOLUSDT_SOL/USDT")
            .limit(25)
            .await
            .expect("response");
        let request = handle.join().expect("server");
        assert!(request.starts_with("GET /v5/spread/orderbook?"));
        assert!(request.contains("symbol=SOLUSDT_SOL%2FUSDT"));
        assert!(request.contains("limit=25"));
    }

    #[tokio::test]
    async fn spread_orderbook_rejects_excessive_depth() {
        let client = BybitClient::public(5000, false, Duration::from_secs(1)).expect("client");
        let error = client
            .get_spread_orderbook("SOLUSDT_SOL/USDT")
            .limit(26)
            .await
            .expect_err("limit");
        assert!(error.to_string().contains("25"));
    }

    #[tokio::test]
    async fn spread_cancel_requires_identifier_before_network() {
        let client = BybitClient::public(5000, false, Duration::from_secs(1)).expect("client");
        let error = client.cancel_spread_order().await.expect_err("identifier");
        assert!(error.to_string().contains("orderId"));
    }
}
