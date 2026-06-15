use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;
use url::form_urlencoded;

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{ExchangeHttpClient, RequestSigner, ResponseValidator, ValidatedResponse};
use crate::http::{block_on, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const SPOT_BASE_URL: &str = "https://api.binance.com";
const FUTURES_BASE_URL: &str = "https://fapi.binance.com";
const SPOT_SERVER_TIME: &str = "/api/v3/time";
const SPOT_EXCHANGE_INFO: &str = "/api/v3/exchangeInfo";
const SPOT_ORDERBOOK: &str = "/api/v3/depth";
const SPOT_TRADES: &str = "/api/v3/trades";
const SPOT_KLINES: &str = "/api/v3/klines";
const SPOT_PRICE: &str = "/api/v3/ticker/price";
const FUTURES_SERVER_TIME: &str = "/fapi/v1/time";
const FUTURES_EXCHANGE_INFO: &str = "/fapi/v1/exchangeInfo";
const FUTURES_BOOK_TICKER: &str = "/fapi/v1/ticker/bookTicker";
const FUTURES_KLINES: &str = "/fapi/v1/klines";
const FUTURES_PREMIUM_INDEX: &str = "/fapi/v1/premiumIndex";
const FUTURES_FUNDING_RATE_HISTORY: &str = "/fapi/v1/fundingRate";
const FUTURES_OPEN_INTEREST: &str = "/fapi/v1/openInterest";
const FUTURES_OPEN_INTEREST_HISTORY: &str = "/futures/data/openInterestHist";
const FUTURES_GLOBAL_LONG_SHORT_ACCOUNT_RATIO: &str = "/futures/data/globalLongShortAccountRatio";
const FUTURES_TOP_LONG_SHORT_ACCOUNT_RATIO: &str = "/futures/data/topLongShortAccountRatio";
const FUTURES_TOP_LONG_SHORT_POSITION_RATIO: &str = "/futures/data/topLongShortPositionRatio";
const FUTURES_TAKER_LONG_SHORT_RATIO: &str = "/futures/data/takerlongshortRatio";
const FUTURES_BASIS: &str = "/futures/data/basis";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BinanceMarket {
    Futures,
    Spot,
}

impl BinanceMarket {
    pub const fn base_url(self) -> &'static str {
        match self {
            Self::Futures => FUTURES_BASE_URL,
            Self::Spot => SPOT_BASE_URL,
        }
    }
}

#[derive(Clone)]
struct BinanceSigner {
    api_key: String,
    api_secret: String,
}

impl RequestSigner for BinanceSigner {
    fn sign(&self, request: &mut HttpRequest, timestamp_ms: u64) -> Result<()> {
        let params = match &mut request.body {
            RequestBody::Empty => &mut request.query,
            RequestBody::Form(params) => params,
            _ => {
                return Err(DcexError::InvalidInput(
                    "Binance signed requests require query or form parameters.".to_string(),
                ));
            }
        };
        params.push(("timestamp".to_string(), timestamp_ms.to_string()));
        params.push(("recvWindow".to_string(), "5000".to_string()));
        let encoded = encode_params(params);
        let signature = hmac_sha256_hex(self.api_secret.as_bytes(), encoded.as_bytes())?;
        params.push(("signature".to_string(), signature));
        request
            .headers
            .insert("X-MBX-APIKEY".to_string(), self.api_key.clone());
        Ok(())
    }
}

struct BinanceResponseValidator;

impl ResponseValidator for BinanceResponseValidator {
    fn validate(&self, response: &HttpResponse) -> Result<Value> {
        let data = response.json()?;
        if let Some(object) = data.as_object() {
            if let Some(code) = object.get("code") {
                if json_value_string(code) != "200" {
                    let message = object
                        .get("msg")
                        .and_then(Value::as_str)
                        .unwrap_or("Unknown error");
                    return Err(DcexError::HttpStatus {
                        status: response.status,
                        message: format!(
                            "BINANCE API Error: [{}] {message}",
                            json_value_string(code)
                        ),
                        headers: response
                            .headers
                            .iter()
                            .map(|(key, value)| (key.clone(), value.clone()))
                            .collect(),
                    });
                }
            }
        }
        response.ensure_success()?;
        Ok(data)
    }
}

#[derive(Clone)]
pub struct BinanceClient {
    inner: ExchangeHttpClient,
    futures_base_url: String,
    spot_base_url: String,
}

impl BinanceClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_urls(
            api_key,
            api_secret,
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
        )
    }

    pub fn with_base_urls(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
    ) -> Result<Self> {
        let mut inner =
            ExchangeHttpClient::new(timeout)?.with_validator(Arc::new(BinanceResponseValidator));
        if let (Some(api_key), Some(api_secret)) = (api_key, api_secret) {
            inner = inner.with_signer(Arc::new(BinanceSigner {
                api_key,
                api_secret,
            }));
        }
        Ok(Self {
            inner,
            futures_base_url,
            spot_base_url,
        })
    }

    pub async fn request(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let request = self.build_request(method, market, path, params);
        self.inner.execute(request, signed).await
    }

    pub async fn request_raw(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let request = self.build_request(method, market, path, params);
        self.inner.execute_raw(request, signed).await
    }

    pub async fn get_server_time(&self, market_type: &str) -> Result<ValidatedResponse> {
        let (market, path) = if market_type == "spot" {
            (BinanceMarket::Spot, SPOT_SERVER_TIME)
        } else {
            (BinanceMarket::Futures, FUTURES_SERVER_TIME)
        };
        self.request(HttpMethod::Get, market, path, Vec::new(), false)
            .await
    }

    pub async fn get_spot_exchange_info(
        &self,
        product_symbol: Option<&str>,
        product_symbols: Option<Vec<String>>,
        symbol_status: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), exchange_symbol(product_symbol)));
        }
        if let Some(product_symbols) = product_symbols {
            let symbols = product_symbols
                .iter()
                .map(|symbol| exchange_symbol(symbol))
                .collect::<Vec<_>>();
            params.push((
                "symbols".to_string(),
                serde_json::to_string(&symbols)
                    .map_err(|error| DcexError::Decode(error.to_string()))?,
            ));
        }
        push_optional(&mut params, "symbolStatus", symbol_status);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            SPOT_EXCHANGE_INFO,
            params,
            false,
        )
        .await
    }

    pub async fn get_spot_orderbook(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), exchange_symbol(product_symbol))];
        push_optional_display(&mut params, "limit", limit);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            SPOT_ORDERBOOK,
            params,
            false,
        )
        .await
    }

    pub async fn get_spot_trades(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), exchange_symbol(product_symbol))];
        push_optional_display(&mut params, "limit", limit);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            SPOT_TRADES,
            params,
            false,
        )
        .await
    }

    pub async fn get_spot_price(
        &self,
        product_symbol: Option<&str>,
        product_symbols: Option<Vec<String>>,
        symbol_status: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), exchange_symbol(product_symbol)));
        }
        if let Some(product_symbols) = product_symbols {
            let symbols = product_symbols
                .iter()
                .map(|symbol| exchange_symbol(symbol))
                .collect::<Vec<_>>();
            params.push((
                "symbols".to_string(),
                serde_json::to_string(&symbols)
                    .map_err(|error| DcexError::Decode(error.to_string()))?,
            ));
        }
        push_optional(&mut params, "symbolStatus", symbol_status);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            SPOT_PRICE,
            params,
            false,
        )
        .await
    }

    pub async fn get_klines(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("symbol".to_string(), exchange_symbol(product_symbol)),
            ("interval".to_string(), interval.to_string()),
        ];
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "limit", limit);
        let market = if is_spot_product_symbol(product_symbol) {
            BinanceMarket::Spot
        } else {
            BinanceMarket::Futures
        };
        let path = if market == BinanceMarket::Spot {
            SPOT_KLINES
        } else {
            FUTURES_KLINES
        };
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    pub async fn get_futures_exchange_info(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_EXCHANGE_INFO,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn get_futures_ticker(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), exchange_symbol(product_symbol)));
        }
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_BOOK_TICKER,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_premium_index(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), exchange_symbol(product_symbol)));
        }
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_PREMIUM_INDEX,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_funding_rate(
        &self,
        product_symbol: Option<&str>,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), exchange_symbol(product_symbol)));
        }
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "limit", limit);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_FUNDING_RATE_HISTORY,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_open_interest(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.futures_symbol_request(FUTURES_OPEN_INTEREST, product_symbol, Vec::new())
            .await
    }

    pub async fn get_futures_open_interest_history(
        &self,
        product_symbol: &str,
        period: &str,
        limit: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.futures_period_request(
            FUTURES_OPEN_INTEREST_HISTORY,
            product_symbol,
            period,
            limit,
            start_time,
            end_time,
        )
        .await
    }

    pub async fn get_futures_global_long_short_account_ratio(
        &self,
        product_symbol: &str,
        period: &str,
        limit: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.futures_period_request(
            FUTURES_GLOBAL_LONG_SHORT_ACCOUNT_RATIO,
            product_symbol,
            period,
            limit,
            start_time,
            end_time,
        )
        .await
    }

    pub async fn get_futures_top_long_short_account_ratio(
        &self,
        product_symbol: &str,
        period: &str,
        limit: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.futures_period_request(
            FUTURES_TOP_LONG_SHORT_ACCOUNT_RATIO,
            product_symbol,
            period,
            limit,
            start_time,
            end_time,
        )
        .await
    }

    pub async fn get_futures_top_long_short_position_ratio(
        &self,
        product_symbol: &str,
        period: &str,
        limit: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.futures_period_request(
            FUTURES_TOP_LONG_SHORT_POSITION_RATIO,
            product_symbol,
            period,
            limit,
            start_time,
            end_time,
        )
        .await
    }

    pub async fn get_futures_taker_buy_sell_volume(
        &self,
        product_symbol: &str,
        period: &str,
        limit: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.futures_period_request(
            FUTURES_TAKER_LONG_SHORT_RATIO,
            product_symbol,
            period,
            limit,
            start_time,
            end_time,
        )
        .await
    }

    pub async fn get_futures_basis(
        &self,
        product_symbol: &str,
        contract_type: &str,
        period: &str,
        limit: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("pair".to_string(), exchange_symbol(product_symbol)),
            ("contractType".to_string(), contract_type.to_string()),
            ("period".to_string(), period.to_string()),
        ];
        push_optional_display(&mut params, "limit", limit);
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_BASIS,
            params,
            false,
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
            "get_server_time" => {
                self.get_server_time(params.get("market_type").unwrap_or("spot"))
                    .await
            }
            "get_spot_exchange_info" => {
                self.get_spot_exchange_info(
                    params.get("product_symbol"),
                    params.values("product_symbols"),
                    params.get("symbolStatus"),
                )
                .await
            }
            "get_spot_orderbook" => {
                self.get_spot_orderbook(params.required("product_symbol")?, params.u64("limit")?)
                    .await
            }
            "get_spot_trades" => {
                self.get_spot_trades(params.required("product_symbol")?, params.u64("limit")?)
                    .await
            }
            "get_spot_price" => {
                self.get_spot_price(
                    params.get("product_symbol"),
                    params.values("product_symbols"),
                    params.get("symbolStatus"),
                )
                .await
            }
            "get_klines" => {
                self.get_klines(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.u64("start_time")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_exchange_info" => self.get_futures_exchange_info().await,
            "get_futures_ticker" => self.get_futures_ticker(params.get("product_symbol")).await,
            "get_futures_premium_index" => {
                self.get_futures_premium_index(params.get("product_symbol"))
                    .await
            }
            "get_futures_funding_rate" => {
                self.get_futures_funding_rate(
                    params.get("product_symbol"),
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_open_interest" => {
                self.get_futures_open_interest(params.required("product_symbol")?)
                    .await
            }
            "get_futures_open_interest_history" => {
                self.get_futures_open_interest_history(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    params.u64("limit")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                )
                .await
            }
            "get_futures_global_long_short_account_ratio" => {
                self.get_futures_global_long_short_account_ratio(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    params.u64("limit")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                )
                .await
            }
            "get_futures_top_long_short_account_ratio" => {
                self.get_futures_top_long_short_account_ratio(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    params.u64("limit")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                )
                .await
            }
            "get_futures_top_long_short_position_ratio" => {
                self.get_futures_top_long_short_position_ratio(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    params.u64("limit")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                )
                .await
            }
            "get_futures_taker_buy_sell_volume" => {
                self.get_futures_taker_buy_sell_volume(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    params.u64("limit")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                )
                .await
            }
            "get_futures_basis" => {
                self.get_futures_basis(
                    params.required("product_symbol")?,
                    params.get("contractType").unwrap_or("PERPETUAL"),
                    params.get("period").unwrap_or("5m"),
                    params.u64("limit")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                )
                .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Binance public method: {method_name}"
            ))),
        }
    }

    fn build_request(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
    ) -> HttpRequest {
        let base_url = match market {
            BinanceMarket::Futures => &self.futures_base_url,
            BinanceMarket::Spot => &self.spot_base_url,
        };
        match method {
            HttpMethod::Get | HttpMethod::Delete => {
                let mut request = HttpRequest::new(method, base_url, path);
                request.query = params;
                request
            }
            HttpMethod::Post | HttpMethod::Put | HttpMethod::Patch => {
                HttpRequest::new(method, base_url, path).form(params)
            }
        }
    }

    pub fn request_blocking(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move { client.request(method, market, path, params, signed).await })
    }

    pub fn get_server_time_blocking(
        &self,
        market_type: impl Into<String>,
    ) -> Result<ValidatedResponse> {
        let client = self.clone();
        let market_type = market_type.into();
        block_on(async move { client.get_server_time(&market_type).await })
    }

    async fn futures_symbol_request(
        &self,
        path: &str,
        product_symbol: &str,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        params.insert(0, ("symbol".to_string(), exchange_symbol(product_symbol)));
        self.request(HttpMethod::Get, BinanceMarket::Futures, path, params, false)
            .await
    }

    async fn futures_period_request(
        &self,
        path: &str,
        product_symbol: &str,
        period: &str,
        limit: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("period".to_string(), period.to_string())];
        push_optional_display(&mut params, "limit", limit);
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        self.futures_symbol_request(path, product_symbol, params)
            .await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, market, path, params, signed)
                .await
        })
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

    fn values(&self, key: &str) -> Option<Vec<String>> {
        let values = self
            .0
            .iter()
            .filter(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.clone())
            .collect::<Vec<_>>();
        if values.is_empty() {
            None
        } else {
            Some(values)
        }
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

fn exchange_symbol(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{quote}"),
        _ => product_symbol.to_string(),
    }
}

fn is_spot_product_symbol(product_symbol: &str) -> bool {
    product_symbol.ends_with("-SPOT")
}

fn push_optional(params: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
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

fn encode_params(params: &[(String, String)]) -> String {
    let mut serializer = form_urlencoded::Serializer::new(String::new());
    serializer.extend_pairs(
        params
            .iter()
            .map(|(key, value)| (key.as_str(), value.as_str())),
    );
    serializer.finish()
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

    #[test]
    fn signer_matches_python_implementation() {
        let signer = BinanceSigner {
            api_key: "api-key".to_string(),
            api_secret: "secret".to_string(),
        };
        let mut request = HttpRequest::new(HttpMethod::Get, SPOT_BASE_URL, "/api/v3/order");
        request.query = vec![
            ("symbol".to_string(), "BTCUSDT".to_string()),
            ("side".to_string(), "BUY".to_string()),
        ];

        signer
            .sign(&mut request, 1_700_000_000_000)
            .expect("signature");

        assert_eq!(
            request.query,
            vec![
                ("symbol".to_string(), "BTCUSDT".to_string()),
                ("side".to_string(), "BUY".to_string()),
                ("timestamp".to_string(), "1700000000000".to_string()),
                ("recvWindow".to_string(), "5000".to_string()),
                (
                    "signature".to_string(),
                    "5858226bd5a361c8dd587d4da2c1d479758c21380d4913cea33235d3f32dd987".to_string(),
                ),
            ]
        );
        assert_eq!(
            request.headers.get("X-MBX-APIKEY").map(String::as_str),
            Some("api-key")
        );
    }
}
