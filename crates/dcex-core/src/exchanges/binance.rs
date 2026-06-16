use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;
use url::form_urlencoded;

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{ExchangeHttpClient, RequestSigner, ResponseValidator, ValidatedResponse};
use crate::http::{block_on, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
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
const SPOT_ACCOUNT_BALANCE: &str = "/api/v3/account";
const WALLET_BALANCE: &str = "/sapi/v1/asset/wallet/balance";
const FUNDING_WALLET: &str = "/sapi/v1/asset/get-funding-asset";
const UNIVERSAL_TRANSFER: &str = "/sapi/v1/asset/transfer";
const FUTURES_ACCOUNT_BALANCE: &str = "/fapi/v3/balance";
const FUTURES_ACCOUNT_INFO: &str = "/fapi/v3/account";
const FUTURES_INCOME_HISTORY: &str = "/fapi/v1/income";
const FUTURES_USER_DATA_STREAM: &str = "/fapi/v1/listenKey";
const SPOT_ORDER: &str = "/api/v3/order";
const SPOT_TEST_ORDER: &str = "/api/v3/order/test";
const SPOT_OPEN_ORDERS: &str = "/api/v3/openOrders";
const SPOT_ALL_ORDERS: &str = "/api/v3/allOrders";
const SPOT_ACCOUNT_TRADES: &str = "/api/v3/myTrades";
const FUTURES_LEVERAGE: &str = "/fapi/v1/leverage";
const FUTURES_ORDER: &str = "/fapi/v1/order";
const FUTURES_TEST_ORDER: &str = "/fapi/v1/order/test";
const FUTURES_CANCEL_ALL_OPEN_ORDERS: &str = "/fapi/v1/allOpenOrders";
const FUTURES_ALL_ORDERS: &str = "/fapi/v1/allOrders";
const FUTURES_OPEN_ORDER: &str = "/fapi/v1/openOrder";
const FUTURES_OPEN_ORDERS: &str = "/fapi/v1/openOrders";
const FUTURES_ALGO_ORDER: &str = "/fapi/v1/algoOrder";
const FUTURES_CANCEL_ALL_OPEN_ALGO_ORDERS: &str = "/fapi/v1/algoOpenOrders";
const FUTURES_OPEN_ALGO_ORDERS: &str = "/fapi/v1/openAlgoOrders";
const FUTURES_ALL_ALGO_ORDERS: &str = "/fapi/v1/allAlgoOrders";
const FUTURES_ACCOUNT_TRADES: &str = "/fapi/v1/userTrades";
const FUTURES_POSITION_INFO: &str = "/fapi/v3/positionRisk";

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
    api_key: Option<String>,
    product_table: Option<Arc<ProductTable>>,
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
        let api_key_header = api_key.clone();
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
            api_key: api_key_header,
            product_table: None,
        })
    }

    pub fn with_product_table(mut self, product_table: ProductTable) -> Self {
        self.product_table = Some(Arc::new(product_table));
        self
    }

    pub fn set_product_table(&mut self, product_table: ProductTable) {
        self.product_table = Some(Arc::new(product_table));
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
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        if let Some(product_symbols) = product_symbols {
            let symbols = product_symbols
                .iter()
                .map(|symbol| self.exchange_symbol(symbol))
                .collect::<Result<Vec<_>>>()?;
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
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
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
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
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
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        if let Some(product_symbols) = product_symbols {
            let symbols = product_symbols
                .iter()
                .map(|symbol| self.exchange_symbol(symbol))
                .collect::<Result<Vec<_>>>()?;
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
            ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
            ("interval".to_string(), interval.to_string()),
        ];
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "limit", limit);
        let market = self.market_for_product_symbol(product_symbol)?;
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
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
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
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
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
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
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
            ("pair".to_string(), self.exchange_symbol(product_symbol)?),
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

    pub async fn get_account_balance(&self, market_type: &str) -> Result<ValidatedResponse> {
        let (market, path) = if market_type == "spot" {
            (BinanceMarket::Spot, SPOT_ACCOUNT_BALANCE)
        } else {
            (BinanceMarket::Futures, FUTURES_ACCOUNT_BALANCE)
        };
        self.request(HttpMethod::Get, market, path, Vec::new(), true)
            .await
    }

    pub async fn get_income_history(
        &self,
        product_symbol: Option<&str>,
        income_type: Option<&str>,
        start_time: Option<u64>,
        end_time: Option<u64>,
        page: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        push_optional(&mut params, "incomeType", income_type);
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "page", page);
        push_optional_display(&mut params, "limit", limit);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_INCOME_HISTORY,
            params,
            true,
        )
        .await
    }

    pub async fn get_futures_account_info(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_ACCOUNT_INFO,
            Vec::new(),
            true,
        )
        .await
    }

    pub async fn get_wallet_balance(&self, quote_asset: Option<&str>) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        push_optional(&mut params, "quoteAsset", quote_asset);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            WALLET_BALANCE,
            params,
            true,
        )
        .await
    }

    pub async fn get_funding_wallet(
        &self,
        asset: Option<&str>,
        need_btc_valuation: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        push_optional(&mut params, "asset", asset);
        push_optional(&mut params, "needBtcValuation", need_btc_valuation);
        self.request(
            HttpMethod::Post,
            BinanceMarket::Spot,
            FUNDING_WALLET,
            params,
            true,
        )
        .await
    }

    pub async fn create_universal_transfer(
        &self,
        transfer_type: &str,
        asset: &str,
        amount: &str,
        from_symbol: Option<&str>,
        to_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("type".to_string(), transfer_type.to_string()),
            ("asset".to_string(), asset.to_string()),
            ("amount".to_string(), amount.to_string()),
        ];
        push_optional(&mut params, "fromSymbol", from_symbol);
        push_optional(&mut params, "toSymbol", to_symbol);
        self.request(
            HttpMethod::Post,
            BinanceMarket::Spot,
            UNIVERSAL_TRANSFER,
            params,
            true,
        )
        .await
    }

    pub async fn get_universal_transfer_history(
        &self,
        transfer_type: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        current: Option<u64>,
        size: Option<u64>,
        from_symbol: Option<&str>,
        to_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("type".to_string(), transfer_type.to_string())];
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "current", current);
        push_optional_display(&mut params, "size", size);
        push_optional(&mut params, "fromSymbol", from_symbol);
        push_optional(&mut params, "toSymbol", to_symbol);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            UNIVERSAL_TRANSFER,
            params,
            true,
        )
        .await
    }

    pub async fn create_futures_listen_key(&self) -> Result<ValidatedResponse> {
        self.api_key_request(
            HttpMethod::Post,
            BinanceMarket::Futures,
            FUTURES_USER_DATA_STREAM,
            Vec::new(),
        )
        .await
    }

    pub async fn keep_alive_futures_listen_key(
        &self,
        listen_key: &str,
    ) -> Result<ValidatedResponse> {
        self.api_key_request(
            HttpMethod::Put,
            BinanceMarket::Futures,
            FUTURES_USER_DATA_STREAM,
            vec![("listenKey".to_string(), listen_key.to_string())],
        )
        .await
    }

    pub async fn close_futures_listen_key(&self, listen_key: &str) -> Result<ValidatedResponse> {
        self.api_key_request(
            HttpMethod::Delete,
            BinanceMarket::Futures,
            FUTURES_USER_DATA_STREAM,
            vec![("listenKey".to_string(), listen_key.to_string())],
        )
        .await
    }

    pub async fn get_listen_key(&self, market_type: &str) -> Result<ValidatedResponse> {
        ensure_futures_listen_key_market(market_type)?;
        self.create_futures_listen_key().await
    }

    pub async fn keep_alive_listen_key(
        &self,
        listen_key: &str,
        market_type: &str,
    ) -> Result<ValidatedResponse> {
        ensure_futures_listen_key_market(market_type)?;
        self.keep_alive_futures_listen_key(listen_key).await
    }

    pub async fn close_listen_key(
        &self,
        listen_key: &str,
        market_type: &str,
    ) -> Result<ValidatedResponse> {
        ensure_futures_listen_key_market(market_type)?;
        self.close_futures_listen_key(listen_key).await
    }

    pub async fn set_leverage(
        &self,
        product_symbol: &str,
        leverage: &str,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Post,
            BinanceMarket::Futures,
            FUTURES_LEVERAGE,
            vec![
                ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
                ("leverage".to_string(), leverage.to_string()),
            ],
            true,
        )
        .await
    }

    pub async fn place_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
        extra_params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.order_request(
            HttpMethod::Post,
            product_symbol,
            false,
            side,
            order_type,
            extra_params,
        )
        .await
    }

    pub async fn test_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
        extra_params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.order_request(
            HttpMethod::Post,
            product_symbol,
            true,
            side,
            order_type,
            extra_params,
        )
        .await
    }

    pub async fn place_futures_algo_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
        algo_type: &str,
        extra_params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("algoType".to_string(), algo_type.to_string()),
            ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
            ("side".to_string(), normalize_order_side(side)?),
            ("type".to_string(), order_type.to_string()),
        ];
        params.extend(extra_params);
        self.request(
            HttpMethod::Post,
            BinanceMarket::Futures,
            FUTURES_ALGO_ORDER,
            params,
            true,
        )
        .await
    }

    pub async fn cancel_futures_algo_order(
        &self,
        algo_id: Option<&str>,
        client_algo_id: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.futures_algo_order_request(HttpMethod::Delete, algo_id, client_algo_id)
            .await
    }

    pub async fn get_futures_algo_order(
        &self,
        algo_id: Option<&str>,
        client_algo_id: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.futures_algo_order_request(HttpMethod::Get, algo_id, client_algo_id)
            .await
    }

    pub async fn get_all_open_futures_algo_orders(
        &self,
        product_symbol: Option<&str>,
        algo_type: Option<&str>,
        algo_id: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        push_optional(&mut params, "algoType", algo_type);
        push_optional(&mut params, "algoId", algo_id);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_OPEN_ALGO_ORDERS,
            params,
            true,
        )
        .await
    }

    pub async fn get_all_futures_algo_orders(
        &self,
        product_symbol: &str,
        algo_id: Option<&str>,
        start_time: Option<&str>,
        end_time: Option<&str>,
        limit: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional(&mut params, "algoId", algo_id);
        push_optional(&mut params, "startTime", start_time);
        push_optional(&mut params, "endTime", end_time);
        push_optional(&mut params, "limit", limit);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_ALL_ALGO_ORDERS,
            params,
            true,
        )
        .await
    }

    pub async fn cancel_all_open_futures_algo_orders(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Delete,
            BinanceMarket::Futures,
            FUTURES_CANCEL_ALL_OPEN_ALGO_ORDERS,
            vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)],
            true,
        )
        .await
    }

    pub async fn place_market_order(
        &self,
        product_symbol: &str,
        side: &str,
        quantity: &str,
        position_side: Option<&str>,
        reduce_only: Option<&str>,
        new_order_resp_type: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("quantity".to_string(), quantity.to_string())];
        push_optional(&mut params, "positionSide", position_side);
        push_optional(&mut params, "reduceOnly", reduce_only);
        push_optional(&mut params, "newOrderRespType", new_order_resp_type);
        self.place_order(product_symbol, side, "MARKET", params)
            .await
    }

    pub async fn place_market_buy_order(
        &self,
        product_symbol: &str,
        quantity: &str,
        position_side: Option<&str>,
        reduce_only: Option<&str>,
        new_order_resp_type: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.place_market_order(
            product_symbol,
            "BUY",
            quantity,
            position_side,
            reduce_only,
            new_order_resp_type,
        )
        .await
    }

    pub async fn place_market_sell_order(
        &self,
        product_symbol: &str,
        quantity: &str,
        position_side: Option<&str>,
        reduce_only: Option<&str>,
        new_order_resp_type: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.place_market_order(
            product_symbol,
            "SELL",
            quantity,
            position_side,
            reduce_only,
            new_order_resp_type,
        )
        .await
    }

    pub async fn place_limit_order(
        &self,
        product_symbol: &str,
        side: &str,
        quantity: &str,
        price: &str,
        time_in_force: &str,
        position_side: Option<&str>,
        reduce_only: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("quantity".to_string(), quantity.to_string()),
            ("price".to_string(), price.to_string()),
            ("timeInForce".to_string(), time_in_force.to_string()),
        ];
        push_optional(&mut params, "positionSide", position_side);
        push_optional(&mut params, "reduceOnly", reduce_only);
        self.place_order(product_symbol, side, "LIMIT", params)
            .await
    }

    pub async fn place_limit_buy_order(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
        time_in_force: &str,
        position_side: Option<&str>,
        reduce_only: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.place_limit_order(
            product_symbol,
            "BUY",
            quantity,
            price,
            time_in_force,
            position_side,
            reduce_only,
        )
        .await
    }

    pub async fn place_limit_sell_order(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
        time_in_force: &str,
        position_side: Option<&str>,
        reduce_only: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.place_limit_order(
            product_symbol,
            "SELL",
            quantity,
            price,
            time_in_force,
            position_side,
            reduce_only,
        )
        .await
    }

    pub async fn place_post_only_limit_order(
        &self,
        product_symbol: &str,
        side: &str,
        quantity: &str,
        price: &str,
        position_side: Option<&str>,
        reduce_only: Option<&str>,
    ) -> Result<ValidatedResponse> {
        if self.market_for_product_symbol(product_symbol)? == BinanceMarket::Spot {
            self.place_order(
                product_symbol,
                side,
                "LIMIT_MAKER",
                vec![
                    ("quantity".to_string(), quantity.to_string()),
                    ("price".to_string(), price.to_string()),
                ],
            )
            .await
        } else {
            self.place_limit_order(
                product_symbol,
                side,
                quantity,
                price,
                "GTX",
                position_side,
                reduce_only,
            )
            .await
        }
    }

    pub async fn place_post_only_limit_buy_order(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
        position_side: Option<&str>,
        reduce_only: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.place_post_only_limit_order(
            product_symbol,
            "BUY",
            quantity,
            price,
            position_side,
            reduce_only,
        )
        .await
    }

    pub async fn place_post_only_limit_sell_order(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
        position_side: Option<&str>,
        reduce_only: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.place_post_only_limit_order(
            product_symbol,
            "SELL",
            quantity,
            price,
            position_side,
            reduce_only,
        )
        .await
    }

    pub async fn cancel_order(
        &self,
        product_symbol: &str,
        order_id: Option<&str>,
        orig_client_order_id: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.order_lookup_request(
            HttpMethod::Delete,
            product_symbol,
            order_id,
            orig_client_order_id,
        )
        .await
    }

    pub async fn get_order(
        &self,
        product_symbol: &str,
        order_id: Option<&str>,
        orig_client_order_id: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.order_lookup_request(
            HttpMethod::Get,
            product_symbol,
            order_id,
            orig_client_order_id,
        )
        .await
    }

    pub async fn get_open_orders(
        &self,
        product_symbol: &str,
        order_id: Option<&str>,
        orig_client_order_id: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        let path = if market == BinanceMarket::Spot {
            SPOT_OPEN_ORDERS
        } else if order_id.is_some() || orig_client_order_id.is_some() {
            push_optional(&mut params, "orderId", order_id);
            push_optional(&mut params, "origClientOrderId", orig_client_order_id);
            FUTURES_OPEN_ORDER
        } else {
            FUTURES_OPEN_ORDERS
        };
        self.request(HttpMethod::Get, market, path, params, true)
            .await
    }

    pub async fn get_all_open_orders(
        &self,
        product_symbol: Option<&str>,
        market_type: &str,
    ) -> Result<ValidatedResponse> {
        let market = if let Some(product_symbol) = product_symbol {
            self.market_for_product_symbol(product_symbol)?
        } else {
            market_from_type(market_type)
        };
        let path = if market == BinanceMarket::Spot {
            SPOT_OPEN_ORDERS
        } else {
            FUTURES_OPEN_ORDERS
        };
        let params = if let Some(product_symbol) = product_symbol {
            vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)]
        } else {
            Vec::new()
        };
        self.request(HttpMethod::Get, market, path, params, true)
            .await
    }

    pub async fn cancel_all_open_orders(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let path = if market == BinanceMarket::Spot {
            SPOT_OPEN_ORDERS
        } else {
            FUTURES_CANCEL_ALL_OPEN_ORDERS
        };
        self.request(
            HttpMethod::Delete,
            market,
            path,
            vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)],
            true,
        )
        .await
    }

    pub async fn get_future_all_order(
        &self,
        product_symbol: &str,
        order_id: Option<&str>,
        start_time: Option<&str>,
        end_time: Option<&str>,
        limit: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.get_all_orders(product_symbol, order_id, start_time, end_time, limit)
            .await
    }

    pub async fn get_all_orders(
        &self,
        product_symbol: &str,
        order_id: Option<&str>,
        start_time: Option<&str>,
        end_time: Option<&str>,
        limit: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let path = if market == BinanceMarket::Spot {
            SPOT_ALL_ORDERS
        } else {
            FUTURES_ALL_ORDERS
        };
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional(&mut params, "orderId", order_id);
        push_optional(&mut params, "startTime", start_time);
        push_optional(&mut params, "endTime", end_time);
        push_optional(&mut params, "limit", limit);
        self.request(HttpMethod::Get, market, path, params, true)
            .await
    }

    pub async fn get_account_trades(
        &self,
        product_symbol: &str,
        order_id: Option<&str>,
        start_time: Option<&str>,
        end_time: Option<&str>,
        from_id: Option<&str>,
        limit: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let path = if market == BinanceMarket::Spot {
            SPOT_ACCOUNT_TRADES
        } else {
            FUTURES_ACCOUNT_TRADES
        };
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        if market == BinanceMarket::Spot {
            push_optional(&mut params, "orderId", order_id);
        }
        push_optional(&mut params, "startTime", start_time);
        push_optional(&mut params, "endTime", end_time);
        push_optional(&mut params, "fromId", from_id);
        push_optional(&mut params, "limit", limit);
        self.request(HttpMethod::Get, market, path, params, true)
            .await
    }

    pub async fn get_future_position(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_POSITION_INFO,
            vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)],
            true,
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

    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = PublicParams(params);
        match method_name {
            "get_account_balance" => {
                self.get_account_balance(params.get("market_type").unwrap_or("swap"))
                    .await
            }
            "get_income_history" => {
                self.get_income_history(
                    params.get("product_symbol"),
                    params.get("incomeType"),
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("page")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_account_info" => self.get_futures_account_info().await,
            "get_wallet_balance" => self.get_wallet_balance(params.get("quoteAsset")).await,
            "get_funding_wallet" => {
                self.get_funding_wallet(params.get("asset"), params.get("needBtcValuation"))
                    .await
            }
            "create_universal_transfer" => {
                self.create_universal_transfer(
                    params.required("type")?,
                    params.required("asset")?,
                    params.required("amount")?,
                    params.get("fromSymbol"),
                    params.get("toSymbol"),
                )
                .await
            }
            "get_universal_transfer_history" => {
                self.get_universal_transfer_history(
                    params.required("type")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("current")?,
                    params.u64("size")?,
                    params.get("fromSymbol"),
                    params.get("toSymbol"),
                )
                .await
            }
            "create_futures_listen_key" => self.create_futures_listen_key().await,
            "keep_alive_futures_listen_key" => {
                self.keep_alive_futures_listen_key(params.required("listenKey")?)
                    .await
            }
            "close_futures_listen_key" => {
                self.close_futures_listen_key(params.required("listenKey")?)
                    .await
            }
            "set_leverage" => {
                self.set_leverage(
                    params.required("product_symbol")?,
                    params.required("leverage")?,
                )
                .await
            }
            "place_order" => {
                self.place_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type_")?,
                    params.without(&["product_symbol", "side", "type_"]),
                )
                .await
            }
            "test_order" => {
                self.test_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type_")?,
                    params.without(&["product_symbol", "side", "type_"]),
                )
                .await
            }
            "place_futures_algo_order" => {
                self.place_futures_algo_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type_")?,
                    params.get("algoType").unwrap_or("CONDITIONAL"),
                    params.without(&["product_symbol", "side", "type_", "algoType"]),
                )
                .await
            }
            "cancel_futures_algo_order" => {
                self.cancel_futures_algo_order(params.get("algoId"), params.get("clientAlgoId"))
                    .await
            }
            "get_futures_algo_order" => {
                self.get_futures_algo_order(params.get("algoId"), params.get("clientAlgoId"))
                    .await
            }
            "get_all_open_futures_algo_orders" => {
                self.get_all_open_futures_algo_orders(
                    params.get("product_symbol"),
                    params.get("algoType"),
                    params.get("algoId"),
                )
                .await
            }
            "get_all_futures_algo_orders" => {
                self.get_all_futures_algo_orders(
                    params.required("product_symbol")?,
                    params.get("algoId"),
                    params.get("startTime"),
                    params.get("endTime"),
                    params.get("limit"),
                )
                .await
            }
            "cancel_all_open_futures_algo_orders" => {
                self.cancel_all_open_futures_algo_orders(params.required("product_symbol")?)
                    .await
            }
            "place_market_order" => {
                self.place_market_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("quantity")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                    params.get("newOrderRespType"),
                )
                .await
            }
            "place_market_buy_order" => {
                self.place_market_buy_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                    params.get("newOrderRespType"),
                )
                .await
            }
            "place_market_sell_order" => {
                self.place_market_sell_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                    params.get("newOrderRespType"),
                )
                .await
            }
            "place_limit_order" => {
                self.place_limit_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("timeInForce").unwrap_or("GTC"),
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "place_limit_buy_order" => {
                self.place_limit_buy_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("timeInForce").unwrap_or("GTC"),
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "place_limit_sell_order" => {
                self.place_limit_sell_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("timeInForce").unwrap_or("GTC"),
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "place_post_only_limit_order" => {
                self.place_post_only_limit_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "place_post_only_limit_buy_order" => {
                self.place_post_only_limit_buy_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "place_post_only_limit_sell_order" => {
                self.place_post_only_limit_sell_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "cancel_order" => {
                self.cancel_order(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("origClientOrderId"),
                )
                .await
            }
            "get_order" => {
                self.get_order(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("origClientOrderId"),
                )
                .await
            }
            "get_open_orders" => {
                self.get_open_orders(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("origClientOrderId"),
                )
                .await
            }
            "get_all_open_orders" => {
                self.get_all_open_orders(
                    params.get("product_symbol"),
                    params.get("market_type").unwrap_or("spot"),
                )
                .await
            }
            "cancel_all_open_orders" => {
                self.cancel_all_open_orders(params.required("product_symbol")?)
                    .await
            }
            "get_future_all_order" => {
                self.get_future_all_order(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("startTime"),
                    params.get("endTime"),
                    params.get("limit"),
                )
                .await
            }
            "get_all_orders" => {
                self.get_all_orders(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("startTime"),
                    params.get("endTime"),
                    params.get("limit"),
                )
                .await
            }
            "get_account_trades" => {
                self.get_account_trades(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("startTime"),
                    params.get("endTime"),
                    params.get("fromId"),
                    params.get("limit"),
                )
                .await
            }
            "get_future_position" => {
                self.get_future_position(params.required("product_symbol")?)
                    .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Binance private method: {method_name}"
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

    async fn api_key_request(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let api_key = self.api_key.as_deref().ok_or_else(|| {
            DcexError::InvalidInput("Binance API key is required for this request.".to_string())
        })?;
        let mut request = self.build_request(method, market, path, params);
        request
            .headers
            .insert("X-MBX-APIKEY".to_string(), api_key.to_string());
        self.inner.execute(request, false).await
    }

    async fn order_request(
        &self,
        method: HttpMethod,
        product_symbol: &str,
        test: bool,
        side: &str,
        order_type: &str,
        extra_params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let path = match (market, test) {
            (BinanceMarket::Spot, false) => SPOT_ORDER,
            (BinanceMarket::Spot, true) => SPOT_TEST_ORDER,
            (BinanceMarket::Futures, false) => FUTURES_ORDER,
            (BinanceMarket::Futures, true) => FUTURES_TEST_ORDER,
        };
        let mut params = vec![
            ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
            ("side".to_string(), normalize_order_side(side)?),
            ("type".to_string(), order_type.to_string()),
        ];
        params.extend(extra_params);
        self.request(method, market, path, params, true).await
    }

    async fn futures_algo_order_request(
        &self,
        method: HttpMethod,
        algo_id: Option<&str>,
        client_algo_id: Option<&str>,
    ) -> Result<ValidatedResponse> {
        if algo_id.is_none() && client_algo_id.is_none() {
            return Err(DcexError::InvalidInput(
                "Either algoId or clientAlgoId is required.".to_string(),
            ));
        }
        let mut params = Vec::new();
        push_optional(&mut params, "algoId", algo_id);
        push_optional(&mut params, "clientAlgoId", client_algo_id);
        self.request(
            method,
            BinanceMarket::Futures,
            FUTURES_ALGO_ORDER,
            params,
            true,
        )
        .await
    }

    async fn order_lookup_request(
        &self,
        method: HttpMethod,
        product_symbol: &str,
        order_id: Option<&str>,
        orig_client_order_id: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let path = if market == BinanceMarket::Spot {
            SPOT_ORDER
        } else {
            FUTURES_ORDER
        };
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional(&mut params, "orderId", order_id);
        push_optional(&mut params, "origClientOrderId", orig_client_order_id);
        self.request(method, market, path, params, true).await
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
        params.insert(
            0,
            ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
        );
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

    fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if let Some(table) = &self.product_table {
            if is_canonical_product_symbol(product_symbol) {
                return table.get_exchange_symbol("binance", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }

    fn market_for_product_symbol(&self, product_symbol: &str) -> Result<BinanceMarket> {
        if let Some(table) = &self.product_table {
            if is_canonical_product_symbol(product_symbol) {
                let product_type = table.get_product_type("binance", Some(product_symbol), None)?;
                return Ok(if product_type == "spot" {
                    BinanceMarket::Spot
                } else {
                    BinanceMarket::Futures
                });
            }
        }
        Ok(market_for_product_symbol_fallback(product_symbol))
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

    fn without(&self, excluded: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| !excluded.contains(&key.as_str()))
            .cloned()
            .collect()
    }
}

fn exchange_symbol_fallback(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{quote}"),
        _ => product_symbol.to_string(),
    }
}

fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.contains('-')
}

fn is_spot_product_symbol(product_symbol: &str) -> bool {
    product_symbol.ends_with("-SPOT")
}

fn market_for_product_symbol_fallback(product_symbol: &str) -> BinanceMarket {
    if is_spot_product_symbol(product_symbol) {
        BinanceMarket::Spot
    } else {
        BinanceMarket::Futures
    }
}

fn market_from_type(market_type: &str) -> BinanceMarket {
    if market_type.eq_ignore_ascii_case("spot") {
        BinanceMarket::Spot
    } else {
        BinanceMarket::Futures
    }
}

fn normalize_order_side(side: &str) -> Result<String> {
    if side.eq_ignore_ascii_case("buy") {
        Ok("BUY".to_string())
    } else if side.eq_ignore_ascii_case("sell") {
        Ok("SELL".to_string())
    } else {
        Err(DcexError::InvalidInput(format!(
            "unsupported Binance order side: {side}"
        )))
    }
}

fn ensure_futures_listen_key_market(market_type: &str) -> Result<()> {
    if market_type.eq_ignore_ascii_case("spot") {
        Err(DcexError::InvalidInput(
            "Binance Spot user data streams are subscribed through the WebSocket API.".to_string(),
        ))
    } else {
        Ok(())
    }
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

    #[test]
    fn product_symbol_selects_expected_market() {
        assert_eq!(
            market_for_product_symbol_fallback("BTC-USDT-SPOT"),
            BinanceMarket::Spot
        );
        assert_eq!(
            market_for_product_symbol_fallback("BTC-USDT-SWAP"),
            BinanceMarket::Futures
        );
    }

    #[test]
    fn product_table_overrides_symbol_fallback() {
        let table = ProductTable::new(vec![crate::product_table::MarketInfo {
            exchange: "binance".to_string(),
            exchange_symbol: "BTCUSDT_250627".to_string(),
            product_symbol: "BTC-USDT-250627".to_string(),
            product_type: "futures".to_string(),
            exchange_type: "delivery".to_string(),
            price_precision: "0.1".to_string(),
            size_precision: "0.001".to_string(),
            min_size: "0.001".to_string(),
            base_currency: "BTC".to_string(),
            quote_currency: "USDT".to_string(),
            min_notional: "0".to_string(),
            size_per_contract: "1".to_string(),
        }]);
        let client = BinanceClient::new(None, None, Duration::from_secs(1))
            .expect("client")
            .with_product_table(table);

        assert_eq!(
            client
                .exchange_symbol("BTC-USDT-250627")
                .expect("exchange symbol"),
            "BTCUSDT_250627"
        );
        assert_eq!(
            client
                .market_for_product_symbol("BTC-USDT-250627")
                .expect("market"),
            BinanceMarket::Futures
        );
    }

    #[test]
    fn order_side_is_normalized_and_validated() {
        assert_eq!(normalize_order_side("buy").expect("buy side"), "BUY");
        assert_eq!(normalize_order_side("SELL").expect("sell side"), "SELL");
        assert_eq!(
            normalize_order_side("hold"),
            Err(DcexError::InvalidInput(
                "unsupported Binance order side: hold".to_string()
            ))
        );
    }

    #[test]
    fn futures_algo_lookup_requires_an_identifier_before_requesting() {
        let client = BinanceClient::new(
            Some("api-key".to_string()),
            Some("secret".to_string()),
            Duration::from_secs(1),
        )
        .expect("client");

        let error = block_on(async move {
            client
                .private_request("cancel_futures_algo_order", Vec::new())
                .await
        })
        .expect_err("missing algo identifier must fail");

        assert_eq!(
            error,
            DcexError::InvalidInput("Either algoId or clientAlgoId is required.".to_string())
        );
    }
}
