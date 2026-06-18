use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use crate::ethereum::{keccak256, recoverable_sign};
use crate::exchange::ValidatedResponse;
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};
use serde_json::Value;

const SPOT_BASE_URL: &str = "https://sapi.asterdex.com";
const FUTURES_BASE_URL: &str = "https://fapi.asterdex.com";
const SPOT_PING: &str = "/api/v3/ping";
const SPOT_SERVER_TIME: &str = "/api/v3/time";
const SPOT_EXCHANGE_INFO: &str = "/api/v3/exchangeInfo";
const SPOT_DEPTH: &str = "/api/v3/depth";
const SPOT_TRADES: &str = "/api/v3/trades";
const SPOT_HISTORICAL_TRADES: &str = "/api/v3/historicalTrades";
const SPOT_AGG_TRADES: &str = "/api/v3/aggTrades";
const SPOT_KLINES: &str = "/api/v3/klines";
const SPOT_TICKER_24HR: &str = "/api/v3/ticker/24hr";
const SPOT_TICKER_PRICE: &str = "/api/v3/ticker/price";
const SPOT_BOOK_TICKER: &str = "/api/v3/ticker/bookTicker";
const SPOT_WITHDRAW_FEE: &str = "/api/v3/aster/withdraw/estimateFee";
const FUTURES_PING: &str = "/fapi/v3/ping";
const FUTURES_SERVER_TIME: &str = "/fapi/v3/time";
const FUTURES_EXCHANGE_INFO: &str = "/fapi/v3/exchangeInfo";
const FUTURES_DEPTH: &str = "/fapi/v3/depth";
const FUTURES_TRADES: &str = "/fapi/v3/trades";
const FUTURES_HISTORICAL_TRADES: &str = "/fapi/v3/historicalTrades";
const FUTURES_AGG_TRADES: &str = "/fapi/v3/aggTrades";
const FUTURES_KLINES: &str = "/fapi/v3/klines";
const FUTURES_INDEX_PRICE_KLINES: &str = "/fapi/v3/indexPriceKlines";
const FUTURES_MARK_PRICE_KLINES: &str = "/fapi/v3/markPriceKlines";
const FUTURES_PREMIUM_INDEX: &str = "/fapi/v3/premiumIndex";
const FUTURES_FUNDING_RATE: &str = "/fapi/v3/fundingRate";
const FUTURES_FUNDING_INFO: &str = "/fapi/v3/fundingInfo";
const FUTURES_TICKER_24HR: &str = "/fapi/v3/ticker/24hr";
const FUTURES_TICKER_PRICE: &str = "/fapi/v3/ticker/price";
const FUTURES_BOOK_TICKER: &str = "/fapi/v3/ticker/bookTicker";
const FUTURES_INDEX_REFERENCES: &str = "/fapi/v3/indexreferences";
const DOMAIN_NAME: &str = "AsterSignTransaction";
const DOMAIN_VERSION: &str = "1";
const DOMAIN_CHAIN_ID: u64 = 1666;
const DOMAIN_TYPE: &str =
    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)";
const MESSAGE_TYPE: &str = "Message(string msg)";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AsterMarket {
    Futures,
    Spot,
}

#[derive(Clone)]
pub struct AsterClient {
    transport: AsyncHttpClient,
    spot_base_url: String,
    futures_base_url: String,
    user_address: Option<String>,
    signer_address: Option<String>,
    private_key: Option<[u8; 32]>,
    last_nonce: Arc<AtomicU64>,
}

impl AsterClient {
    pub fn new(
        user_address: Option<String>,
        signer_address: Option<String>,
        private_key: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_urls(
            user_address,
            signer_address,
            private_key,
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
        )
    }

    pub fn with_base_urls(
        user_address: Option<String>,
        signer_address: Option<String>,
        private_key: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            spot_base_url,
            futures_base_url,
            user_address,
            signer_address,
            private_key: private_key.map(|key| parse_private_key(&key)).transpose()?,
            last_nonce: Arc::new(AtomicU64::new(0)),
        })
    }

    pub async fn request(
        &self,
        method: HttpMethod,
        market: AsterMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, market, path, params, signed)
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
        market: AsterMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let request = self.build_request(method, market, path, params, signed, None)?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        market: AsterMarket,
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

    fn build_request(
        &self,
        method: HttpMethod,
        market: AsterMarket,
        path: impl Into<String>,
        mut params: Vec<(String, String)>,
        signed: bool,
        nonce: Option<u64>,
    ) -> Result<HttpRequest> {
        if !matches!(
            method,
            HttpMethod::Get | HttpMethod::Post | HttpMethod::Put | HttpMethod::Delete
        ) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Aster HTTP method: {}",
                http_method_name(method)
            )));
        }
        if signed {
            let signer_address = self.signer_address.as_deref().ok_or_else(|| {
                DcexError::InvalidInput(
                    "Signed Aster requests require signer_address and private_key.".to_string(),
                )
            })?;
            let private_key = self.private_key.as_ref().ok_or_else(|| {
                DcexError::InvalidInput(
                    "Signed Aster requests require signer_address and private_key.".to_string(),
                )
            })?;
            if market == AsterMarket::Futures {
                let user_address = self.user_address.as_deref().ok_or_else(|| {
                    DcexError::InvalidInput(
                        "Signed Aster futures requests require user_address.".to_string(),
                    )
                })?;
                params.push((
                    "nonce".to_string(),
                    nonce.unwrap_or_else(|| self.next_nonce()).to_string(),
                ));
                params.push(("user".to_string(), user_address.to_string()));
            } else {
                params.push((
                    "nonce".to_string(),
                    nonce.unwrap_or_else(|| self.next_nonce()).to_string(),
                ));
            }
            params.push(("signer".to_string(), signer_address.to_string()));
            let message = encode_params(&params);
            params.push((
                "signature".to_string(),
                sign_message(&message, private_key)?,
            ));
        }

        let base_url = match market {
            AsterMarket::Futures => &self.futures_base_url,
            AsterMarket::Spot => &self.spot_base_url,
        };
        let path = path.into();
        let encoded = encode_params(&params);
        let mut request =
            HttpRequest::new(method, base_url, &path).header("Accept", "application/json");
        if method == HttpMethod::Get {
            if !encoded.is_empty() {
                request.path = format!("{path}?{encoded}");
            }
        } else {
            request.headers.insert(
                "Content-Type".to_string(),
                "application/x-www-form-urlencoded".to_string(),
            );
            if !encoded.is_empty() {
                request.body = RequestBody::Raw(encoded.into_bytes());
            }
        }
        Ok(request)
    }

    fn next_nonce(&self) -> u64 {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system time after epoch")
            .as_nanos()
            / 1_000;
        let now = u64::try_from(now).unwrap_or(u64::MAX);
        self.last_nonce
            .fetch_update(Ordering::Relaxed, Ordering::Relaxed, |previous| {
                Some(now.max(previous.saturating_add(1)))
            })
            .map(|previous| now.max(previous.saturating_add(1)))
            .unwrap_or(now)
    }

    pub async fn ping_spot(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Spot,
            SPOT_PING,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn ping_futures(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Futures,
            FUTURES_PING,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn get_spot_server_time(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Spot,
            SPOT_SERVER_TIME,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn get_futures_server_time(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Futures,
            FUTURES_SERVER_TIME,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn get_spot_exchange_info(
        &self,
        product_symbol: Option<&str>,
        symbols: Option<Vec<String>>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), exchange_symbol(product_symbol)));
        }
        if let Some(symbols) = symbols {
            params.push((
                "symbols".to_string(),
                serde_json::to_string(&symbols)
                    .map_err(|error| DcexError::Decode(error.to_string()))?,
            ));
        }
        self.request(
            HttpMethod::Get,
            AsterMarket::Spot,
            SPOT_EXCHANGE_INFO,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_exchange_info(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Futures,
            FUTURES_EXCHANGE_INFO,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn get_spot_orderbook(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Spot, SPOT_DEPTH, product_symbol, limit)
            .await
    }

    pub async fn get_futures_orderbook(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Futures, FUTURES_DEPTH, product_symbol, limit)
            .await
    }

    pub async fn get_spot_recent_trades(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Spot, SPOT_TRADES, product_symbol, limit)
            .await
    }

    pub async fn get_futures_recent_trades(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Futures, FUTURES_TRADES, product_symbol, limit)
            .await
    }

    pub async fn get_spot_historical_trades(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
        from_id: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.historical_trades_request(
            AsterMarket::Spot,
            SPOT_HISTORICAL_TRADES,
            product_symbol,
            limit,
            from_id,
        )
        .await
    }

    pub async fn get_futures_historical_trades(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
        from_id: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.historical_trades_request(
            AsterMarket::Futures,
            FUTURES_HISTORICAL_TRADES,
            product_symbol,
            limit,
            from_id,
        )
        .await
    }

    pub async fn get_spot_agg_trades(
        &self,
        product_symbol: &str,
        from_id: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.agg_trades_request(
            AsterMarket::Spot,
            SPOT_AGG_TRADES,
            product_symbol,
            from_id,
            start_time,
            end_time,
            limit,
        )
        .await
    }

    pub async fn get_futures_agg_trades(
        &self,
        product_symbol: &str,
        from_id: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.agg_trades_request(
            AsterMarket::Futures,
            FUTURES_AGG_TRADES,
            product_symbol,
            from_id,
            start_time,
            end_time,
            limit,
        )
        .await
    }

    pub async fn get_spot_klines(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.klines_request(
            AsterMarket::Spot,
            SPOT_KLINES,
            product_symbol,
            interval,
            start_time,
            end_time,
            limit,
        )
        .await
    }

    pub async fn get_futures_klines(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.klines_request(
            AsterMarket::Futures,
            FUTURES_KLINES,
            product_symbol,
            interval,
            start_time,
            end_time,
            limit,
        )
        .await
    }

    pub async fn get_futures_index_price_klines(
        &self,
        pair: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("pair".to_string(), pair.to_string()),
            ("interval".to_string(), interval.to_string()),
        ];
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "limit", limit);
        self.request(
            HttpMethod::Get,
            AsterMarket::Futures,
            FUTURES_INDEX_PRICE_KLINES,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_mark_price_klines(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.klines_request(
            AsterMarket::Futures,
            FUTURES_MARK_PRICE_KLINES,
            product_symbol,
            interval,
            start_time,
            end_time,
            limit,
        )
        .await
    }

    pub async fn get_spot_ticker_24hr(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_TICKER_24HR, product_symbol)
            .await
    }

    pub async fn get_futures_ticker_24hr(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_TICKER_24HR, product_symbol)
            .await
    }

    pub async fn get_spot_ticker_price(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_TICKER_PRICE, product_symbol)
            .await
    }

    pub async fn get_futures_ticker_price(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_TICKER_PRICE, product_symbol)
            .await
    }

    pub async fn get_spot_book_ticker(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_BOOK_TICKER, product_symbol)
            .await
    }

    pub async fn get_futures_book_ticker(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_BOOK_TICKER, product_symbol)
            .await
    }

    pub async fn get_spot_withdraw_fee(
        &self,
        chain_id: &str,
        asset: &str,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Spot,
            SPOT_WITHDRAW_FEE,
            vec![
                ("chainId".to_string(), chain_id.to_string()),
                ("asset".to_string(), asset.to_string()),
            ],
            false,
        )
        .await
    }

    pub async fn get_futures_premium_index(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_PREMIUM_INDEX, product_symbol)
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
            AsterMarket::Futures,
            FUTURES_FUNDING_RATE,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_funding_info(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_FUNDING_INFO, product_symbol)
            .await
    }

    pub async fn get_futures_index_references(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Futures,
            FUTURES_INDEX_REFERENCES,
            vec![("symbol".to_string(), exchange_symbol(product_symbol))],
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
            "ping_spot" => self.ping_spot().await,
            "ping_futures" => self.ping_futures().await,
            "get_spot_server_time" => self.get_spot_server_time().await,
            "get_futures_server_time" => self.get_futures_server_time().await,
            "get_spot_exchange_info" => {
                self.get_spot_exchange_info(params.get("product_symbol"), params.values("symbols"))
                    .await
            }
            "get_futures_exchange_info" => self.get_futures_exchange_info().await,
            "get_spot_orderbook" => {
                self.get_spot_orderbook(params.required("product_symbol")?, params.u64("limit")?)
                    .await
            }
            "get_futures_orderbook" => {
                self.get_futures_orderbook(params.required("product_symbol")?, params.u64("limit")?)
                    .await
            }
            "get_spot_recent_trades" => {
                self.get_spot_recent_trades(
                    params.required("product_symbol")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_recent_trades" => {
                self.get_futures_recent_trades(
                    params.required("product_symbol")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_spot_historical_trades" => {
                self.get_spot_historical_trades(
                    params.required("product_symbol")?,
                    params.u64("limit")?,
                    params.u64("fromId")?,
                )
                .await
            }
            "get_futures_historical_trades" => {
                self.get_futures_historical_trades(
                    params.required("product_symbol")?,
                    params.u64("limit")?,
                    params.u64("fromId")?,
                )
                .await
            }
            "get_spot_agg_trades" => {
                self.get_spot_agg_trades(
                    params.required("product_symbol")?,
                    params.u64("fromId")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_agg_trades" => {
                self.get_futures_agg_trades(
                    params.required("product_symbol")?,
                    params.u64("fromId")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_spot_klines" => {
                self.get_spot_klines(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_klines" => {
                self.get_futures_klines(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_index_price_klines" => {
                self.get_futures_index_price_klines(
                    params.required("pair")?,
                    params.required("interval")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_mark_price_klines" => {
                self.get_futures_mark_price_klines(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_spot_ticker_24hr" => {
                self.get_spot_ticker_24hr(params.get("product_symbol"))
                    .await
            }
            "get_futures_ticker_24hr" => {
                self.get_futures_ticker_24hr(params.get("product_symbol"))
                    .await
            }
            "get_spot_ticker_price" => {
                self.get_spot_ticker_price(params.get("product_symbol"))
                    .await
            }
            "get_futures_ticker_price" => {
                self.get_futures_ticker_price(params.get("product_symbol"))
                    .await
            }
            "get_spot_book_ticker" => {
                self.get_spot_book_ticker(params.get("product_symbol"))
                    .await
            }
            "get_futures_book_ticker" => {
                self.get_futures_book_ticker(params.get("product_symbol"))
                    .await
            }
            "get_spot_withdraw_fee" => {
                self.get_spot_withdraw_fee(params.required("chainId")?, params.required("asset")?)
                    .await
            }
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
            "get_futures_funding_info" => {
                self.get_futures_funding_info(params.get("product_symbol"))
                    .await
            }
            "get_futures_index_references" => {
                self.get_futures_index_references(params.required("product_symbol")?)
                    .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Aster public method: {method_name}"
            ))),
        }
    }

    async fn optional_symbol_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), exchange_symbol(product_symbol)));
        }
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    async fn symbol_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), exchange_symbol(product_symbol))];
        push_optional_display(&mut params, "limit", limit);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    async fn historical_trades_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: &str,
        limit: Option<u64>,
        from_id: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), exchange_symbol(product_symbol))];
        push_optional_display(&mut params, "limit", limit);
        push_optional_display(&mut params, "fromId", from_id);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    async fn agg_trades_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: &str,
        from_id: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), exchange_symbol(product_symbol))];
        push_optional_display(&mut params, "fromId", from_id);
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "limit", limit);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    async fn klines_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("symbol".to_string(), exchange_symbol(product_symbol)),
            ("interval".to_string(), interval.to_string()),
        ];
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "limit", limit);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
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

pub fn sign_message(message: &str, private_key: &[u8; 32]) -> Result<String> {
    let digest = eip712_digest(message);
    let mut signature = recoverable_sign(&digest, private_key)?;
    signature[64] += 27;
    Ok(format!("0x{}", hex::encode(signature)))
}

fn eip712_digest(message: &str) -> [u8; 32] {
    let mut domain = Vec::with_capacity(160);
    domain.extend_from_slice(&keccak256(DOMAIN_TYPE.as_bytes()));
    domain.extend_from_slice(&keccak256(DOMAIN_NAME.as_bytes()));
    domain.extend_from_slice(&keccak256(DOMAIN_VERSION.as_bytes()));
    let mut chain_id = [0u8; 32];
    chain_id[24..].copy_from_slice(&DOMAIN_CHAIN_ID.to_be_bytes());
    domain.extend_from_slice(&chain_id);
    domain.extend_from_slice(&[0u8; 32]);
    let domain_separator = keccak256(&domain);

    let mut message_struct = Vec::with_capacity(64);
    message_struct.extend_from_slice(&keccak256(MESSAGE_TYPE.as_bytes()));
    message_struct.extend_from_slice(&keccak256(message.as_bytes()));
    let message_hash = keccak256(&message_struct);

    let mut digest = Vec::with_capacity(66);
    digest.extend_from_slice(b"\x19\x01");
    digest.extend_from_slice(&domain_separator);
    digest.extend_from_slice(&message_hash);
    keccak256(&digest)
}

fn parse_private_key(private_key: &str) -> Result<[u8; 32]> {
    let normalized = private_key.strip_prefix("0x").unwrap_or(private_key);
    let bytes = hex::decode(normalized)
        .map_err(|error| DcexError::InvalidInput(format!("invalid Aster private key: {error}")))?;
    bytes.try_into().map_err(|bytes: Vec<u8>| {
        DcexError::InvalidInput(format!(
            "Aster private key must contain 32 bytes, got {}",
            bytes.len()
        ))
    })
}

fn encode_params(params: &[(String, String)]) -> String {
    url::form_urlencoded::Serializer::new(String::new())
        .extend_pairs(
            params
                .iter()
                .map(|(key, value)| (key.as_str(), value.as_str())),
        )
        .finish()
}

fn exchange_symbol(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{quote}"),
        _ => product_symbol.to_string(),
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

fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    response.ensure_success()?;
    if let Some(object) = data.as_object() {
        let code = object.get("code");
        if code.is_some_and(|code| !matches!(json_value_string(code).as_str(), "0" | "200")) {
            let message = object
                .get("msg")
                .or_else(|| object.get("message"))
                .and_then(Value::as_str)
                .unwrap_or("Unknown error");
            return Err(DcexError::HttpStatus {
                status: response.status,
                message: format!(
                    "Aster API error [{}]: {message}",
                    code.map(json_value_string)
                        .unwrap_or_else(|| "null".to_string())
                ),
                headers: response
                    .headers
                    .iter()
                    .map(|(key, value)| (key.clone(), value.clone()))
                    .collect(),
            });
        }
    }
    Ok(data)
}

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}

const fn http_method_name(method: HttpMethod) -> &'static str {
    match method {
        HttpMethod::Delete => "DELETE",
        HttpMethod::Get => "GET",
        HttpMethod::Patch => "PATCH",
        HttpMethod::Post => "POST",
        HttpMethod::Put => "PUT",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn eip712_signature_matches_python_vector() {
        let message = "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001\
&nonce=1700000000000000&signer=0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a";
        assert_eq!(
            sign_message(message, &[0x11; 32]).expect("signature"),
            "0x3ca64e9c82501b8f15cd31348beaaf1aa6636cbba5fb2bc8d1bccf8ee2ffd310\
1a3724dfa8fd2f36de42d3a641b95599d0d4dee5ffb9010eb33b44784d3f60191c"
        );
    }
}
