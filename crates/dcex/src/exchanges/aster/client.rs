use std::sync::Arc;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::{AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody, block_on};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::{FUTURES_BASE_URL, SPOT_BASE_URL};
use super::params::json_value_string;
use super::signing::{encode_params, http_method_name, parse_private_key, sign_message};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AsterMarket {
    Futures,
    Spot,
}

impl AsterMarket {
    pub fn from_path(path: &str) -> Result<Self> {
        if path.starts_with("/fapi/") {
            return Ok(Self::Futures);
        }
        if path.starts_with("/api/") {
            return Ok(Self::Spot);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Aster API path: {path}"
        )))
    }
}

#[derive(Clone)]
pub struct AsterClient {
    transport: AsyncHttpClient,
    spot_base_url: String,
    futures_base_url: String,
    prediction_base_url: String,
    chain_base_url: String,
    announcement_base_url: String,
    user_address: Option<String>,
    signer_address: Option<String>,
    private_key: Option<[u8; 32]>,
    last_nonce: Arc<AtomicU64>,
    product_table: Option<Arc<ProductTable>>,
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

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, None, timeout)
    }

    pub fn with_base_urls(
        user_address: Option<String>,
        signer_address: Option<String>,
        private_key: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
    ) -> Result<Self> {
        if spot_base_url.trim().is_empty() || futures_base_url.trim().is_empty() {
            return Err(DcexError::InvalidInput(
                "Aster REST base URLs must not be empty.".to_string(),
            ));
        }
        match (&signer_address, &private_key) {
            (Some(signer), Some(_)) => validate_wallet_address("signer_address", signer)?,
            (None, None) => {}
            _ => {
                return Err(DcexError::InvalidInput(
                    "Aster signer_address and private_key must be provided together.".to_string(),
                ));
            }
        }
        if let Some(user) = &user_address {
            validate_wallet_address("user_address", user)?;
        }
        let is_testnet = |url: &str| {
            url::Url::parse(url)
                .ok()
                .and_then(|u| u.host_str().map(str::to_owned))
                .is_some_and(|host| host.ends_with(".asterdex-testnet.com"))
        };
        let spot_testnet = is_testnet(&spot_base_url);
        let futures_testnet = is_testnet(&futures_base_url);
        if spot_testnet != futures_testnet {
            return Err(DcexError::InvalidInput(
                "Aster network mismatch: configure both spot and futures URLs for testnet".into(),
            ));
        }
        let prediction_base_url = if spot_testnet {
            "https://papi.asterdex-testnet.com"
        } else {
            "https://papi.asterdex.com"
        };
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            spot_base_url: spot_base_url.trim_end_matches('/').to_string(),
            futures_base_url: futures_base_url.trim_end_matches('/').to_string(),
            prediction_base_url: prediction_base_url.into(),
            chain_base_url: "https://chainapi.asterdex.com".into(),
            announcement_base_url: "https://www.asterdex.com".into(),
            user_address,
            signer_address,
            private_key: private_key.map(|key| parse_private_key(&key)).transpose()?,
            last_nonce: Arc::new(AtomicU64::new(0)),
            product_table: None,
        })
    }

    pub fn with_auxiliary_base_urls(
        mut self,
        chain: String,
        announcements: String,
    ) -> Result<Self> {
        if chain.trim().is_empty() || announcements.trim().is_empty() {
            return Err(DcexError::InvalidInput(
                "Aster auxiliary base URLs cannot be empty".into(),
            ));
        }
        self.chain_base_url = chain.trim_end_matches('/').into();
        self.announcement_base_url = announcements.trim_end_matches('/').into();
        Ok(self)
    }

    pub(super) async fn auxiliary_public_request(
        &self,
        name: &str,
        params: &super::params::AsterParams,
    ) -> Result<Option<ValidatedResponse>> {
        use serde_json::json;
        let (base, path, method, fields, body): (&str, &str, HttpMethod, &[&str], Option<Value>) =
            match name {
                "get_chain_locked_aster" => (
                    &self.chain_base_url,
                    "/aster-chain/v3/staking/getLockedAster",
                    HttpMethod::Get,
                    &[],
                    None,
                ),
                "get_chain_withdraw_fee" => {
                    params.required("chainId")?.parse::<u64>().map_err(|_| {
                        DcexError::InvalidInput("chainId must be an unsigned integer".into())
                    })?;
                    params.required("asset")?;
                    (
                        &self.chain_base_url,
                        "/aster-chain/v3/withdraw/estimateFee",
                        HttpMethod::Get,
                        &["chainId", "asset"],
                        None,
                    )
                }
                "get_announcement" => {
                    params.required("id")?.parse::<u64>().map_err(|_| {
                        DcexError::InvalidInput("id must be an unsigned integer".into())
                    })?;
                    (
                        &self.announcement_base_url,
                        "/bapi/composite/v1/public/composite/ae/announcement/get",
                        HttpMethod::Get,
                        &["id"],
                        None,
                    )
                }
                "search_announcements" => {
                    let number = |key| -> Result<u64> {
                        let n = params.required(key)?.parse::<u64>().map_err(|_| {
                            DcexError::InvalidInput(format!("{key} must be positive"))
                        })?;
                        if n == 0 {
                            return Err(DcexError::InvalidInput(format!("{key} must be positive")));
                        }
                        Ok(n)
                    };
                    let mut body = json!({"page":number("page")?,"size":number("size")?});
                    if let Some(category) = params.get("category") {
                        if !["ACTIVITY", "NEW_LISTING", "DELISTING", "UPDATES"].contains(&category)
                        {
                            return Err(DcexError::InvalidInput(
                                "invalid announcement category".into(),
                            ));
                        }
                        body["category"] = category.into();
                    }
                    (
                        &self.announcement_base_url,
                        "/bapi/composite/v1/public/composite/ae/announcement/search",
                        HttpMethod::Post,
                        &["page", "size", "category"],
                        Some(body),
                    )
                }
                _ => return Ok(None),
            };
        params.ensure_allowed(fields, &[])?;
        let mut request = HttpRequest::new(method, base, path);
        if let Some(body) = body {
            request = request.json(body);
        } else {
            request.query = params.only(fields);
        }
        let response = self.transport.execute(request).await?;
        let data = validate_response(&response)?;
        Ok(Some(ValidatedResponse {
            status: response.status,
            headers: response.headers,
            data,
        }))
    }

    pub fn with_prediction_base_url(mut self, url: String) -> Result<Self> {
        if url.trim().is_empty() {
            return Err(DcexError::InvalidInput(
                "prediction base URL cannot be empty".into(),
            ));
        }
        self.prediction_base_url = url.trim_end_matches('/').into();
        Ok(self)
    }
    pub(super) async fn prediction_request(
        &self,
        method: HttpMethod,
        path: &str,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let mut client = self.clone();
        client.spot_base_url = self.prediction_base_url.clone();
        client
            .request(method, AsterMarket::Spot, path, params, signed)
            .await
    }

    pub(super) async fn prediction_noop(&self, nonce: u64) -> Result<ValidatedResponse> {
        let mut client = self.clone();
        client.spot_base_url = self.prediction_base_url.clone();
        client
            .signed_at_nonce(
                HttpMethod::Post,
                AsterMarket::Spot,
                "/api/v3/noop",
                vec![],
                Some(nonce),
            )
            .await
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

    pub async fn request_raw_auto(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let path = path.into();
        let market = AsterMarket::from_path(&path)?;
        self.request_raw(method, market, path, params, signed).await
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

    pub fn request_raw_auto_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move { client.request_raw_auto(method, path, params, signed).await })
    }

    pub(super) fn build_request(
        &self,
        method: HttpMethod,
        market: AsterMarket,
        path: impl Into<String>,
        mut params: Vec<(String, String)>,
        signed: bool,
        nonce: Option<u64>,
    ) -> Result<HttpRequest> {
        let path = path.into();
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
            let nonce = match nonce {
                Some(nonce) => {
                    // Guarded cancellation authenticates with the original order's
                    // nonce, even when that order has rested for more than a minute.
                    let original_order_nonce = method == HttpMethod::Delete
                        && market == AsterMarket::Futures
                        && matches!(
                            path.as_str(),
                            "/fapi/v3/guardedCancelOrder" | "/fapi/v3/guardedBatchOrders"
                        );
                    if !original_order_nonce {
                        validate_nonce_window(nonce)?;
                        self.last_nonce.fetch_max(nonce, Ordering::Relaxed);
                    }
                    nonce
                }
                None => self.next_nonce()?,
            };
            params.push(("nonce".to_string(), nonce.to_string()));
            if market == AsterMarket::Futures {
                let user_address = self.user_address.as_deref().ok_or_else(|| {
                    DcexError::InvalidInput(
                        "Signed Aster futures requests require user_address.".to_string(),
                    )
                })?;
                params.push(("user".to_string(), user_address.to_string()));
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

    pub(super) async fn signed_at_nonce(
        &self,
        method: HttpMethod,
        market: AsterMarket,
        path: &str,
        params: Vec<(String, String)>,
        nonce: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let request = self.build_request(method, market, path, params, true, nonce)?;
        let response = self.transport.execute(request).await?;
        let data = validate_response(&response)?;
        Ok(ValidatedResponse {
            status: response.status,
            headers: response.headers,
            data,
        })
    }

    /// Transfers within one master/sub-account family using the approved agent.
    /// Not verified live: the official V3 parameter table specifies `signer`, but
    /// its generic signing template also includes `user`. This implementation
    /// follows the endpoint table pending an authoritative signed example.
    /// https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
    pub(super) async fn sub_account_transfer(
        &self,
        params: &super::params::AsterParams,
    ) -> Result<ValidatedResponse> {
        let signer = self.signer_address.as_deref().ok_or_else(|| {
            DcexError::InvalidInput(
                "Aster sub-account transfers require an approved signer.".into(),
            )
        })?;
        let key = self.private_key.as_ref().ok_or_else(|| {
            DcexError::InvalidInput(
                "Aster sub-account transfers require the signer private key.".into(),
            )
        })?;
        let mut pairs = params.only(&["toAccountAddress", "asset", "amount", "kindType"]);
        pairs.push(("nonce".into(), self.next_nonce()?.to_string()));
        pairs.push(("signer".into(), signer.into()));
        pairs.extend(params.only(&["fromAccountAddress"]));
        let signature = sign_message(&encode_params(&pairs), key)?;
        pairs.push(("signature".into(), signature));
        // Already signed in this endpoint's specified field order.
        self.request(
            HttpMethod::Post,
            AsterMarket::Futures,
            "/fapi/v3/subAccountTransfer",
            pairs,
            false,
        )
        .await
    }

    /// Reserve a unique microsecond nonce; pass it to the order and its guarded cancel.
    pub fn reserve_nonce(&self) -> Result<u64> {
        let nonce = self.next_nonce()?;
        validate_nonce_window(nonce)?;
        Ok(nonce)
    }

    fn next_nonce(&self) -> Result<u64> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_err(|error| DcexError::Runtime(error.to_string()))?
            .as_nanos()
            / 1_000;
        let now = u64::try_from(now).unwrap_or(u64::MAX);
        let nonce = self
            .last_nonce
            .fetch_update(Ordering::Relaxed, Ordering::Relaxed, |previous| {
                Some(now.max(previous.saturating_add(1)))
            })
            .map(|previous| now.max(previous.saturating_add(1)))
            .unwrap_or(now);
        validate_nonce_window(nonce)?;
        Ok(nonce)
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if !product_symbol.contains('-') {
            return Ok(product_symbol.to_string());
        }
        if let Some(table) = &self.product_table {
            return table.get_exchange_symbol("aster", product_symbol);
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }
}

pub(super) fn validate_wallet_address(label: &str, value: &str) -> Result<()> {
    let value = value.trim();
    if value.len() != 42
        || !value.starts_with("0x")
        || !value[2..]
            .chars()
            .all(|character| character.is_ascii_hexdigit())
    {
        return Err(DcexError::InvalidInput(format!(
            "Aster {label} must be a 0x-prefixed 20-byte hexadecimal address."
        )));
    }
    Ok(())
}

fn exchange_symbol_fallback(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{quote}"),
        _ => product_symbol.to_string(),
    }
}

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    response.ensure_success()?;
    if let Some(object) = data.as_object() {
        let code = object.get("code");
        if object.get("success") == Some(&Value::Bool(false))
            || code.is_some_and(|code| {
                !matches!(json_value_string(code).as_str(), "0" | "000000" | "200")
            })
        {
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

fn validate_nonce_window(nonce: u64) -> Result<()> {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|error| DcexError::Runtime(error.to_string()))?
        .as_micros();
    if now.abs_diff(u128::from(nonce)) > 60_000_000 {
        return Err(DcexError::InvalidInput(
            "Aster nonce must be within 60 seconds of current time (microseconds)".into(),
        ));
    }
    Ok(())
}

#[cfg(test)]
mod review_nonce_tests {
    use super::*;

    fn signed_client() -> AsterClient {
        AsterClient::with_base_urls(
            Some(format!("0x{}", "22".repeat(20))),
            Some(format!("0x{}", "33".repeat(20))),
            Some(format!("0x{}", "11".repeat(32))),
            Duration::from_secs(1),
            "http://127.0.0.1:1".into(),
            "http://127.0.0.1:1".into(),
        )
        .unwrap()
    }

    #[test]
    fn explicit_nonce_advances_shared_counter_and_rejects_outside_window() {
        let client = signed_client();
        let future = client.reserve_nonce().unwrap() + 30_000_000;
        client
            .build_request(
                HttpMethod::Post,
                AsterMarket::Futures,
                "/fapi/v3/noop",
                vec![],
                true,
                Some(future),
            )
            .unwrap();
        assert!(client.reserve_nonce().unwrap() > future);
        for invalid in [1, future + 120_000_000] {
            let error = client
                .build_request(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    "/fapi/v3/noop",
                    vec![],
                    true,
                    Some(invalid),
                )
                .unwrap_err();
            assert!(error.to_string().contains("within 60 seconds"));
        }
    }

    #[test]
    fn concurrent_reservations_do_not_collide() {
        let client = signed_client();
        let values: Vec<_> = std::thread::scope(|scope| {
            let tasks: Vec<_> = (0..16)
                .map(|_| {
                    scope.spawn(|| {
                        (0..100)
                            .map(|_| client.reserve_nonce().unwrap())
                            .collect::<Vec<_>>()
                    })
                })
                .collect();
            tasks
                .into_iter()
                .flat_map(|task| task.join().unwrap())
                .collect()
        });
        let unique: std::collections::HashSet<_> = values.iter().collect();
        assert_eq!(unique.len(), 1600);
    }

    #[test]
    fn automatic_nonce_rejects_counter_outside_time_window() {
        let client = signed_client();
        client.last_nonce.store(u64::MAX - 1, Ordering::Relaxed);
        assert!(
            client
                .next_nonce()
                .unwrap_err()
                .to_string()
                .contains("within 60 seconds")
        );
    }
}
