use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::Duration;

use serde_json::{Map, Value};
use tokio::sync::Mutex;
use url::form_urlencoded;

use crate::common::OrderSide;
use crate::crypto::hmac_sha256_hex;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

const BASE_URL: &str = "https://api.bybit.com";
const TIME_ENDPOINT: &str = "/v5/market/time";
const INSTRUMENTS_INFO: &str = "/v5/market/instruments-info";
const KLINE: &str = "/v5/market/kline";
const ORDERBOOK: &str = "/v5/market/orderbook";
const TICKERS: &str = "/v5/market/tickers";
const FUNDING_RATE_HISTORY: &str = "/v5/market/funding/history";
const PUBLIC_TRADE_HISTORY: &str = "/v5/market/recent-trade";
const OPEN_INTEREST: &str = "/v5/market/open-interest";
const HISTORICAL_VOLATILITY: &str = "/v5/market/historical-volatility";
const INSURANCE_POOL: &str = "/v5/market/insurance";
const RISK_LIMIT: &str = "/v5/market/risk-limit";
const DELIVERY_PRICE: &str = "/v5/market/delivery-price";
const LONG_SHORT_RATIO: &str = "/v5/market/account-ratio";
const ORDER_PRICE_LIMIT: &str = "/v5/market/price-limit";
const ADL_ALERT: &str = "/v5/market/adlAlert";
const GET_WALLET_BALANCE: &str = "/v5/account/wallet-balance";
const GET_TRANSFERABLE_AMOUNT: &str = "/v5/account/withdrawal";
const UPGRADE_TO_UNIFIED_ACCOUNT: &str = "/v5/account/upgrade-to-uta";
const GET_BORROW_HISTORY: &str = "/v5/account/borrow-history";
const GET_COLLATERAL_INFO: &str = "/v5/account/collateral-info";
const GET_FEE_RATE: &str = "/v5/account/fee-rate";
const GET_ACCOUNT_INFO: &str = "/v5/account/info";
const GET_TRANSACTION_LOG: &str = "/v5/account/transaction-log";
const SET_MARGIN_MODE: &str = "/v5/account/set-margin-mode";
const GET_COIN_INFO: &str = "/v5/asset/coin/query-info";
const GET_SUB_UID: &str = "/v5/asset/transfer/query-sub-member-list";
const GET_SPOT_ASSET_INFO: &str = "/v5/asset/transfer/query-asset-info";
const GET_ALL_COINS_BALANCE: &str = "/v5/asset/transfer/query-account-coins-balance";
const GET_SINGLE_COIN_BALANCE: &str = "/v5/asset/transfer/query-account-coin-balance";
const GET_WITHDRAWABLE_AMOUNT: &str = "/v5/asset/withdraw/withdrawable-amount";
const GET_INTERNAL_TRANSFER_RECORDS: &str = "/v5/asset/transfer/query-inter-transfer-list";
const GET_TRANSFERABLE_COIN: &str = "/v5/asset/transfer/query-transfer-coin-list";
const CREATE_INTERNAL_TRANSFER: &str = "/v5/asset/transfer/inter-transfer";
const GET_UNIVERSAL_TRANSFER_RECORDS: &str = "/v5/asset/transfer/query-universal-transfer-list";
const SET_DEPOSIT_ACCOUNT: &str = "/v5/asset/deposit/deposit-to-account";
const GET_DEPOSIT_RECORDS: &str = "/v5/asset/deposit/query-record";
const GET_SUB_ACCOUNT_DEPOSIT_RECORDS: &str = "/v5/asset/deposit/query-sub-member-record";
const GET_INTERNAL_DEPOSIT_RECORDS: &str = "/v5/asset/deposit/query-internal-record";
const GET_MASTER_DEPOSIT_ADDRESS: &str = "/v5/asset/deposit/query-address";
const GET_POSITIONS: &str = "/v5/position/list";
const SET_LEVERAGE: &str = "/v5/position/set-leverage";
const SWITCH_POSITION_MODE: &str = "/v5/position/switch-mode";
const GET_CLOSED_PNL: &str = "/v5/position/closed-pnl";
const PLACE_ORDER: &str = "/v5/order/create";
const AMEND_ORDER: &str = "/v5/order/amend";
const CANCEL_ORDER: &str = "/v5/order/cancel";
const GET_OPEN_ORDERS: &str = "/v5/order/realtime";
const CANCEL_BATCH_ORDERS: &str = "/v5/order/cancel-batch";
const CANCEL_ALL_ORDERS: &str = "/v5/order/cancel-all";
const GET_ORDER_HISTORY: &str = "/v5/order/history";
const GET_EXECUTION_LIST: &str = "/v5/execution/list";
const BATCH_PLACE_ORDER: &str = "/v5/order/create-batch";
const BATCH_AMEND_ORDER: &str = "/v5/order/amend-batch";
const GET_BORROW_QUOTA: &str = "/v5/order/spot-borrow-check";
const VIP_MARGIN_DATA: &str = "/v5/spot-margin-trade/data";
const SPOT_MARGIN_COLLATERAL: &str = "/v5/spot-margin-trade/collateral";
const HISTORICAL_INTEREST: &str = "/v5/spot-margin-trade/interest-rate-history";
const STATUS_AND_LEVERAGE: &str = "/v5/spot-margin-trade/state";
static TRANSFER_COUNTER: AtomicU64 = AtomicU64::new(0);

#[derive(Clone)]
pub struct BybitClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    recv_window: u64,
    sync_server_time: bool,
    timestamp_offset_ms: Arc<Mutex<Option<i64>>>,
    product_table: Option<Arc<ProductTable>>,
}

impl BybitClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        recv_window: u64,
        sync_server_time: bool,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(
            api_key,
            api_secret,
            recv_window,
            sync_server_time,
            timeout,
            BASE_URL.to_string(),
        )
    }

    pub fn with_base_url(
        api_key: Option<String>,
        api_secret: Option<String>,
        recv_window: u64,
        sync_server_time: bool,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key,
            api_secret,
            recv_window,
            sync_server_time,
            timestamp_offset_ms: Arc::new(Mutex::new(None)),
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
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self.request_raw(method, path, params, body, signed).await?;
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
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let timestamp = self.timestamp(signed).await?;
        let request = self.build_request(method, path, params, body, signed, timestamp)?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move { client.request_raw(method, path, params, body, signed).await })
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let (path, params) = match method_name {
            "get_instruments_info" => (
                INSTRUMENTS_INFO,
                self.normalize_symbol_params(params, true)?,
            ),
            "get_kline" => (KLINE, self.normalize_kline_params(params)?),
            "get_orderbook" => (ORDERBOOK, self.normalize_symbol_params(params, true)?),
            "get_tickers" => (TICKERS, self.normalize_symbol_params(params, true)?),
            "get_funding_rate_history" => (
                FUNDING_RATE_HISTORY,
                self.normalize_symbol_params(params, true)?,
            ),
            "get_public_trade_history" => (
                PUBLIC_TRADE_HISTORY,
                self.normalize_symbol_params(params, true)?,
            ),
            "get_open_interest" => (OPEN_INTEREST, self.normalize_symbol_params(params, true)?),
            "get_long_short_ratio" => (
                LONG_SHORT_RATIO,
                self.normalize_symbol_params(params, true)?,
            ),
            "get_historical_volatility" => (HISTORICAL_VOLATILITY, params),
            "get_insurance_pool" => (INSURANCE_POOL, params),
            "get_delivery_price" => (DELIVERY_PRICE, self.normalize_symbol_params(params, true)?),
            "get_order_price_limit" => (
                ORDER_PRICE_LIMIT,
                self.normalize_symbol_params(params, true)?,
            ),
            "get_adl_alert" => (ADL_ALERT, self.normalize_symbol_params(params, true)?),
            "get_risk_limit" => (RISK_LIMIT, self.normalize_symbol_params(params, false)?),
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Bybit public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, path, params, None, false)
            .await
    }

    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = BybitParams(params);
        match method_name {
            "get_wallet_balance" => {
                self.get_request(
                    GET_WALLET_BALANCE,
                    vec![("accountType".to_string(), "UNIFIED".to_string())],
                )
                .await
            }
            "get_transferable_amount" => {
                let coins = params.required("coins")?;
                if coins.is_empty() {
                    return Err(DcexError::InvalidInput(
                        "coins must contain at least one coin.".to_string(),
                    ));
                }
                let count = coins.split(',').filter(|coin| !coin.is_empty()).count();
                if count > 20 {
                    return Err(DcexError::InvalidInput(
                        "coins must contain no more than 20 coins.".to_string(),
                    ));
                }
                self.get_request(
                    GET_TRANSFERABLE_AMOUNT,
                    vec![("coinName".to_string(), coins.to_string())],
                )
                .await
            }
            "upgrade_to_unified_trading_account" => {
                self.post_request(UPGRADE_TO_UNIFIED_ACCOUNT, Map::new())
                    .await
            }
            "get_borrow_history" => {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "currency", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_BORROW_HISTORY, query).await
            }
            "get_collateral_info" => {
                self.get_request(GET_COLLATERAL_INFO, params.only(&["coin"]))
                    .await
            }
            "get_fee_rates" => {
                let mut query = Vec::new();
                if let Some(product_symbol) = params.get("product_symbol") {
                    self.push_symbol_category(&mut query, product_symbol, true)?;
                }
                push_optional(&mut query, "category", params.get("category"));
                self.get_request(GET_FEE_RATE, query).await
            }
            "get_account_info" => self.get_request(GET_ACCOUNT_INFO, Vec::new()).await,
            "get_transaction_log" => {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "category", params.get("category"));
                push_optional(&mut query, "currency", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_TRANSACTION_LOG, query).await
            }
            "set_margin_mode" => {
                let mut body = Map::new();
                body.insert(
                    "setMarginMode".to_string(),
                    Value::String(params.required("margin_mode")?.to_string()),
                );
                self.post_request(SET_MARGIN_MODE, body).await
            }
            "get_coin_info" => {
                self.get_request(GET_COIN_INFO, params.only(&["coin"]))
                    .await
            }
            "get_sub_uid" => self.get_request(GET_SUB_UID, Vec::new()).await,
            "get_spot_asset_info" => {
                let mut query = vec![("accountType".to_string(), "SPOT".to_string())];
                push_optional(&mut query, "coin", params.get("coin"));
                self.get_request(GET_SPOT_ASSET_INFO, query).await
            }
            "get_coins_balance" => {
                let mut query = vec![(
                    "accountType".to_string(),
                    params.required("accountType")?.to_string(),
                )];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "memberId", params.get("memberId"));
                self.get_request(GET_ALL_COINS_BALANCE, query).await
            }
            "get_coin_balance" => {
                let mut query = vec![
                    (
                        "accountType".to_string(),
                        params.required("accountType")?.to_string(),
                    ),
                    ("coin".to_string(), params.required("coin")?.to_string()),
                ];
                push_optional(&mut query, "memberId", params.get("memberId"));
                push_optional(&mut query, "toAccountType", params.get("toAccountType"));
                self.get_request(GET_SINGLE_COIN_BALANCE, query).await
            }
            "get_withdrawable_amount" => {
                self.get_request(
                    GET_WITHDRAWABLE_AMOUNT,
                    vec![("coin".to_string(), params.required("coin")?.to_string())],
                )
                .await
            }
            "get_internal_transfer_records" => {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_INTERNAL_TRANSFER_RECORDS, query).await
            }
            "get_transferable_coin" => {
                let query = vec![
                    (
                        "fromAccountType".to_string(),
                        params.required("fromAccountType")?.to_string(),
                    ),
                    (
                        "toAccountType".to_string(),
                        params.required("toAccountType")?.to_string(),
                    ),
                ];
                self.get_request(GET_TRANSFERABLE_COIN, query).await
            }
            "create_internal_transfer" => {
                let mut body = string_body(&[
                    ("coin", params.required("coin")?),
                    ("amount", params.required("amount")?),
                    ("fromAccountType", params.required("fromAccountType")?),
                    ("toAccountType", params.required("toAccountType")?),
                ]);
                let transfer_id = params
                    .get("transferId")
                    .map(str::to_string)
                    .unwrap_or_else(generate_transfer_id);
                body.insert("transferId".to_string(), Value::String(transfer_id));
                self.post_request(CREATE_INTERNAL_TRANSFER, body).await
            }
            "get_universal_transfer_records" => {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "status", params.get("status"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_UNIVERSAL_TRANSFER_RECORDS, query)
                    .await
            }
            "set_deposit_account" => {
                let body = string_body(&[("accountType", params.required("accountType")?)]);
                self.post_request(SET_DEPOSIT_ACCOUNT, body).await
            }
            "get_deposit_records" => {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_DEPOSIT_RECORDS, query).await
            }
            "get_sub_deposit_records" => {
                let mut query = vec![
                    (
                        "subMemberId".to_string(),
                        params.required("subMemberId")?.to_string(),
                    ),
                    (
                        "limit".to_string(),
                        params.get("limit").unwrap_or("20").to_string(),
                    ),
                ];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_SUB_ACCOUNT_DEPOSIT_RECORDS, query)
                    .await
            }
            "get_internal_deposit_records" => {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_INTERNAL_DEPOSIT_RECORDS, query).await
            }
            "get_master_deposit_address" => {
                self.get_request(
                    GET_MASTER_DEPOSIT_ADDRESS,
                    vec![("coin".to_string(), params.required("coin")?.to_string())],
                )
                .await
            }
            "get_positions" => self.get_positions_from_params(&params).await,
            "set_leverage" => {
                let product_symbol = params.required("product_symbol")?;
                let mut body = Map::new();
                self.insert_symbol_category(&mut body, product_symbol)?;
                body.insert(
                    "buyLeverage".to_string(),
                    Value::String(params.required("leverage")?.to_string()),
                );
                body.insert(
                    "sellLeverage".to_string(),
                    Value::String(params.required("leverage")?.to_string()),
                );
                self.post_request(SET_LEVERAGE, body).await
            }
            "switch_position_mode" => {
                let mut body = Map::new();
                body.insert("category".to_string(), Value::String("linear".to_string()));
                body.insert(
                    "mode".to_string(),
                    Value::Number(params.i64_required("mode")?.into()),
                );
                if let Some(product_symbol) = params.get("product_symbol") {
                    body.insert(
                        "symbol".to_string(),
                        Value::String(self.exchange_symbol(product_symbol)?),
                    );
                }
                insert_optional_string(&mut body, "coin", params.get("coin"));
                self.post_request(SWITCH_POSITION_MODE, body).await
            }
            "get_closed_pnl" => self.get_closed_pnl_from_params(&params).await,
            "place_order" => self.place_order_from_params(&params).await,
            "place_market_order" => {
                let mut pairs = params.without(&["orderType"]);
                pairs.push(("orderType".to_string(), "Market".to_string()));
                self.place_order_from_params(&BybitParams(pairs)).await
            }
            "place_market_buy_order" => {
                let mut pairs = params.without(&["side", "orderType"]);
                pairs.push(("side".to_string(), "Buy".to_string()));
                pairs.push(("orderType".to_string(), "Market".to_string()));
                self.place_order_from_params(&BybitParams(pairs)).await
            }
            "place_market_sell_order" => {
                let mut pairs = params.without(&["side", "orderType"]);
                pairs.push(("side".to_string(), "Sell".to_string()));
                pairs.push(("orderType".to_string(), "Market".to_string()));
                self.place_order_from_params(&BybitParams(pairs)).await
            }
            "place_limit_order" => {
                let mut pairs = params.without(&["orderType"]);
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                self.place_order_from_params(&BybitParams(pairs)).await
            }
            "place_limit_buy_order" => {
                let mut pairs = params.without(&["side", "orderType"]);
                pairs.push(("side".to_string(), "Buy".to_string()));
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                self.place_order_from_params(&BybitParams(pairs)).await
            }
            "place_limit_sell_order" => {
                let mut pairs = params.without(&["side", "orderType"]);
                pairs.push(("side".to_string(), "Sell".to_string()));
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                self.place_order_from_params(&BybitParams(pairs)).await
            }
            "place_post_only_limit_order" => {
                let mut pairs = params.without(&["orderType", "timeInForce"]);
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                pairs.push(("timeInForce".to_string(), "PostOnly".to_string()));
                self.place_order_from_params(&BybitParams(pairs)).await
            }
            "place_post_only_limit_buy_order" => {
                let mut pairs = params.without(&["side", "orderType", "timeInForce"]);
                pairs.push(("side".to_string(), "Buy".to_string()));
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                pairs.push(("timeInForce".to_string(), "PostOnly".to_string()));
                self.place_order_from_params(&BybitParams(pairs)).await
            }
            "place_post_only_limit_sell_order" => {
                let mut pairs = params.without(&["side", "orderType", "timeInForce"]);
                pairs.push(("side".to_string(), "Sell".to_string()));
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                pairs.push(("timeInForce".to_string(), "PostOnly".to_string()));
                self.place_order_from_params(&BybitParams(pairs)).await
            }
            "amend_order" => self.amend_order_from_params(&params).await,
            "cancel_order" => self.cancel_order_from_params(&params).await,
            "get_open_orders" => self.get_open_orders_from_params(&params).await,
            "cancel_batch_orders" => self.batch_request(CANCEL_BATCH_ORDERS, &params).await,
            "cancel_all_orders" => self.cancel_all_orders_from_params(&params).await,
            "get_order_history" => self.get_order_history_from_params(&params).await,
            "get_execution_list" => self.get_execution_list_from_params(&params).await,
            "place_batch_order" => self.batch_request(BATCH_PLACE_ORDER, &params).await,
            "amend_batch_order" => self.batch_request(BATCH_AMEND_ORDER, &params).await,
            "get_borrow_quota" => {
                let product_symbol = params.required("product_symbol")?;
                let query = vec![
                    ("category".to_string(), "spot".to_string()),
                    ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
                    (
                        "side".to_string(),
                        OrderSide::parse(params.required("side")?)?
                            .to_exchange("bybit")?
                            .to_string(),
                    ),
                ];
                self.get_request(GET_BORROW_QUOTA, query).await
            }
            "get_vip_margin_data" => {
                self.get_request(VIP_MARGIN_DATA, params.only(&["vipLevel", "currency"]))
                    .await
            }
            "get_collateral" => {
                self.get_request(SPOT_MARGIN_COLLATERAL, params.only(&["currency"]))
                    .await
            }
            "get_historical_interest_rate" => {
                let mut query = vec![(
                    "currency".to_string(),
                    params.required("currency")?.to_string(),
                )];
                push_optional(&mut query, "vipLevel", params.get("vipLevel"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                push_optional(&mut query, "endTime", params.get("endTime"));
                self.get_request(HISTORICAL_INTEREST, query).await
            }
            "get_status_and_leverage" => self.get_request(STATUS_AND_LEVERAGE, Vec::new()).await,
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Bybit private method: {method_name}"
            ))),
        }
    }

    async fn get_request(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, None, true)
            .await
    }

    async fn post_request(
        &self,
        path: &str,
        body: Map<String, Value>,
    ) -> Result<ValidatedResponse> {
        let body = serde_json::to_vec(&Value::Object(body))
            .map_err(|error| DcexError::Decode(error.to_string()))?;
        self.request(HttpMethod::Post, path, Vec::new(), Some(body), true)
            .await
    }

    fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_symbol("bybit", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }

    fn category_for_product_symbol(
        &self,
        product_symbol: &str,
        default_category: &str,
    ) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_type("bybit", Some(product_symbol), None);
            }
        }
        Ok(category_for_product_symbol_fallback(
            product_symbol,
            default_category,
        ))
    }

    fn push_symbol_category(
        &self,
        params: &mut Vec<(String, String)>,
        product_symbol: &str,
        include_category: bool,
    ) -> Result<()> {
        params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        if include_category {
            params.push((
                "category".to_string(),
                self.category_for_product_symbol(product_symbol, "linear")?,
            ));
        }
        Ok(())
    }

    fn insert_symbol_category(
        &self,
        body: &mut Map<String, Value>,
        product_symbol: &str,
    ) -> Result<()> {
        body.insert(
            "category".to_string(),
            Value::String(self.category_for_product_symbol(product_symbol, "linear")?),
        );
        body.insert(
            "symbol".to_string(),
            Value::String(self.exchange_symbol(product_symbol)?),
        );
        Ok(())
    }

    fn normalize_symbol_params(
        &self,
        params: Vec<(String, String)>,
        include_product_category: bool,
    ) -> Result<Vec<(String, String)>> {
        let mut output = Vec::with_capacity(params.len() + 1);
        let mut product_symbol = None;
        let mut explicit_category = None;

        for (key, value) in params {
            match key.as_str() {
                "product_symbol" => product_symbol = Some(value),
                "category" => explicit_category = Some(value),
                "symbol" if is_canonical_product_symbol(&value) => {
                    output.push(("symbol".to_string(), self.exchange_symbol(&value)?));
                    if include_product_category {
                        explicit_category =
                            Some(self.category_for_product_symbol(&value, "linear")?);
                    }
                }
                _ => output.push((key, value)),
            }
        }

        if let Some(product_symbol) = product_symbol {
            output.push(("symbol".to_string(), self.exchange_symbol(&product_symbol)?));
            if include_product_category {
                explicit_category =
                    Some(self.category_for_product_symbol(&product_symbol, "linear")?);
            }
        }
        if let Some(category) = explicit_category {
            output.retain(|(key, _)| key != "category");
            output.insert(0, ("category".to_string(), category));
        }
        Ok(output)
    }

    fn normalize_kline_params(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<Vec<(String, String)>> {
        let normalized = self.normalize_symbol_params(params, true)?;
        normalized
            .into_iter()
            .map(|(key, value)| {
                if key == "interval" {
                    Ok((key, bybit_timeframe(&value)?.to_string()))
                } else if key == "startTime" {
                    Ok(("start".to_string(), value))
                } else {
                    Ok((key, value))
                }
            })
            .collect()
    }

    async fn get_positions_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        let mut query = vec![
            (
                "category".to_string(),
                params.get("category").unwrap_or("linear").to_string(),
            ),
            (
                "limit".to_string(),
                params.get("limit").unwrap_or("20").to_string(),
            ),
        ];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, true)?;
        }
        push_optional(&mut query, "settleCoin", params.get("settleCoin"));
        self.get_request(GET_POSITIONS, query).await
    }

    async fn get_closed_pnl_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        let mut query = vec![
            (
                "category".to_string(),
                params.get("category").unwrap_or("linear").to_string(),
            ),
            (
                "limit".to_string(),
                params.get("limit").unwrap_or("20").to_string(),
            ),
        ];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, true)?;
        }
        push_optional(&mut query, "startTime", params.get("startTime"));
        self.get_request(GET_CLOSED_PNL, query).await
    }

    async fn place_order_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        let product_symbol = params.required("product_symbol")?;
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, product_symbol)?;
        body.insert(
            "side".to_string(),
            Value::String(
                OrderSide::parse(params.required("side")?)?
                    .to_exchange("bybit")?
                    .to_string(),
            ),
        );
        body.insert(
            "orderType".to_string(),
            Value::String(params.required("orderType")?.to_string()),
        );
        body.insert(
            "qty".to_string(),
            Value::String(params.required("qty")?.to_string()),
        );
        for key in [
            "price",
            "isLeverage",
            "marketUnit",
            "triggerDirection",
            "orderFilter",
            "triggerPrice",
            "triggerBy",
            "orderIv",
            "timeInForce",
            "takeProfit",
            "stopLoss",
            "tpTriggerBy",
            "slTriggerBy",
            "reduceOnly",
            "closeOnTrigger",
            "tpslMode",
            "tpLimitPrice",
            "slLimitPrice",
            "tpOrderType",
            "slOrderType",
            "positionIdx",
        ] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        self.post_request(PLACE_ORDER, body).await
    }

    async fn amend_order_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        let product_symbol = params.required("product_symbol")?;
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, product_symbol)?;
        for key in [
            "orderId",
            "orderLinkId",
            "orderIv",
            "triggerPrice",
            "qty",
            "price",
            "tpslMode",
            "takeProfit",
            "stopLoss",
            "tpTriggerBy",
            "slTriggerBy",
            "triggerBy",
            "tpLimitPrice",
            "slLimitPrice",
        ] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        self.post_request(AMEND_ORDER, body).await
    }

    async fn cancel_order_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        let product_symbol = params.required("product_symbol")?;
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, product_symbol)?;
        insert_optional_string(&mut body, "orderId", params.get("orderId"));
        self.post_request(CANCEL_ORDER, body).await
    }

    async fn get_open_orders_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        let category = params.get("category").unwrap_or("linear");
        let mut query = vec![
            ("category".to_string(), category.to_string()),
            (
                "limit".to_string(),
                params.get("limit").unwrap_or("20").to_string(),
            ),
        ];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, true)?;
        } else {
            push_optional(&mut query, "baseCoin", params.get("baseCoin"));
            if let Some(settle_coin) = params.get("settleCoin") {
                query.push(("settleCoin".to_string(), settle_coin.to_string()));
            } else if category == "linear" {
                query.push(("settleCoin".to_string(), "USDT".to_string()));
            }
        }
        self.get_request(GET_OPEN_ORDERS, query).await
    }

    async fn cancel_all_orders_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        let mut body = Map::new();
        body.insert(
            "category".to_string(),
            Value::String(params.get("category").unwrap_or("linear").to_string()),
        );
        if let Some(product_symbol) = params.get("product_symbol") {
            self.insert_symbol_category(&mut body, product_symbol)?;
        }
        self.post_request(CANCEL_ALL_ORDERS, body).await
    }

    async fn get_order_history_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        let mut query = vec![(
            "category".to_string(),
            params.get("category").unwrap_or("linear").to_string(),
        )];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, true)?;
        }
        push_optional(&mut query, "orderId", params.get("orderId"));
        push_optional(&mut query, "startTime", params.get("startTime"));
        push_optional(&mut query, "cursor", params.get("cursor"));
        push_optional(&mut query, "limit", params.get("limit"));
        self.get_request(GET_ORDER_HISTORY, query).await
    }

    async fn get_execution_list_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        let mut query = vec![
            (
                "category".to_string(),
                params.get("category").unwrap_or("linear").to_string(),
            ),
            (
                "limit".to_string(),
                params.get("limit").unwrap_or("50").to_string(),
            ),
        ];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, true)?;
        }
        push_optional(&mut query, "startTime", params.get("startTime"));
        self.get_request(GET_EXECUTION_LIST, query).await
    }

    async fn batch_request(&self, path: &str, params: &BybitParams) -> Result<ValidatedResponse> {
        let mut body = Map::new();
        body.insert(
            "category".to_string(),
            Value::String(params.get("category").unwrap_or("linear").to_string()),
        );
        body.insert("request".to_string(), params.json_required("request")?);
        self.post_request(path, body).await
    }

    async fn timestamp(&self, signed: bool) -> Result<u64> {
        if !signed || !self.sync_server_time {
            return unix_timestamp_ms();
        }
        let mut offset = self.timestamp_offset_ms.lock().await;
        if offset.is_none() {
            let local_start = unix_timestamp_ms()?;
            let response = self
                .transport
                .execute(HttpRequest::new(
                    HttpMethod::Get,
                    &self.base_url,
                    TIME_ENDPOINT,
                ))
                .await;
            let local_end = unix_timestamp_ms()?;
            let calculated = response
                .ok()
                .and_then(|response| response.json().ok())
                .and_then(|data| extract_server_time_ms(&data))
                .map(|server_time| server_time as i64 - ((local_start + local_end) / 2) as i64)
                .unwrap_or(0);
            *offset = Some(calculated);
        }
        let local = unix_timestamp_ms()? as i64;
        let adjusted = local + offset.unwrap_or(0);
        u64::try_from(adjusted).map_err(|error| DcexError::Runtime(error.to_string()))
    }

    fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        mut params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        timestamp: u64,
    ) -> Result<HttpRequest> {
        let path = path.into();
        params.sort_by(|left, right| left.0.cmp(&right.0));
        let payload = if matches!(method, HttpMethod::Get) {
            encode_params(&params)
        } else {
            String::from_utf8_lossy(body.as_deref().unwrap_or_default()).into_owned()
        };
        let mut request = HttpRequest::new(method, &self.base_url, path)
            .header("Content-Type", "application/json");
        if matches!(method, HttpMethod::Get) {
            request.query = params;
        } else {
            request.body = body.map(RequestBody::Raw).unwrap_or_default();
        }
        if signed {
            let (api_key, api_secret) = self.credentials()?;
            let signature_payload = format!("{timestamp}{api_key}{}{payload}", self.recv_window);
            let signature = hmac_sha256_hex(api_secret.as_bytes(), signature_payload.as_bytes())?;
            request
                .headers
                .insert("X-BAPI-API-KEY".to_string(), api_key.to_string());
            request.headers.insert("X-BAPI-SIGN".to_string(), signature);
            request
                .headers
                .insert("X-BAPI-SIGN-TYPE".to_string(), "2".to_string());
            request
                .headers
                .insert("X-BAPI-TIMESTAMP".to_string(), timestamp.to_string());
            request.headers.insert(
                "X-BAPI-RECV-WINDOW".to_string(),
                self.recv_window.to_string(),
            );
        }
        Ok(request)
    }

    fn credentials(&self) -> Result<(&str, &str)> {
        match (&self.api_key, &self.api_secret) {
            (Some(api_key), Some(api_secret)) => Ok((api_key, api_secret)),
            _ => Err(DcexError::InvalidInput(
                "Signed request requires API Key and Secret.".to_string(),
            )),
        }
    }
}

struct BybitParams(Vec<(String, String)>);

impl BybitParams {
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

    fn i64_required(&self, key: &str) -> Result<i64> {
        self.required(key)?.parse::<i64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
        })
    }

    fn json_required(&self, key: &str) -> Result<Value> {
        serde_json::from_str(self.required(key)?).map_err(|error| {
            DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
        })
    }

    fn only(&self, keys: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| keys.contains(&key.as_str()))
            .cloned()
            .collect()
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

fn category_for_product_symbol_fallback(product_symbol: &str, default_category: &str) -> String {
    let parts = product_symbol.split('-').collect::<Vec<_>>();
    if parts.len() >= 3 {
        if parts[2].eq_ignore_ascii_case("SPOT") {
            return "spot".to_string();
        }
        if parts[1].eq_ignore_ascii_case("USD") {
            return "inverse".to_string();
        }
    }
    default_category.to_string()
}

fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.contains('-')
}

fn push_optional(params: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
}

fn insert_optional_string(body: &mut Map<String, Value>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        body.insert(key.to_string(), Value::String(value.to_string()));
    }
}

fn string_body(pairs: &[(&str, &str)]) -> Map<String, Value> {
    pairs
        .iter()
        .map(|(key, value)| (key.to_string(), Value::String(value.to_string())))
        .collect()
}

fn generate_transfer_id() -> String {
    let now = unix_timestamp_ms().unwrap_or(0) as u128;
    let counter = TRANSFER_COUNTER.fetch_add(1, Ordering::Relaxed) as u128;
    let value = (now << 64) | counter;
    let hex = format!("{value:032x}");
    format!(
        "{}-{}-4{}-a{}-{}",
        &hex[0..8],
        &hex[8..12],
        &hex[13..16],
        &hex[17..20],
        &hex[20..32]
    )
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

fn bybit_timeframe(timeframe: &str) -> Result<&'static str> {
    match timeframe {
        "1m" => Ok("1"),
        "3m" => Ok("3"),
        "5m" => Ok("5"),
        "15m" => Ok("15"),
        "30m" => Ok("30"),
        "1h" => Ok("60"),
        "2h" => Ok("120"),
        "4h" => Ok("240"),
        "6h" => Ok("360"),
        "12h" => Ok("720"),
        "1d" => Ok("D"),
        "1w" => Ok("W"),
        "1M" => Ok("M"),
        _ => Err(DcexError::InvalidInput(
            "timeframe not supported".to_string(),
        )),
    }
}

fn extract_server_time_ms(data: &Value) -> Option<u64> {
    if let Some(value) = data.get("time").and_then(json_u64) {
        return Some(value);
    }
    let result = data.get("result")?.as_object()?;
    if let Some(value) = result.get("timeNano").and_then(json_u64) {
        return Some(value / 1_000_000);
    }
    result
        .get("timeSecond")
        .and_then(json_u64)
        .map(|value| value * 1_000)
}

fn json_u64(value: &Value) -> Option<u64> {
    value
        .as_u64()
        .or_else(|| value.as_str().and_then(|value| value.parse().ok()))
}

fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    let code = data
        .as_object()
        .and_then(|object| object.get("retCode"))
        .map(json_value_string)
        .unwrap_or_else(|| "0".to_string());
    if code != "0" {
        let message = data
            .as_object()
            .and_then(|object| object.get("retMsg"))
            .and_then(Value::as_str)
            .unwrap_or("Unknown error");
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("Bybit API Error: [{code}] {message}"),
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
    fn auth_matches_python_vector() {
        let client = BybitClient::new(
            Some("test_api_key_0000".to_string()),
            Some("test_api_secret_0000".to_string()),
            5_000,
            false,
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Get,
                "/v5/order/realtime",
                vec![
                    ("symbol".to_string(), "BTCUSDT".to_string()),
                    ("category".to_string(), "linear".to_string()),
                ],
                None,
                true,
                1_700_000_000_000,
            )
            .expect("request");

        assert_eq!(
            request.headers.get("X-BAPI-SIGN").map(String::as_str),
            Some("ef8980e55f6ba1d32ab182ddbdad9c8182df87123b035c969965698c9dcd8713")
        );
    }

    #[test]
    fn auth_signs_encoded_get_query_payload() {
        let client = BybitClient::new(
            Some("test_api_key_0000".to_string()),
            Some("test_api_secret_0000".to_string()),
            5_000,
            false,
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Get,
                "/v5/account/withdrawal",
                vec![("coinName".to_string(), "BTC,ETH".to_string())],
                None,
                true,
                1_700_000_000_000,
            )
            .expect("request");

        assert_eq!(
            request.headers.get("X-BAPI-SIGN").map(String::as_str),
            Some("debcb4f8de9897ee9b0f8ff0c4f6c4ee2e98b96ee3e418617f23da70801fe587")
        );
    }

    #[test]
    fn extracts_supported_server_time_shapes() {
        assert_eq!(
            extract_server_time_ms(&serde_json::json!({"time": "1700000000000"})),
            Some(1_700_000_000_000)
        );
        assert_eq!(
            extract_server_time_ms(
                &serde_json::json!({"result": {"timeNano": "1700000000000000000"}})
            ),
            Some(1_700_000_000_000)
        );
    }
}
