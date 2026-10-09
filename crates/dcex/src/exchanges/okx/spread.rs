use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::OkxClient;
use super::endpoints::*;
use super::params::{OkxParams, require_one};

impl OkxClient {
    pub(super) async fn spread_public_request(
        &self,
        name: &str,
        params: &OkxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, keys) = match name {
            "get_spread_spreads" => (
                SPREAD_SPREADS,
                &["baseCcy", "instId", "sprdId", "state"][..],
            ),
            "get_spread_books" => (SPREAD_BOOKS, &["sprdId", "sz"][..]),
            "get_spread_ticker" => (SPREAD_TICKER, &["sprdId"][..]),
            "get_spread_public_trades" => (SPREAD_PUBLIC_TRADES, &["sprdId"][..]),
            "get_spread_candles" => (
                SPREAD_CANDLES,
                &["sprdId", "bar", "after", "before", "limit"][..],
            ),
            "get_spread_history_candles" => (
                SPREAD_HISTORY_CANDLES,
                &["sprdId", "bar", "after", "before", "limit"][..],
            ),
            _ => return Ok(None),
        };
        params.ensure_allowed(keys)?;
        if matches!(
            name,
            "get_spread_books"
                | "get_spread_ticker"
                | "get_spread_public_trades"
                | "get_spread_candles"
                | "get_spread_history_candles"
        ) {
            params.required("sprdId")?;
        }
        Ok(Some(
            self.request(HttpMethod::Get, path, params.only(keys), None, false)
                .await?,
        ))
    }

    pub(super) async fn spread_private_request(
        &self,
        name: &str,
        params: &OkxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match name {
            "place_spread_order" => {
                params
                    .ensure_allowed(&["sprdId", "side", "ordType", "sz", "px", "clOrdId", "tag"])?;
                params.required("sprdId")?;
                let side = params.required("side")?;
                if !matches!(side, "buy" | "sell") {
                    return Err(DcexError::InvalidInput(
                        "OKX spread side must be buy or sell".into(),
                    ));
                }
                let order_type = params.required("ordType")?;
                if !matches!(order_type, "limit" | "market" | "post_only" | "ioc" | "fok") {
                    return Err(DcexError::InvalidInput(
                        "unsupported OKX spread order type".into(),
                    ));
                }
                positive(params.required("sz")?, "sz")?;
                if order_type != "market" {
                    positive(params.required("px")?, "px")?;
                }
                self.post_request(
                    SPREAD_ORDER,
                    Value::Object(
                        params.body(&["sprdId", "clOrdId", "tag", "side", "ordType", "sz", "px"]),
                    ),
                )
                .await?
            }
            "cancel_spread_order" => {
                params.ensure_allowed(&["ordId", "clOrdId"])?;
                require_one(params, &["ordId", "clOrdId"])?;
                self.post_request(
                    SPREAD_CANCEL_ORDER,
                    Value::Object(params.body(&["ordId", "clOrdId"])),
                )
                .await?
            }
            "cancel_all_spread_orders" => {
                params.ensure_allowed(&["sprdId"])?;
                self.post_request(SPREAD_MASS_CANCEL, Value::Object(params.body(&["sprdId"])))
                    .await?
            }
            "get_spread_order" => {
                params.ensure_allowed(&["ordId", "clOrdId"])?;
                require_one(params, &["ordId", "clOrdId"])?;
                self.get_request(SPREAD_ORDER, params.only(&["ordId", "clOrdId"]))
                    .await?
            }
            "get_spread_orders_pending" => {
                params
                    .ensure_allowed(&["sprdId", "ordType", "state", "beginId", "endId", "limit"])?;
                self.get_request(
                    SPREAD_ORDERS_PENDING,
                    params.only(&["sprdId", "ordType", "state", "beginId", "endId", "limit"]),
                )
                .await?
            }
            "get_spread_orders_history" => {
                params.ensure_allowed(&[
                    "sprdId", "ordType", "state", "beginId", "endId", "begin", "end", "limit",
                ])?;
                self.get_request(
                    SPREAD_ORDERS_HISTORY,
                    params.only(&[
                        "sprdId", "ordType", "state", "beginId", "endId", "begin", "end", "limit",
                    ]),
                )
                .await?
            }
            "set_spread_cancel_all_after" => {
                params.ensure_allowed(&["timeOut"])?;
                let timeout = params.required("timeOut")?.parse::<u16>().map_err(|_| {
                    DcexError::InvalidInput(
                        "OKX spread timeOut must be a nonnegative integer".into(),
                    )
                })?;
                if timeout > 120 {
                    return Err(DcexError::InvalidInput(
                        "OKX spread timeOut must not exceed 120 seconds".into(),
                    ));
                }
                self.post_request(
                    SPREAD_CANCEL_ALL_AFTER,
                    Value::Object(params.body(&["timeOut"])),
                )
                .await?
            }
            "get_spread_trades" => {
                params.ensure_allowed(&[
                    "sprdId", "tradeId", "ordId", "beginId", "endId", "begin", "end", "limit",
                ])?;
                self.get_request(
                    SPREAD_TRADES,
                    params.only(&[
                        "sprdId", "tradeId", "ordId", "beginId", "endId", "begin", "end", "limit",
                    ]),
                )
                .await?
            }
            _ => return Ok(None),
        };
        Ok(Some(response))
    }
}

fn positive(value: &str, key: &str) -> Result<()> {
    if value
        .parse::<f64>()
        .is_ok_and(|number| number.is_finite() && number > 0.0)
    {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(format!(
            "OKX spread {key} must be positive"
        )))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::{
        io::{Read, Write},
        net::TcpListener,
        thread,
        time::Duration,
    };

    fn server() -> (String, thread::JoinHandle<String>) {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
        let address = listener.local_addr().expect("address");
        let handle = thread::spawn(move || {
            let (mut stream, _) = listener.accept().expect("accept");
            let mut buffer = [0u8; 4096];
            let size = stream.read(&mut buffer).expect("read");
            let mut request = String::from_utf8_lossy(&buffer[..size]).into_owned();
            let length = request
                .lines()
                .find_map(|line| {
                    line.to_ascii_lowercase()
                        .strip_prefix("content-length: ")
                        .and_then(|value| value.trim().parse::<usize>().ok())
                })
                .unwrap_or(0);
            while request.split("\r\n\r\n").nth(1).map_or(0, str::len) < length {
                let size = stream.read(&mut buffer).expect("read body");
                assert!(size > 0);
                request.push_str(&String::from_utf8_lossy(&buffer[..size]));
            }
            let body = r#"{"code":"0","msg":"","data":[]}"#;
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
    async fn spread_order_uses_signed_route_and_body() {
        let (base, handle) = server();
        let client = OkxClient::with_base_url(
            Some("key".into()),
            Some("secret".into()),
            Some("pass".into()),
            "0".into(),
            Duration::from_secs(10),
            base,
        )
        .expect("client");
        client
            .place_spread_order("BTC-USDT_BTC-USDT-SWAP", "buy", "limit", "0.1")
            .px("2.5")
            .await
            .expect("response");
        let request = handle.join().expect("server");
        assert!(request.starts_with("POST /api/v5/sprd/order HTTP/1.1"));
        assert!(request.to_ascii_lowercase().contains("ok-access-sign:"));
        let body: Value =
            serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("json");
        assert_eq!(body["sprdId"], "BTC-USDT_BTC-USDT-SWAP");
        assert_eq!(body["px"], "2.5");
    }

    #[tokio::test]
    async fn spread_books_use_public_route() {
        let (base, handle) = server();
        let client =
            OkxClient::with_base_url(None, None, None, "0".into(), Duration::from_secs(10), base)
                .expect("client");
        client
            .get_spread_books("BTC-USDT_BTC-USDT-SWAP")
            .sz("5")
            .await
            .expect("response");
        let request = handle.join().expect("server");
        assert!(request.starts_with("GET /api/v5/sprd/books?"));
        assert!(request.contains("sprdId="));
        assert!(!request.to_ascii_lowercase().contains("ok-access-sign:"));
    }

    #[tokio::test]
    async fn spread_deadman_uses_independent_signed_route() {
        let (base, handle) = server();
        let client = OkxClient::with_base_url(
            Some("key".into()),
            Some("secret".into()),
            Some("pass".into()),
            "0".into(),
            Duration::from_secs(10),
            base,
        )
        .expect("client");
        client
            .set_spread_cancel_all_after("60")
            .await
            .expect("response");
        let request = handle.join().expect("server");
        assert!(request.starts_with("POST /api/v5/sprd/cancel-all-after HTTP/1.1"));
        assert!(request.to_ascii_lowercase().contains("ok-access-sign:"));
        let body: Value =
            serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("json");
        assert_eq!(body["timeOut"], "60");
    }

    #[tokio::test]
    async fn spread_ticker_uses_market_route() {
        let (base, handle) = server();
        let client =
            OkxClient::with_base_url(None, None, None, "0".into(), Duration::from_secs(10), base)
                .expect("client");
        client
            .get_spread_ticker("BTC-USDT_BTC-USDT-SWAP")
            .await
            .expect("response");
        let request = handle.join().expect("server");
        assert!(request.starts_with("GET /api/v5/market/sprd-ticker?"));
    }

    #[tokio::test]
    async fn spread_cancel_needs_order_identifier() {
        let client = OkxClient::public(Duration::from_secs(1)).expect("client");
        let error = client
            .private_request("cancel_spread_order", Vec::new())
            .await
            .expect_err("identifier");
        assert!(error.to_string().contains("ordId"));
    }
}
