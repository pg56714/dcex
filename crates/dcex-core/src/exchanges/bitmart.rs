use std::time::Duration;

use serde_json::Value;

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const SPOT_BASE_URL: &str = "https://api-cloud.bitmart.com";
const FUTURES_BASE_URL: &str = "https://api-cloud-v2.bitmart.com";
const SPOT_CURRENCIES: &str = "/spot/v1/currencies";
const SPOT_SYMBOLS: &str = "/spot/v1/symbols";
const SPOT_SYMBOL_DETAILS: &str = "/spot/v1/symbols/details";
const SPOT_TICKERS: &str = "/spot/quotation/v3/tickers";
const SPOT_TICKER: &str = "/spot/quotation/v3/ticker";
const SPOT_KLINE: &str = "/spot/quotation/v3/lite-klines";
const FUTURES_CONTRACT_DETAILS: &str = "/contract/public/details";
const FUTURES_DEPTH: &str = "/contract/public/depth";
const FUTURES_KLINE: &str = "/contract/public/kline";
const FUTURES_FUNDING_RATE: &str = "/contract/public/funding-rate";
const FUTURES_FUNDING_RATE_HISTORY: &str = "/contract/public/funding-rate-history";
const FUTURES_OPEN_INTEREST: &str = "/contract/public/open-interest";
const FUTURES_MARK_PRICE_KLINE: &str = "/contract/public/markprice-kline";
const FUTURES_LEVERAGE_BRACKET: &str = "/contract/public/leverage-bracket";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BitmartMarket {
    Futures,
    Spot,
}

#[derive(Clone)]
pub struct BitmartClient {
    transport: AsyncHttpClient,
    spot_base_url: String,
    futures_base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    memo: Option<String>,
}

impl BitmartClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        memo: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_urls(
            api_key,
            api_secret,
            memo,
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
        )
    }

    pub fn with_base_urls(
        api_key: Option<String>,
        api_secret: Option<String>,
        memo: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            spot_base_url,
            futures_base_url,
            api_key,
            api_secret,
            memo,
        })
    }

    pub async fn request(
        &self,
        method: HttpMethod,
        market: BitmartMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, market, path, params, body, signed)
            .await?;
        let data = validate_response(&response)?;
        Ok(ValidatedResponse {
            status: response.status,
            headers: response.headers,
            data,
        })
    }

    pub async fn request_raw(
        &self,
        method: HttpMethod,
        market: BitmartMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let timestamp = unix_timestamp_ms()?;
        let request = self.build_request(method, market, path, params, body, signed, timestamp)?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        market: BitmartMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, market, path, params, body, signed)
                .await
        })
    }

    pub async fn get_spot_currencies(&self) -> Result<ValidatedResponse> {
        self.public_get(BitmartMarket::Spot, SPOT_CURRENCIES, Vec::new())
            .await
    }

    pub async fn get_trading_pairs(&self) -> Result<ValidatedResponse> {
        self.public_get(BitmartMarket::Spot, SPOT_SYMBOLS, Vec::new())
            .await
    }

    pub async fn get_trading_pairs_details(&self) -> Result<ValidatedResponse> {
        self.public_get(BitmartMarket::Spot, SPOT_SYMBOL_DETAILS, Vec::new())
            .await
    }

    pub async fn get_ticker_of_all_pairs(&self) -> Result<ValidatedResponse> {
        self.public_get(BitmartMarket::Spot, SPOT_TICKERS, Vec::new())
            .await
    }

    pub async fn get_ticker_of_a_pair(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.public_get(
            BitmartMarket::Spot,
            SPOT_TICKER,
            vec![("symbol".to_string(), exchange_symbol(product_symbol, true))],
        )
        .await
    }

    pub async fn get_spot_kline(
        &self,
        product_symbol: &str,
        interval: &str,
        before: Option<&str>,
        after: Option<&str>,
        limit: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("symbol".to_string(), exchange_symbol(product_symbol, true)),
            ("step".to_string(), bitmart_timeframe(interval)?.to_string()),
        ];
        push_optional(&mut params, "before", before);
        push_optional(&mut params, "after", after);
        push_optional(&mut params, "limit", limit);
        self.public_get(BitmartMarket::Spot, SPOT_KLINE, params)
            .await
    }

    pub async fn get_contracts_details(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            BitmartMarket::Futures,
            FUTURES_CONTRACT_DETAILS,
            optional_symbol_params(product_symbol, false),
        )
        .await
    }

    pub async fn get_depth(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.futures_symbol_get(FUTURES_DEPTH, product_symbol).await
    }

    pub async fn get_contract_kline(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: &str,
        end_time: &str,
    ) -> Result<ValidatedResponse> {
        self.futures_kline_get(
            FUTURES_KLINE,
            product_symbol,
            interval,
            start_time,
            end_time,
        )
        .await
    }

    pub async fn get_open_interest(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.futures_symbol_get(FUTURES_OPEN_INTEREST, product_symbol)
            .await
    }

    pub async fn get_mark_price_kline(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: &str,
        end_time: &str,
    ) -> Result<ValidatedResponse> {
        self.futures_kline_get(
            FUTURES_MARK_PRICE_KLINE,
            product_symbol,
            interval,
            start_time,
            end_time,
        )
        .await
    }

    pub async fn get_leverage_bracket(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.futures_symbol_get(FUTURES_LEVERAGE_BRACKET, product_symbol)
            .await
    }

    pub async fn get_current_funding_rate(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.futures_symbol_get(FUTURES_FUNDING_RATE, product_symbol)
            .await
    }

    pub async fn get_funding_rate_history(
        &self,
        product_symbol: &str,
        limit: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), exchange_symbol(product_symbol, false))];
        push_optional(&mut params, "limit", limit);
        self.public_get(BitmartMarket::Futures, FUTURES_FUNDING_RATE_HISTORY, params)
            .await
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = PublicParams(params);
        match method_name {
            "get_spot_currencies" => self.get_spot_currencies().await,
            "get_trading_pairs" => self.get_trading_pairs().await,
            "get_trading_pairs_details" => self.get_trading_pairs_details().await,
            "get_ticker_of_all_pairs" => self.get_ticker_of_all_pairs().await,
            "get_ticker_of_a_pair" => {
                self.get_ticker_of_a_pair(params.required("product_symbol")?)
                    .await
            }
            "get_spot_kline" => {
                self.get_spot_kline(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.get("before"),
                    params.get("after"),
                    params.get("limit"),
                )
                .await
            }
            "get_contracts_details" => {
                self.get_contracts_details(params.get("product_symbol"))
                    .await
            }
            "get_depth" => self.get_depth(params.required("product_symbol")?).await,
            "get_contract_kline" => {
                self.get_contract_kline(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.required("start_time")?,
                    params.required("end_time")?,
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
                    params.required("start_time")?,
                    params.required("end_time")?,
                )
                .await
            }
            "get_leverage_bracket" => {
                self.get_leverage_bracket(params.required("product_symbol")?)
                    .await
            }
            "get_current_funding_rate" => {
                self.get_current_funding_rate(params.required("product_symbol")?)
                    .await
            }
            "get_funding_rate_history" => {
                self.get_funding_rate_history(
                    params.required("product_symbol")?,
                    params.get("limit"),
                )
                .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported BitMart public method: {method_name}"
            ))),
        }
    }

    async fn futures_symbol_get(
        &self,
        path: &str,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            BitmartMarket::Futures,
            path,
            vec![("symbol".to_string(), exchange_symbol(product_symbol, false))],
        )
        .await
    }

    async fn futures_kline_get(
        &self,
        path: &str,
        product_symbol: &str,
        interval: &str,
        start_time: &str,
        end_time: &str,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            BitmartMarket::Futures,
            path,
            vec![
                ("symbol".to_string(), exchange_symbol(product_symbol, false)),
                ("step".to_string(), bitmart_timeframe(interval)?.to_string()),
                ("start_time".to_string(), start_time.to_string()),
                ("end_time".to_string(), end_time.to_string()),
            ],
        )
        .await
    }

    async fn public_get(
        &self,
        market: BitmartMarket,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, market, path, params, None, false)
            .await
    }

    fn build_request(
        &self,
        method: HttpMethod,
        market: BitmartMarket,
        path: impl Into<String>,
        mut params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        timestamp: u64,
    ) -> Result<HttpRequest> {
        let base_url = match market {
            BitmartMarket::Futures => &self.futures_base_url,
            BitmartMarket::Spot => &self.spot_base_url,
        };
        params.sort_by(|left, right| left.0.cmp(&right.0));
        let path = path.into();
        let path = if matches!(method, HttpMethod::Get) && !params.is_empty() {
            format!(
                "{path}?{}",
                params
                    .iter()
                    .map(|(key, value)| format!("{key}={value}"))
                    .collect::<Vec<_>>()
                    .join("&")
            )
        } else {
            path
        };
        let mut request =
            HttpRequest::new(method, base_url, path).header("Content-Type", "application/json");
        if matches!(method, HttpMethod::Post) {
            request.body = body.clone().map(RequestBody::Raw).unwrap_or_default();
        }
        if signed {
            let (api_key, api_secret, memo) = self.credentials()?;
            let body = String::from_utf8_lossy(body.as_deref().unwrap_or_default());
            let payload = format!("{timestamp}#{memo}#{body}");
            let signature = hmac_sha256_hex(api_secret.as_bytes(), payload.as_bytes())?;
            request
                .headers
                .insert("X-BM-KEY".to_string(), api_key.to_string());
            request.headers.insert("X-BM-SIGN".to_string(), signature);
            request
                .headers
                .insert("X-BM-TIMESTAMP".to_string(), timestamp.to_string());
            request
                .headers
                .insert("X-BM-MEMO".to_string(), memo.to_string());
        }
        Ok(request)
    }

    fn credentials(&self) -> Result<(&str, &str, &str)> {
        match (&self.api_key, &self.api_secret, &self.memo) {
            (Some(api_key), Some(api_secret), Some(memo)) => Ok((api_key, api_secret, memo)),
            _ => Err(DcexError::InvalidInput(
                "Signed request requires API Key and Secret and Memo.".to_string(),
            )),
        }
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
}

fn optional_symbol_params(product_symbol: Option<&str>, spot: bool) -> Vec<(String, String)> {
    product_symbol
        .map(|product_symbol| vec![("symbol".to_string(), exchange_symbol(product_symbol, spot))])
        .unwrap_or_default()
}

fn push_optional(params: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
}

fn exchange_symbol(product_symbol: &str, spot: bool) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) if spot => format!("{base}_{quote}"),
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{quote}"),
        _ => product_symbol.to_string(),
    }
}

fn bitmart_timeframe(timeframe: &str) -> Result<u32> {
    match timeframe {
        "1m" => Ok(1),
        "5m" => Ok(5),
        "15m" => Ok(15),
        "30m" => Ok(30),
        "1h" => Ok(60),
        "2h" => Ok(120),
        "4h" => Ok(240),
        "1d" => Ok(1440),
        "1w" => Ok(10080),
        "1M" => Ok(43200),
        _ => Err(DcexError::InvalidInput(
            "timeframe not supported".to_string(),
        )),
    }
}

fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    let code = data
        .as_object()
        .and_then(|object| object.get("code"))
        .map(json_value_string)
        .unwrap_or_else(|| "0".to_string());
    if code != "1000" {
        let message = data
            .as_object()
            .and_then(|object| object.get("msg").or_else(|| object.get("message")))
            .and_then(Value::as_str)
            .unwrap_or("Unknown error");
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("BitMart API Error: [{code}] {message}"),
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
    fn signed_post_uses_exact_body() {
        let client = BitmartClient::new(
            Some("api-key".to_string()),
            Some("test_api_secret_0000".to_string()),
            Some("test_memo".to_string()),
            Duration::from_secs(1),
        )
        .expect("client");
        let body = br#"{"symbol":"BTCUSDT"}"#.to_vec();
        let request = client
            .build_request(
                HttpMethod::Post,
                BitmartMarket::Spot,
                "/spot/v2/submit_order",
                Vec::new(),
                Some(body.clone()),
                true,
                1_700_000_000_000,
            )
            .expect("request");

        assert_eq!(
            request.headers.get("X-BM-SIGN").map(String::as_str),
            Some("a5a38bab707890a577d96959ca82a1b7a4c0db7ffd9b40ba17b20ad57932a542")
        );
        assert_eq!(request.body, RequestBody::Raw(body));
    }
}
