use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde_json::Value;

use crate::http::{AsyncHttpClient, HttpRequest, HttpResponse};
use crate::{DcexError, Result};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Exchange {
    Arcus,
    Aster,
    Backpack,
    Binance,
    BingX,
    Bitget,
    Bybit,
    Extended,
    Hyperliquid,
    Kraken,
    KuCoin,
    Lighter,
    Mexc,
    Okx,
    Ondo,
}

impl Exchange {
    pub const ALL: [Self; 15] = [
        Self::Arcus,
        Self::Aster,
        Self::Backpack,
        Self::Binance,
        Self::BingX,
        Self::Bitget,
        Self::Bybit,
        Self::Extended,
        Self::Hyperliquid,
        Self::KuCoin,
        Self::Kraken,
        Self::Lighter,
        Self::Mexc,
        Self::Okx,
        Self::Ondo,
    ];

    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Arcus => "arcus",
            Self::Aster => "aster",
            Self::Backpack => "backpack",
            Self::Binance => "binance",
            Self::BingX => "bingx",
            Self::Bitget => "bitget",
            Self::Bybit => "bybit",
            Self::Extended => "extended",
            Self::Hyperliquid => "hyperliquid",
            Self::Kraken => "kraken",
            Self::KuCoin => "kucoin",
            Self::Lighter => "lighter",
            Self::Mexc => "mexc",
            Self::Okx => "okx",
            Self::Ondo => "ondo",
        }
    }
}

pub trait RequestSigner: Send + Sync {
    fn sign(&self, request: &mut HttpRequest, timestamp_ms: u64) -> Result<()>;
}

pub trait ResponseValidator: Send + Sync {
    fn validate(&self, response: &HttpResponse) -> Result<Value>;
}

#[derive(Clone)]
pub struct ExchangeHttpClient {
    transport: AsyncHttpClient,
    signer: Option<Arc<dyn RequestSigner>>,
    validator: Arc<dyn ResponseValidator>,
}

impl ExchangeHttpClient {
    pub fn new(timeout: Duration, validator: Arc<dyn ResponseValidator>) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            signer: None,
            validator,
        })
    }

    pub fn with_signer(mut self, signer: Arc<dyn RequestSigner>) -> Self {
        self.signer = Some(signer);
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

/// Corrects signed WebSocket timestamps with an exchange's REST time endpoint, fetched once
/// before the first signed message, as the REST clients do. Without a URL it is the local
/// clock (custom or test endpoints).
pub(crate) struct ServerClock {
    url: Option<String>,
    extract: fn(&serde_json::Value) -> Option<u64>,
    offset_ms: std::sync::Mutex<Option<i64>>,
}

impl ServerClock {
    pub(crate) fn new(url: Option<String>, extract: fn(&serde_json::Value) -> Option<u64>) -> Self {
        Self {
            url,
            extract,
            offset_ms: std::sync::Mutex::new(None),
        }
    }

    #[cfg(test)]
    pub(crate) fn url(&self) -> Option<&str> {
        self.url.as_deref()
    }

    pub(crate) fn set_url(&mut self, url: Option<String>) {
        self.url = url;
        *self
            .offset_ms
            .get_mut()
            .unwrap_or_else(|poison| poison.into_inner()) = None;
    }

    pub(crate) async fn sync(&self, exchange: &str, timeout: std::time::Duration) -> Result<()> {
        let Some(url) = &self.url else {
            return Ok(());
        };
        if self.offset()?.is_some() {
            return Ok(());
        }
        let client = crate::http::AsyncHttpClient::new(timeout)?;
        let request = crate::http::HttpRequest::new(crate::http::HttpMethod::Get, url, "");
        let start = unix_timestamp_ms()?;
        let response = client.execute(request).await?;
        let end = unix_timestamp_ms()?;
        response.ensure_success(exchange)?;
        let server = (self.extract)(&response.json()?).ok_or_else(|| {
            DcexError::Decode(format!("{exchange} server time response missing its time"))
        })?;
        let midpoint = (start + end) / 2;
        *self.lock()? = Some(server as i64 - midpoint as i64);
        Ok(())
    }

    /// Local time corrected by the synced offset (the local clock before any sync).
    pub(crate) fn now_ms(&self) -> Result<u64> {
        let corrected = unix_timestamp_ms()? as i64 + self.offset()?.unwrap_or_default();
        Ok(corrected.max(0) as u64)
    }

    fn offset(&self) -> Result<Option<i64>> {
        Ok(*self.lock()?)
    }

    fn lock(&self) -> Result<std::sync::MutexGuard<'_, Option<i64>>> {
        self.offset_ms
            .lock()
            .map_err(|_| DcexError::Runtime("server clock offset lock poisoned".into()))
    }
}

pub fn exchange_names() -> Vec<&'static str> {
    Exchange::ALL.into_iter().map(Exchange::as_str).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exchange_registry_matches_python_registry() {
        assert_eq!(Exchange::ALL.len(), 15);
        assert_eq!(Exchange::Binance.as_str(), "binance");
        assert_eq!(Exchange::Lighter.as_str(), "lighter");
    }
}
