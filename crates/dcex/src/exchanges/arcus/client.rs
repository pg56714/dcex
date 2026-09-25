//! Arcus perpetuals and Spot RFQ HTTP clients.

pub use spot::ArcusSpotClient;

use std::time::Duration;

use ed25519_dalek::SigningKey;

use super::endpoints::{MAINNET_URL, TESTNET_URL};
use crate::exchange::ValidatedResponse;
use crate::http::{AsyncHttpClient, HttpRequest};
use crate::{DcexError, Result};

#[derive(Clone)]
pub struct ArcusClient {
    pub(super) transport: AsyncHttpClient,
    pub(super) base_url: String,
    pub(super) address: Option<String>,
    pub(super) account_index: u8,
    pub(super) signing_key: Option<SigningKey>,
    pub(super) api_key: Option<String>,
}

impl ArcusClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        address: Option<String>,
        account_index: u8,
        testnet: bool,
        timeout: Duration,
    ) -> Result<Self> {
        if account_index > 9 {
            return Err(DcexError::InvalidInput(
                "Arcus account_index must be 0–9".into(),
            ));
        }
        let signing_key = api_secret
            .as_deref()
            .map(|secret| {
                let bytes = hex::decode(secret.trim_start_matches("0x"))
                    .map_err(|_| DcexError::InvalidInput("invalid Arcus API secret hex".into()))?;
                let bytes: [u8; 32] = bytes.try_into().map_err(|_| {
                    DcexError::InvalidInput("Arcus API secret must be 32 bytes".into())
                })?;
                Ok(SigningKey::from_bytes(&bytes))
            })
            .transpose()?;
        let derived_key = signing_key
            .as_ref()
            .map(|key| hex::encode(key.verifying_key().to_bytes()));
        if let (Some(configured), Some(derived)) = (&api_key, &derived_key) {
            if !configured.eq_ignore_ascii_case(derived) {
                return Err(DcexError::InvalidInput(
                    "Arcus API key does not match signing key".into(),
                ));
            }
        }
        let api_key = derived_key.or(api_key);
        let address = address
            .map(|address| {
                let address = address.to_ascii_lowercase();
                if address.len() == 42
                    && address.starts_with("0x")
                    && address[2..].bytes().all(|byte| byte.is_ascii_hexdigit())
                {
                    Ok(address)
                } else {
                    Err(DcexError::InvalidInput(
                        "invalid Arcus wallet address".into(),
                    ))
                }
            })
            .transpose()?;
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url: if testnet { TESTNET_URL } else { MAINNET_URL }.into(),
            address,
            account_index,
            signing_key,
            api_key,
        })
    }

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, None, 0, false, timeout)
    }

    pub fn with_base_url(mut self, base_url: String) -> Result<Self> {
        let url = url::Url::parse(&base_url)
            .map_err(|_| DcexError::InvalidInput("invalid Arcus base URL".into()))?;
        if !matches!(url.scheme(), "https" | "http") {
            return Err(DcexError::InvalidInput(
                "Arcus base URL must use HTTP(S)".into(),
            ));
        }
        self.base_url = base_url;
        Ok(self)
    }

    pub(super) async fn execute(&self, request: HttpRequest) -> Result<ValidatedResponse> {
        let response = self.transport.execute(request).await?;
        response.ensure_success()?;
        let data = response.json()?;
        Ok(ValidatedResponse {
            status: response.status,
            headers: response.headers,
            data,
        })
    }
}

mod spot {
    //! Arcus spot RFQ router. Trade signing uses an EVM wallet, not the perps API key.

    use std::collections::BTreeMap;
    use std::time::Duration;

    use serde_json::Value;

    use crate::exchange::ValidatedResponse;
    use crate::http::{AsyncHttpClient, HttpMethod, HttpRequest};
    use crate::{DcexError, Result};

    const MAINNET_URL: &str = "https://router.spot.arcus.xyz";
    const TESTNET_URL: &str = "https://router.spot.testnet.arcus.xyz";

    #[derive(Clone)]
    pub struct ArcusSpotClient {
        pub(in crate::exchanges::arcus) transport: AsyncHttpClient,
        base_url: String,
        pub(in crate::exchanges::arcus) chain_id: u64,
        api_key: Option<String>,
        pub(in crate::exchanges::arcus) rpc_url: String,
        pub(in crate::exchanges::arcus) wallet_address: Option<String>,
    }

    impl ArcusSpotClient {
        pub fn new(api_key: Option<String>, testnet: bool, timeout: Duration) -> Result<Self> {
            Ok(Self {
                transport: AsyncHttpClient::new(timeout)?,
                base_url: if testnet { TESTNET_URL } else { MAINNET_URL }.into(),
                chain_id: if testnet { 46630 } else { 4663 },
                api_key,
                rpc_url: if testnet {
                    "https://rpc.testnet.chain.robinhood.com"
                } else {
                    "https://rpc.mainnet.chain.robinhood.com"
                }
                .into(),
                wallet_address: None,
            })
        }

        pub fn with_rpc_url(mut self, rpc_url: String) -> Result<Self> {
            let url = url::Url::parse(&rpc_url)
                .map_err(|_| DcexError::InvalidInput("invalid Arcus wallet RPC URL".into()))?;
            if !matches!(url.scheme(), "https" | "http") || url.host_str().is_none() {
                return Err(DcexError::InvalidInput(
                    "Arcus wallet RPC URL must use HTTP(S)".into(),
                ));
            }
            self.rpc_url = rpc_url;
            Ok(self)
        }

        pub fn with_wallet_address(mut self, address: String) -> Result<Self> {
            validate_address(&address)?;
            self.wallet_address = Some(address);
            Ok(self)
        }

        pub fn with_base_url(mut self, base_url: String) -> Result<Self> {
            let url = url::Url::parse(&base_url)
                .map_err(|_| DcexError::InvalidInput("invalid Arcus spot router URL".into()))?;
            if !matches!(url.scheme(), "https" | "http") {
                return Err(DcexError::InvalidInput(
                    "Arcus spot router URL must use HTTP(S)".into(),
                ));
            }
            self.base_url = base_url
                .trim_end_matches('/')
                .trim_end_matches("/v1")
                .into();
            Ok(self)
        }

        pub fn chain_id(&self) -> u64 {
            self.chain_id
        }

        /// Assemble the Arcus `/v1/submit` body from a firm quote and a signature
        /// produced by the caller's EVM wallet.
        pub fn build_signed_quote(
            &self,
            quote: Value,
            taker: &str,
            signature: &str,
            permits: Option<Value>,
            route_tag: Option<&str>,
        ) -> Result<Value> {
            self.build_signed_quote_with_fee(quote, taker, signature, permits, route_tag, None)
        }

        pub fn build_signed_quote_with_fee(
            &self,
            quote: Value,
            taker: &str,
            signature: &str,
            permits: Option<Value>,
            route_tag: Option<&str>,
            builder_fee_bps: Option<u16>,
        ) -> Result<Value> {
            validate_address(taker)?;
            validate_hex(signature, 65)?;
            let quote = quote.as_object().ok_or_else(|| {
                DcexError::InvalidInput("Arcus spot firm quote must be a JSON object".into())
            })?;
            if quote.get("venue").and_then(Value::as_str) != Some("arcus") {
                return Err(DcexError::InvalidInput(
                    "Arcus spot firm quote venue must be arcus".into(),
                ));
            }
            let typed_data = quote.get("toSign").cloned().ok_or_else(|| {
                DcexError::InvalidInput("Arcus spot firm quote toSign is required".into())
            })?;
            validate_typed_data(&typed_data, self.chain_id)?;

            let mut body = serde_json::Map::new();
            body.insert("venue".into(), Value::String("arcus".into()));
            body.insert("chainId".into(), Value::from(self.chain_id));
            body.insert("taker".into(), Value::String(taker.into()));
            body.insert("typedData".into(), typed_data);
            body.insert("signature".into(), Value::String(signature.into()));
            if let Some(permits) = permits {
                if !permits.is_array() {
                    return Err(DcexError::InvalidInput(
                        "Arcus spot permits must be a JSON array".into(),
                    ));
                }
                body.insert("permits".into(), permits);
            }
            if let Some(route_tag) = route_tag {
                if route_tag.trim().is_empty() {
                    return Err(DcexError::InvalidInput(
                        "Arcus spot routeTag must not be empty".into(),
                    ));
                }
                body.insert("routeTag".into(), Value::String(route_tag.into()));
            }
            if let Some(bps) = builder_fee_bps {
                self.validate_builder_fee(bps)?;
                body.insert("builderFeeBps".into(), Value::from(bps));
            }
            Ok(Value::Object(body))
        }

        pub async fn public_request(
            &self,
            method_name: &str,
            params: Vec<(String, String)>,
        ) -> Result<ValidatedResponse> {
            if matches!(
                method_name,
                "get_native_balance"
                    | "get_token_balance"
                    | "get_allowance"
                    | "get_balances"
                    | "get_transaction_receipt"
                    | "get_block_number"
                    | "get_trade_history"
            ) {
                return self.wallet_request(method_name, params).await;
            }
            self.router_request(method_name, params).await
        }

        pub(in crate::exchanges::arcus) async fn router_request(
            &self,
            method_name: &str,
            params: Vec<(String, String)>,
        ) -> Result<ValidatedResponse> {
            let values: BTreeMap<_, _> = params.into_iter().collect();
            let (path, query) = match method_name {
                "health" => {
                    ensure_allowed(&values, &[])?;
                    ("/health", Vec::new())
                }
                "get_tokens" => {
                    ensure_allowed(&values, &[])?;
                    ("/v1/tokens", Vec::new())
                }
                "get_price" | "get_quote" => {
                    let allowed = if method_name == "get_quote" {
                        &[
                            "chainId",
                            "sellToken",
                            "buyToken",
                            "sellAmount",
                            "taker",
                            "slippageBps",
                            "allowWrapped",
                            "builderFeeBps",
                        ][..]
                    } else {
                        &[
                            "chainId",
                            "sellToken",
                            "buyToken",
                            "sellAmount",
                            "builderFeeBps",
                        ][..]
                    };
                    ensure_allowed(&values, allowed)?;
                    let sell = required(&values, "sellToken")?;
                    let buy = required(&values, "buyToken")?;
                    validate_address(sell)?;
                    validate_address(buy)?;
                    if sell.eq_ignore_ascii_case(buy) {
                        return Err(DcexError::InvalidInput(
                            "Arcus spot sellToken and buyToken must differ".into(),
                        ));
                    }
                    validate_positive_atoms(required(&values, "sellAmount")?)?;
                    if let Some(fee) = values.get("builderFeeBps") {
                        let bps = fee.parse::<u16>().map_err(|_| {
                            DcexError::InvalidInput("invalid Arcus spot builderFeeBps".into())
                        })?;
                        self.validate_builder_fee(bps)?;
                    }
                    if method_name == "get_quote" {
                        validate_address(required(&values, "taker")?)?;
                        if let Some(slippage) = values.get("slippageBps") {
                            let bps = slippage.parse::<u16>().map_err(|_| {
                                DcexError::InvalidInput("invalid Arcus spot slippageBps".into())
                            })?;
                            if bps > 10_000 {
                                return Err(DcexError::InvalidInput(
                                    "Arcus spot slippageBps must be at most 10000".into(),
                                ));
                            }
                        }
                        if values
                            .get("allowWrapped")
                            .is_some_and(|v| v != "true" && v != "false")
                        {
                            return Err(DcexError::InvalidInput(
                                "Arcus spot allowWrapped must be true or false".into(),
                            ));
                        }
                    }
                    (
                        if method_name == "get_quote" {
                            "/v1/quote"
                        } else {
                            "/v1/price"
                        },
                        self.query(values)?,
                    )
                }
                "get_status" => {
                    ensure_allowed(&values, &["venue", "id", "chainId"])?;
                    if required(&values, "venue")? != "arcus" {
                        return Err(DcexError::InvalidInput(
                            "Arcus spot status venue must be arcus".into(),
                        ));
                    }
                    validate_hex(required(&values, "id")?, 32)?;
                    ("/v1/status", self.query(values)?)
                }
                _ => {
                    return Err(DcexError::InvalidInput(format!(
                        "unknown Arcus spot public method: {method_name}"
                    )))
                }
            };
            let mut request = HttpRequest::new(HttpMethod::Get, &self.base_url, path);
            request.query = query;
            self.execute(request).await
        }

        pub async fn submit_signed_quote(&self, signed_quote: Value) -> Result<ValidatedResponse> {
            let object = signed_quote.as_object().ok_or_else(|| {
                DcexError::InvalidInput("Arcus spot signed quote must be a JSON object".into())
            })?;
            if object.get("venue").and_then(Value::as_str) != Some("arcus") {
                return Err(DcexError::InvalidInput(
                    "Arcus spot signed quote venue must be arcus".into(),
                ));
            }
            if object.get("chainId").and_then(Value::as_u64) != Some(self.chain_id) {
                return Err(DcexError::InvalidInput(
                    "Arcus spot signed quote chainId does not match selected network".into(),
                ));
            }
            let taker = object.get("taker").and_then(Value::as_str).ok_or_else(|| {
                DcexError::InvalidInput("Arcus spot signed quote taker is required".into())
            })?;
            validate_address(taker)?;
            let signature = object
                .get("signature")
                .and_then(Value::as_str)
                .ok_or_else(|| {
                    DcexError::InvalidInput("Arcus spot wallet signature is required".into())
                })?;
            validate_hex(signature, 65)?;
            let typed_data = object.get("typedData").ok_or_else(|| {
                DcexError::InvalidInput("Arcus spot typedData is required".into())
            })?;
            validate_typed_data(typed_data, self.chain_id)?;
            if object
                .get("permits")
                .is_some_and(|permits| !permits.is_array())
            {
                return Err(DcexError::InvalidInput(
                    "Arcus spot permits must be a JSON array".into(),
                ));
            }
            if let Some(fee) = object.get("builderFeeBps") {
                let bps = fee
                    .as_u64()
                    .and_then(|value| u16::try_from(value).ok())
                    .ok_or_else(|| {
                        DcexError::InvalidInput("invalid Arcus spot builderFeeBps".into())
                    })?;
                self.validate_builder_fee(bps)?;
            }
            let request =
                HttpRequest::new(HttpMethod::Post, &self.base_url, "/v1/submit").json(signed_quote);
            self.execute(request).await
        }

        pub async fn private_request(
            &self,
            method_name: &str,
            params: Vec<(String, String)>,
        ) -> Result<ValidatedResponse> {
            if method_name != "submit_signed_quote" {
                return Err(DcexError::InvalidInput(format!(
                    "unknown Arcus spot private method: {method_name}"
                )));
            }
            let values: BTreeMap<_, _> = params.into_iter().collect();
            ensure_allowed(&values, &["signed_quote_json"])?;
            let signed_quote = serde_json::from_str(required(&values, "signed_quote_json")?)
                .map_err(|error| {
                    DcexError::InvalidInput(format!("invalid signed quote JSON: {error}"))
                })?;
            self.submit_signed_quote(signed_quote).await
        }

        fn query(&self, mut values: BTreeMap<String, String>) -> Result<Vec<(String, String)>> {
            if let Some(chain_id) = values.get("chainId") {
                if chain_id.parse::<u64>().ok() != Some(self.chain_id) {
                    return Err(DcexError::InvalidInput(
                        "Arcus spot chainId does not match selected network".into(),
                    ));
                }
            } else {
                values.insert("chainId".into(), self.chain_id.to_string());
            }
            Ok(values.into_iter().collect())
        }

        fn validate_builder_fee(&self, bps: u16) -> Result<()> {
            if bps > 10_000 {
                return Err(DcexError::InvalidInput(
                    "Arcus spot builderFeeBps must be at most 10000".into(),
                ));
            }
            if bps > 0 && self.api_key.is_none() {
                return Err(DcexError::InvalidInput(
                    "Arcus spot builderFeeBps requires a router API key".into(),
                ));
            }
            Ok(())
        }

        async fn execute(&self, mut request: HttpRequest) -> Result<ValidatedResponse> {
            if let Some(api_key) = &self.api_key {
                request = request.header("X-Api-Key", api_key);
            }
            let response = self.transport.execute(request).await?;
            response.ensure_success()?;
            let data = response.json()?;
            Ok(ValidatedResponse {
                status: response.status,
                headers: response.headers,
                data,
            })
        }
    }

    fn ensure_allowed(values: &BTreeMap<String, String>, allowed: &[&str]) -> Result<()> {
        if let Some(key) = values.keys().find(|key| !allowed.contains(&key.as_str())) {
            return Err(DcexError::InvalidInput(format!(
                "unknown Arcus spot parameter: {key}"
            )));
        }
        Ok(())
    }

    fn required<'a>(values: &'a BTreeMap<String, String>, key: &str) -> Result<&'a str> {
        values
            .get(key)
            .map(String::as_str)
            .filter(|s| !s.is_empty())
            .ok_or_else(|| DcexError::InvalidInput(format!("Arcus spot {key} is required")))
    }

    fn validate_address(value: &str) -> Result<()> {
        validate_hex(value, 20)
    }

    fn validate_hex(value: &str, bytes: usize) -> Result<()> {
        if value.len() != bytes * 2 + 2
            || !value.starts_with("0x")
            || !value[2..].bytes().all(|c| c.is_ascii_hexdigit())
        {
            return Err(DcexError::InvalidInput(format!(
                "Arcus spot expected a {bytes}-byte 0x-prefixed hex value"
            )));
        }
        Ok(())
    }

    fn validate_positive_atoms(value: &str) -> Result<()> {
        if value.starts_with('0')
            || !value.bytes().all(|c| c.is_ascii_digit())
            || value.parse::<u128>().is_err()
        {
            return Err(DcexError::InvalidInput(
                "Arcus spot sellAmount must be a positive integer in token atoms".into(),
            ));
        }
        Ok(())
    }

    fn validate_typed_data(typed_data: &Value, chain_id: u64) -> Result<()> {
        if !typed_data.is_object()
            || typed_data["domain"]["chainId"].as_u64() != Some(chain_id)
            || typed_data["primaryType"].as_str() != Some("PermitWitnessTransferFrom")
        {
            return Err(DcexError::InvalidInput(
                "Arcus spot typedData must match the selected network and PermitWitnessTransferFrom"
                    .into(),
            ));
        }
        Ok(())
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn validates_spot_addresses_and_atomic_amounts() {
            assert!(validate_address(&format!("0x{}", "ab".repeat(20))).is_ok());
            assert!(validate_address("BTC-USD").is_err());
            assert!(validate_positive_atoms("1000000").is_ok());
            assert!(validate_positive_atoms("0").is_err());
            assert!(validate_positive_atoms("1.5").is_err());
        }

        #[test]
        fn builds_arcus_submit_body_from_external_wallet_signature() {
            let client = ArcusSpotClient::new(None, false, Duration::from_secs(1)).expect("client");
            let taker = format!("0x{}", "11".repeat(20));
            let signature = format!("0x{}", "22".repeat(65));
            let body = client
                .build_signed_quote(
                    serde_json::json!({
                        "venue": "arcus",
                        "toSign": {
                            "domain": {"chainId": 4663},
                            "primaryType": "PermitWitnessTransferFrom"
                        }
                    }),
                    &taker,
                    &signature,
                    Some(serde_json::json!([{"token": "permit"}])),
                    Some("strategy-a"),
                )
                .expect("signed quote");

            assert_eq!(body["chainId"], 4663);
            assert_eq!(body["taker"], taker);
            assert_eq!(body["signature"], signature);
            assert_eq!(body["permits"][0]["token"], "permit");
            assert_eq!(body["routeTag"], "strategy-a");
        }

        #[test]
        fn builder_fee_requires_separate_router_key() {
            let quote = serde_json::json!({
                "venue": "arcus",
                "toSign": {
                    "domain": {"chainId": 4663},
                    "primaryType": "PermitWitnessTransferFrom"
                }
            });
            let taker = format!("0x{}", "11".repeat(20));
            let signature = format!("0x{}", "22".repeat(65));
            let public = ArcusSpotClient::new(None, false, Duration::from_secs(1)).unwrap();
            assert!(public
                .build_signed_quote_with_fee(
                    quote.clone(),
                    &taker,
                    &signature,
                    None,
                    None,
                    Some(80),
                )
                .is_err());
            let partner =
                ArcusSpotClient::new(Some("router-key".into()), false, Duration::from_secs(1))
                    .unwrap();
            let body = partner
                .build_signed_quote_with_fee(quote, &taker, &signature, None, None, Some(80))
                .unwrap();
            assert_eq!(body["builderFeeBps"], 80);
        }
    }
}
