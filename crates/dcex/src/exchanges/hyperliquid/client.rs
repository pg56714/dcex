use std::sync::Arc;
use std::time::Duration;

use serde_json::{Map, Number, Value};

use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::{EXCHANGE, INFO, MAINNET_URL, TESTNET_URL};
use super::params::{fallback_coin, is_canonical_product_symbol};
use super::signing::{encode_query, http_method_name, hyperliquid_signature, parse_private_key};

#[derive(Clone)]
pub struct HyperliquidClient {
    transport: AsyncHttpClient,
    endpoint: String,
    testnet: bool,
    wallet_address: Option<String>,
    private_key: Option<[u8; 32]>,
    product_table: Option<Arc<ProductTable>>,
}

impl HyperliquidClient {
    pub fn new(
        testnet: bool,
        wallet_address: Option<String>,
        private_key: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_endpoint(
            testnet,
            wallet_address,
            private_key,
            timeout,
            if testnet { TESTNET_URL } else { MAINNET_URL }.to_string(),
        )
    }

    pub fn with_endpoint(
        testnet: bool,
        wallet_address: Option<String>,
        private_key: Option<String>,
        timeout: Duration,
        endpoint: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            endpoint,
            testnet,
            wallet_address,
            private_key: private_key.map(|key| parse_private_key(&key)).transpose()?,
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
        query_json: Vec<u8>,
        action_msgpack: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, path, query_json, action_msgpack, signed)
            .await?;
        response.ensure_success()?;
        let data = response.json()?;
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
        query_json: Vec<u8>,
        action_msgpack: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let timestamp = unix_timestamp_ms()?;
        let request = self.build_request(
            method,
            path,
            query_json,
            action_msgpack.as_deref(),
            signed,
            timestamp,
        )?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        query_json: Vec<u8>,
        action_msgpack: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, path, query_json, action_msgpack, signed)
                .await
        })
    }

    pub(super) async fn info_json_request(&self, query_json: Vec<u8>) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Post, INFO, query_json, None, false)
            .await
    }

    pub(super) async fn info_payload(&self, payload: Value) -> Result<ValidatedResponse> {
        self.info_json_request(json_bytes(&payload)?).await
    }

    pub(super) async fn exchange_payload(
        &self,
        payload: Value,
        action_msgpack: Vec<u8>,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Post,
            EXCHANGE,
            json_bytes(&payload)?,
            Some(action_msgpack),
            true,
        )
        .await
    }

    fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        query_json: Vec<u8>,
        action_msgpack: Option<&[u8]>,
        signed: bool,
        timestamp: u64,
    ) -> Result<HttpRequest> {
        if !matches!(method, HttpMethod::Get | HttpMethod::Post) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Hyperliquid HTTP method: {}",
                http_method_name(method)
            )));
        }
        let mut query: Value = if query_json.is_empty() {
            Value::Object(Map::new())
        } else {
            serde_json::from_slice(&query_json)
                .map_err(|error| DcexError::Decode(error.to_string()))?
        };
        let query_object = query.as_object_mut().ok_or_else(|| {
            DcexError::InvalidInput("Hyperliquid query must be a JSON object.".to_string())
        })?;

        if signed {
            if self.wallet_address.is_none() || self.private_key.is_none() {
                return Err(DcexError::InvalidInput(
                    "Signed request requires Address and Private Key of wallet.".to_string(),
                ));
            }
            let action_msgpack = action_msgpack.ok_or_else(|| {
                DcexError::InvalidInput(
                    "Signed Hyperliquid requests require MessagePack action bytes.".to_string(),
                )
            })?;
            let vault_address = query_object
                .get("vaultAddress")
                .and_then(Value::as_str)
                .filter(|value| !value.is_empty());
            let expire_after = query_object.get("expireAfter").and_then(Value::as_u64);
            let signature = hyperliquid_signature(
                action_msgpack,
                timestamp,
                vault_address,
                expire_after,
                self.testnet,
                self.private_key.as_ref().expect("checked private key"),
            )?;
            query_object.insert("nonce".to_string(), Value::Number(Number::from(timestamp)));
            query_object.insert(
                "signature".to_string(),
                serde_json::json!({
                    "r": signature.r,
                    "s": signature.s,
                    "v": signature.v,
                }),
            );
        }

        let path = path.into();
        let mut request = HttpRequest::new(method, &self.endpoint, &path)
            .header("Content-Type", "application/json");
        if method == HttpMethod::Get {
            let query_string = encode_query(query_object);
            if !query_string.is_empty() {
                request.path = format!("{path}?{query_string}");
            }
        } else {
            request.body = RequestBody::Raw(
                serde_json::to_vec(&query).map_err(|error| DcexError::Decode(error.to_string()))?,
            );
        }
        Ok(request)
    }

    pub(super) fn symbol_parts(&self, product_symbol: &str) -> Result<(String, u64)> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return parse_exchange_symbol(
                    &table.get_exchange_symbol("hyperliquid", product_symbol)?,
                );
            }
        }
        parse_exchange_symbol(product_symbol).or_else(|_| {
            Ok((
                fallback_coin(product_symbol),
                fallback_asset_id(product_symbol),
            ))
        })
    }

    pub(super) fn coin(&self, product_symbol: &str) -> Result<String> {
        Ok(self.symbol_parts(product_symbol)?.0)
    }

    pub(super) fn asset_id(&self, product_symbol: &str) -> Result<u64> {
        Ok(self.symbol_parts(product_symbol)?.1)
    }
}

fn json_bytes(value: &Value) -> Result<Vec<u8>> {
    serde_json::to_vec(value).map_err(|error| DcexError::Decode(error.to_string()))
}

fn parse_exchange_symbol(exchange_symbol: &str) -> Result<(String, u64)> {
    let value = serde_json::from_str::<Value>(exchange_symbol).map_err(|error| {
        DcexError::InvalidInput(format!("invalid Hyperliquid exchange symbol: {error}"))
    })?;
    let values = value.as_array().ok_or_else(|| {
        DcexError::InvalidInput("Hyperliquid exchange symbol must be a JSON array.".to_string())
    })?;
    if values.len() < 2 {
        return Err(DcexError::InvalidInput(
            "Hyperliquid exchange symbol must contain coin and asset id.".to_string(),
        ));
    }
    let coin = values[0]
        .as_str()
        .ok_or_else(|| DcexError::InvalidInput("Hyperliquid coin must be a string.".to_string()))?;
    let asset_id = values[1].as_u64().ok_or_else(|| {
        DcexError::InvalidInput("Hyperliquid asset id must be an integer.".to_string())
    })?;
    Ok((coin.to_string(), asset_id))
}

fn fallback_asset_id(product_symbol: &str) -> u64 {
    if product_symbol.contains("-SPOT") {
        10_000
    } else {
        0
    }
}
