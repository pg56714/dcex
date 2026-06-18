use std::sync::Arc;
use std::time::Duration;

use serde_json::{json, Value};

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{ExchangeHttpClient, RequestSigner, ResponseValidator, ValidatedResponse};
use crate::http::{block_on, HttpMethod, HttpRequest, HttpResponse};
use crate::{DcexError, Result};

const BASE_URL: &str = "https://open-api.bingx.com";
const SWAP_INSTRUMENT_INFO: &str = "/openApi/swap/v2/quote/contracts";
const SWAP_ORDERBOOK: &str = "/openApi/swap/v2/quote/depth";
const SWAP_PUBLIC_TRADE: &str = "/openApi/swap/v2/quote/trades";
const SWAP_KLINE: &str = "/openApi/swap/v3/quote/klines";
const SWAP_TICKER: &str = "/openApi/swap/v2/quote/ticker";
const SWAP_OPEN_INTEREST: &str = "/openApi/swap/v2/quote/openInterest";
const SWAP_MARK_PRICE_KLINE: &str = "/openApi/swap/v1/market/markPriceKlines";
const SPOT_SYMBOLS: &str = "/openApi/spot/v1/common/symbols";
const SPOT_ORDERBOOK: &str = "/openApi/spot/v1/market/depth";
const SPOT_ORDERBOOK_V2: &str = "/openApi/spot/v2/market/depth";
const SPOT_PUBLIC_TRADE: &str = "/openApi/spot/v1/market/trades";
const SPOT_KLINE: &str = "/openApi/spot/v1/market/kline";
const SPOT_KLINE_V2: &str = "/openApi/spot/v2/market/kline";
const SPOT_TICKER: &str = "/openApi/spot/v1/ticker/24hr";
const SPOT_BOOK_TICKER: &str = "/openApi/spot/v1/ticker/bookTicker";
const SPOT_PRICE_TICKER: &str = "/openApi/spot/v2/ticker/price";

#[derive(Clone)]
struct BingxSigner {
    api_key: String,
    api_secret: String,
}

impl RequestSigner for BingxSigner {
    fn sign(&self, request: &mut HttpRequest, timestamp_ms: u64) -> Result<()> {
        request.query.sort_by(|left, right| left.0.cmp(&right.0));
        request
            .query
            .push(("timestamp".to_string(), timestamp_ms.to_string()));
        let payload = request
            .query
            .iter()
            .map(|(key, value)| format!("{key}={value}"))
            .collect::<Vec<_>>()
            .join("&");
        let signature = hmac_sha256_hex(self.api_secret.as_bytes(), payload.as_bytes())?;
        request.query.push(("signature".to_string(), signature));
        request
            .headers
            .insert("X-BX-APIKEY".to_string(), self.api_key.clone());
        Ok(())
    }
}

struct BingxResponseValidator;

impl ResponseValidator for BingxResponseValidator {
    fn validate(&self, response: &HttpResponse) -> Result<Value> {
        let data = if response.body.is_empty() {
            json!({"code": 0})
        } else {
            response.json()?
        };
        let code = data
            .as_object()
            .and_then(|object| object.get("code"))
            .map(json_value_string)
            .unwrap_or_else(|| "0".to_string());
        if code != "0" {
            let message = data
                .as_object()
                .and_then(|object| object.get("msg"))
                .and_then(Value::as_str)
                .unwrap_or("Unknown error");
            return Err(DcexError::HttpStatus {
                status: response.status,
                message: format!("BingX API Error: [{code}] {message}"),
                headers: response
                    .headers
                    .iter()
                    .map(|(key, value)| (key.clone(), value.clone()))
                    .collect(),
            });
        }
        response.ensure_success()?;
        Ok(data)
    }
}

#[derive(Clone)]
pub struct BingxClient {
    inner: ExchangeHttpClient,
    base_url: String,
}

impl BingxClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(api_key, api_secret, timeout, BASE_URL.to_string())
    }

    pub fn with_base_url(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        let mut inner =
            ExchangeHttpClient::new(timeout)?.with_validator(Arc::new(BingxResponseValidator));
        if let (Some(api_key), Some(api_secret)) = (api_key, api_secret) {
            inner = inner.with_signer(Arc::new(BingxSigner {
                api_key,
                api_secret,
            }));
        }
        Ok(Self { inner, base_url })
    }

    pub async fn request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
        headers: Vec<(String, String)>,
        json_body: Option<Value>,
    ) -> Result<ValidatedResponse> {
        self.inner
            .execute(
                self.build_request(method, path, params, signed, headers, json_body),
                signed,
            )
            .await
    }

    pub async fn request_raw(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
        headers: Vec<(String, String)>,
        json_body: Option<Value>,
    ) -> Result<HttpResponse> {
        self.inner
            .execute_raw(
                self.build_request(method, path, params, signed, headers, json_body),
                signed,
            )
            .await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
        headers: Vec<(String, String)>,
        json_body: Option<Value>,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, path, params, signed, headers, json_body)
                .await
        })
    }

    pub async fn get_swap_instrument_info(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            SWAP_INSTRUMENT_INFO,
            optional_symbol_params(product_symbol, "symbol"),
        )
        .await
    }

    pub async fn get_spot_instrument_info(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            SPOT_SYMBOLS,
            optional_symbol_params(product_symbol, "symbol"),
        )
        .await
    }

    pub async fn get_orderbook(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            SWAP_ORDERBOOK,
            depth_params(product_symbol, limit, "limit", None),
        )
        .await
    }

    pub async fn get_spot_orderbook(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            SPOT_ORDERBOOK,
            depth_params(product_symbol, limit, "limit", None),
        )
        .await
    }

    pub async fn get_spot_orderbook_v2(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
        type_: &str,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            SPOT_ORDERBOOK_V2,
            depth_params(product_symbol, limit, "depth", Some(type_)),
        )
        .await
    }

    pub async fn get_public_trades(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            SWAP_PUBLIC_TRADE,
            depth_params(product_symbol, limit, "limit", None),
        )
        .await
    }

    pub async fn get_spot_public_trades(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.public_get(
            SPOT_PUBLIC_TRADE,
            vec![("symbol".to_string(), exchange_symbol(product_symbol))],
        )
        .await
    }

    pub async fn get_kline(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            SWAP_KLINE,
            kline_params(product_symbol, interval, start_time, end_time, limit),
        )
        .await
    }

    pub async fn get_spot_kline(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            SPOT_KLINE,
            kline_params(product_symbol, interval, start_time, end_time, limit),
        )
        .await
    }

    pub async fn get_spot_kline_v2(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            SPOT_KLINE_V2,
            kline_params(product_symbol, interval, start_time, end_time, limit),
        )
        .await
    }

    pub async fn get_open_interest(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.public_get(
            SWAP_OPEN_INTEREST,
            vec![("symbol".to_string(), exchange_symbol(product_symbol))],
        )
        .await
    }

    pub async fn get_mark_price_kline(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            SWAP_MARK_PRICE_KLINE,
            kline_params(product_symbol, interval, start_time, end_time, limit),
        )
        .await
    }

    pub async fn get_ticker(&self, product_symbol: Option<&str>) -> Result<ValidatedResponse> {
        self.public_get(
            SWAP_TICKER,
            optional_symbol_params(product_symbol, "symbol"),
        )
        .await
    }

    pub async fn get_spot_ticker(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.public_get(
            SPOT_TICKER,
            vec![("symbol".to_string(), exchange_symbol(product_symbol))],
        )
        .await
    }

    pub async fn get_spot_book_ticker(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.public_get(
            SPOT_BOOK_TICKER,
            vec![("symbol".to_string(), exchange_symbol(product_symbol))],
        )
        .await
    }

    pub async fn get_spot_price_ticker(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.public_get(
            SPOT_PRICE_TICKER,
            vec![("symbol".to_string(), exchange_symbol(product_symbol))],
        )
        .await
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = PublicParams(params);
        match method_name {
            "get_swap_instrument_info" => {
                self.get_swap_instrument_info(params.get("product_symbol"))
                    .await
            }
            "get_spot_instrument_info" => {
                self.get_spot_instrument_info(params.get("product_symbol"))
                    .await
            }
            "get_orderbook" => {
                self.get_orderbook(params.required("product_symbol")?, params.u64("limit")?)
                    .await
            }
            "get_spot_orderbook" => {
                self.get_spot_orderbook(params.required("product_symbol")?, params.u64("limit")?)
                    .await
            }
            "get_spot_orderbook_v2" => {
                self.get_spot_orderbook_v2(
                    params.required("product_symbol")?,
                    params.u64("limit")?,
                    params.get("type_").unwrap_or("step0"),
                )
                .await
            }
            "get_public_trades" => {
                self.get_public_trades(params.required("product_symbol")?, params.u64("limit")?)
                    .await
            }
            "get_spot_public_trades" => {
                self.get_spot_public_trades(params.required("product_symbol")?)
                    .await
            }
            "get_kline" => {
                self.get_kline(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.u64("start_time")?,
                    params.u64("end_time")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_spot_kline" => {
                self.get_spot_kline(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.u64("start_time")?,
                    params.u64("end_time")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_spot_kline_v2" => {
                self.get_spot_kline_v2(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.u64("start_time")?,
                    params.u64("end_time")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_open_interest" => {
                self.get_open_interest(params.required("product_symbol")?)
                    .await
            }
            "get_mark_price_kline" => {
                self.get_mark_price_kline(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.u64("start_time")?,
                    params.u64("end_time")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_ticker" => self.get_ticker(params.get("product_symbol")).await,
            "get_spot_ticker" => {
                self.get_spot_ticker(params.required("product_symbol")?)
                    .await
            }
            "get_spot_book_ticker" => {
                self.get_spot_book_ticker(params.required("product_symbol")?)
                    .await
            }
            "get_spot_price_ticker" => {
                self.get_spot_price_ticker(params.required("product_symbol")?)
                    .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported BingX public method: {method_name}"
            ))),
        }
    }

    async fn public_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            path,
            params,
            false,
            vec![("Content-Type".to_string(), "application/json".to_string())],
            None,
        )
        .await
    }

    fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        mut params: Vec<(String, String)>,
        signed: bool,
        headers: Vec<(String, String)>,
        json_body: Option<Value>,
    ) -> HttpRequest {
        params.sort_by(|left, right| left.0.cmp(&right.0));
        let mut request = HttpRequest::new(method, &self.base_url, path);
        request.headers.extend(headers);
        if signed || matches!(method, HttpMethod::Get | HttpMethod::Delete) {
            request.query = params;
        } else if let Some(json_body) = json_body {
            request = request.json(json_body);
        }
        request
    }
}

struct PublicParams(Vec<(String, String)>);

impl PublicParams {
    fn get(&self, key: &str) -> Option<&str> {
        self.0
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    fn required(&self, key: &str) -> Result<&str> {
        self.get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
    }

    fn u64(&self, key: &str) -> Result<Option<u64>> {
        self.get(key)
            .map(|value| {
                value.parse::<u64>().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
                })
            })
            .transpose()
    }
}

fn optional_symbol_params(product_symbol: Option<&str>, key: &str) -> Vec<(String, String)> {
    product_symbol
        .map(|product_symbol| vec![(key.to_string(), exchange_symbol(product_symbol))])
        .unwrap_or_default()
}

fn depth_params(
    product_symbol: &str,
    limit: Option<u64>,
    limit_key: &str,
    type_: Option<&str>,
) -> Vec<(String, String)> {
    let mut params = vec![("symbol".to_string(), exchange_symbol(product_symbol))];
    if let Some(type_) = type_ {
        params.push(("type".to_string(), type_.to_string()));
    }
    push_optional_display(&mut params, limit_key, limit);
    params
}

fn kline_params(
    product_symbol: &str,
    interval: &str,
    start_time: Option<u64>,
    end_time: Option<u64>,
    limit: Option<u64>,
) -> Vec<(String, String)> {
    let mut params = vec![
        ("symbol".to_string(), exchange_symbol(product_symbol)),
        ("interval".to_string(), interval.to_string()),
    ];
    push_optional_display(&mut params, "startTime", start_time);
    push_optional_display(&mut params, "endTime", end_time);
    push_optional_display(&mut params, "limit", limit);
    params
}

fn push_optional_display<T: ToString>(
    params: &mut Vec<(String, String)>,
    key: &str,
    value: Option<T>,
) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
}

fn exchange_symbol(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}-{quote}"),
        _ => product_symbol.to_string(),
    }
}

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::exchange::RequestSigner;

    #[test]
    fn signer_uses_unescaped_sorted_payload() {
        let signer = BingxSigner {
            api_key: "api-key".to_string(),
            api_secret: "secret".to_string(),
        };
        let mut request = HttpRequest::new(HttpMethod::Get, BASE_URL, "/test");
        request.query = vec![
            ("symbol".to_string(), "BTC USDT".to_string()),
            ("limit".to_string(), "10".to_string()),
        ];

        signer
            .sign(&mut request, 1_700_000_000_000)
            .expect("signature");

        assert_eq!(
            request.query,
            vec![
                ("limit".to_string(), "10".to_string()),
                ("symbol".to_string(), "BTC USDT".to_string()),
                ("timestamp".to_string(), "1700000000000".to_string()),
                (
                    "signature".to_string(),
                    "19a79f275d914021036bb65476f48319ed590bc5f26de3e0f8e6b3aa6bb31e1f".to_string(),
                ),
            ]
        );
        assert_eq!(
            request.headers.get("X-BX-APIKEY").map(String::as_str),
            Some("api-key")
        );
    }
}
