use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde_json::Value;

use crate::http::{AsyncHttpClient, HttpRequest, HttpResponse};
use crate::{DcexError, Result};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Exchange {
    Aster,
    Backpack,
    Binance,
    BingX,
    Bitget,
    BitMEX,
    Bybit,
    Extended,
    Hyperliquid,
    Kraken,
    KuCoin,
    Lighter,
    Mexc,
    Okx,
}

impl Exchange {
    pub const ALL: [Self; 14] = [
        Self::Aster,
        Self::Backpack,
        Self::Binance,
        Self::BingX,
        Self::Bitget,
        Self::BitMEX,
        Self::Bybit,
        Self::Extended,
        Self::Hyperliquid,
        Self::KuCoin,
        Self::Kraken,
        Self::Lighter,
        Self::Mexc,
        Self::Okx,
    ];

    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Aster => "aster",
            Self::Backpack => "backpack",
            Self::Binance => "binance",
            Self::BingX => "bingx",
            Self::Bitget => "bitget",
            Self::BitMEX => "bitmex",
            Self::Bybit => "bybit",
            Self::Extended => "extended",
            Self::Hyperliquid => "hyperliquid",
            Self::Kraken => "kraken",
            Self::KuCoin => "kucoin",
            Self::Lighter => "lighter",
            Self::Mexc => "mexc",
            Self::Okx => "okx",
        }
    }
}

pub trait RequestSigner: Send + Sync {
    fn sign(&self, request: &mut HttpRequest, timestamp_ms: u64) -> Result<()>;
}

pub trait ResponseValidator: Send + Sync {
    fn validate(&self, response: &HttpResponse) -> Result<Value>;
}

#[derive(Default)]
pub struct JsonResponseValidator;

impl ResponseValidator for JsonResponseValidator {
    fn validate(&self, response: &HttpResponse) -> Result<Value> {
        response.ensure_success()?;
        response.json()
    }
}

#[derive(Clone)]
pub struct ExchangeHttpClient {
    transport: AsyncHttpClient,
    signer: Option<Arc<dyn RequestSigner>>,
    validator: Arc<dyn ResponseValidator>,
}

impl ExchangeHttpClient {
    pub fn new(timeout: Duration) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            signer: None,
            validator: Arc::new(JsonResponseValidator),
        })
    }

    pub fn with_signer(mut self, signer: Arc<dyn RequestSigner>) -> Self {
        self.signer = Some(signer);
        self
    }

    pub fn with_validator(mut self, validator: Arc<dyn ResponseValidator>) -> Self {
        self.validator = validator;
        self
    }

    pub async fn execute(&self, request: HttpRequest, signed: bool) -> Result<ValidatedResponse> {
        let response = self.execute_raw(request, signed).await?;
        let data = self.validator.validate(&response)?;
        Ok(ValidatedResponse {
            status: response.status,
            headers: response.headers,
            data,
        })
    }

    pub async fn execute_raw(
        &self,
        mut request: HttpRequest,
        signed: bool,
    ) -> Result<HttpResponse> {
        if signed {
            let signer = self.signer.as_ref().ok_or_else(|| {
                DcexError::InvalidInput("signed request requires credentials".to_string())
            })?;
            signer.sign(&mut request, unix_timestamp_ms()?)?;
        }
        self.transport.execute(request).await
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct ValidatedResponse {
    pub status: u16,
    pub headers: std::collections::BTreeMap<String, String>,
    pub data: Value,
}

pub fn unix_timestamp_ms() -> Result<u64> {
    let duration = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|error| DcexError::Runtime(error.to_string()))?;
    u64::try_from(duration.as_millis()).map_err(|error| DcexError::Runtime(error.to_string()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exchange_registry_matches_python_registry() {
        assert_eq!(Exchange::ALL.len(), 14);
        assert_eq!(Exchange::Binance.as_str(), "binance");
        assert_eq!(Exchange::Lighter.as_str(), "lighter");
    }
}
