//! Arcus api-meta routes. Preference writes require the signed header triple.
use super::{
    ArcusClient,
    signing::{legacy_signing_message, timestamp_ns},
};
use crate::exchange::ValidatedResponse;
use crate::http::{HttpMethod, HttpRequest};
use crate::{DcexError, Result};
use ed25519_dalek::Signer;
use serde_json::Value;
use std::collections::BTreeMap;
fn invalid(s: &str) -> DcexError {
    DcexError::InvalidInput(format!("Arcus: {s}"))
}
const KEYS: &[&str] = &[
    "favoritedMarkets",
    "favoritePerpMarkets",
    "favoriteSpotMarkets",
    "subaccountPreferences",
    "perpsLayout",
    "spotLayout",
    "language",
    "numberRepresentation",
    "disabledAlerts",
    "colorTheme",
    "colorRedGreen",
    "lastSignedTOS",
    "isSpotLayoutLocked",
    "isPerpLayoutLocked",
    "isSpotLayoutFlex",
    "isPerpLayoutFlex",
];
pub(super) fn handles(name: &str, public: bool) -> bool {
    public
        != matches!(
            name,
            "upsert_user_preferences" | "delete_user_preference_signed"
        )
        && matches!(
            name,
            "get_market_metadata"
                | "get_market_overview"
                | "get_spot_market_overview"
                | "get_metadata_candles"
                | "get_user_preferences"
                | "upsert_user_preferences"
                | "delete_user_preference_signed"
        )
}
fn preferences(body: &Value) -> Result<()> {
    let obj = body
        .as_object()
        .ok_or_else(|| invalid("preferences must be an object"))?;
    if obj.is_empty()
        || obj.len() > 64
        || serde_json::to_vec(body)
            .map_err(|_| invalid("invalid JSON"))?
            .len()
            > 128 * 1024
    {
        return Err(invalid("preferences exceed documented size limits"));
    }
    for (k, v) in obj {
        if !KEYS.contains(&k.as_str()) {
            return Err(invalid("unknown preference key"));
        }
        let valid = match k.as_str() {
            "favoritedMarkets" => v
                .as_array()
                .is_some_and(|a| a.iter().all(|x| x.as_u64().is_some())),
            "favoritePerpMarkets" | "favoriteSpotMarkets" => v
                .as_array()
                .is_some_and(|a| a.iter().all(|x| x.is_string())),
            "disabledAlerts" => {
                v.is_string()
                    || v.as_array()
                        .is_some_and(|a| a.iter().all(|x| x.is_string() || x.is_i64()))
            }
            "lastSignedTOS" => v.as_u64().is_some(),
            "isSpotLayoutLocked" | "isPerpLayoutLocked" | "isSpotLayoutFlex"
            | "isPerpLayoutFlex" => v.is_boolean(),
            "subaccountPreferences" => v.as_object().is_some_and(|a| {
                a.len() <= 256
                    && a.iter().all(|(id, v)| {
                        id.parse::<u64>().is_ok()
                            && v.as_object().is_some_and(|x| {
                                x.len() == 1
                                    && x.get("name")
                                        .and_then(Value::as_str)
                                        .is_some_and(|s| s.chars().count() <= 64)
                            })
                    })
            }),
            _ => v.is_string(),
        };
        if !valid {
            return Err(invalid("invalid preference value type"));
        }
    }
    Ok(())
}
impl ArcusClient {
    pub(super) async fn metadata_request(
        &self,
        name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let mut p = BTreeMap::new();
        for (key, value) in params {
            if p.insert(key, value).is_some() {
                return Err(invalid("duplicate parameter"));
            }
        }
        let (path, allowed): (&str, &[&str]) = match name {
            "get_market_metadata" => ("/v1/api-meta/markets", &["market"]),
            "get_market_overview" => ("/v1/api-meta/overview", &[]),
            "get_spot_market_overview" => ("/v1/api-meta/spot/overview", &[]),
            "get_metadata_candles" => (
                "/v1/api-meta/candles",
                &["market", "timeframe", "from", "to", "countback"],
            ),
            "get_user_preferences" => ("/v1/api-meta/userPreferences", &["address"]),
            "upsert_user_preferences" => ("/v1/api-meta/userPreferences", &["preferences"]),
            "delete_user_preference_signed" => (
                "/v1/api-meta/userPreferences",
                &["key", "timestamp", "signature"],
            ),
            _ => return Err(invalid("unknown metadata method")),
        };
        if p.iter()
            .any(|(k, v)| !allowed.contains(&k.as_str()) || v.is_empty())
        {
            return Err(invalid("unknown or empty parameter"));
        }
        if name == "get_user_preferences" {
            let address = p
                .get("address")
                .map(String::as_str)
                .or(self.address.as_deref())
                .ok_or_else(|| invalid("address is required"))?;
            if address.len() != 42
                || !address.starts_with("0x")
                || !address[2..].bytes().all(|b| b.is_ascii_hexdigit())
            {
                return Err(invalid("invalid address"));
            }
            p.insert("address".into(), address.to_string());
        }
        if name == "get_metadata_candles" {
            for key in ["market", "timeframe", "to"] {
                if !p.contains_key(key) {
                    return Err(invalid("market, timeframe and to are required"));
                }
            }
            if !p.contains_key("from") && !p.contains_key("countback") {
                return Err(invalid("from or countback is required"));
            }
            for key in ["from", "to"] {
                if p.get(key)
                    .is_some_and(|s| !s.parse::<u64>().is_ok_and(|v| v < 100_000_000_000))
                {
                    return Err(invalid("metadata candle timestamps must be seconds"));
                }
            }
            if p.get("countback")
                .is_some_and(|s| !s.parse::<u64>().is_ok_and(|v| (1..=1500).contains(&v)))
            {
                return Err(invalid("countback must be 1..1500"));
            }
            if !p.contains_key("countback")
                && p.get("from").and_then(|s| s.parse::<u64>().ok())
                    > p.get("to").and_then(|s| s.parse::<u64>().ok())
            {
                return Err(invalid("from must not exceed to"));
            }
        }
        let mut request = HttpRequest::new(HttpMethod::Get, &self.base_url, path);
        if name == "upsert_user_preferences" {
            let body: Value = serde_json::from_str(
                p.get("preferences")
                    .ok_or_else(|| invalid("preferences are required"))?,
            )
            .map_err(|_| invalid("invalid preferences JSON"))?;
            preferences(&body)?;
            let key = self
                .signing_key
                .as_ref()
                .ok_or_else(|| invalid("API signing key is required"))?;
            let timestamp = timestamp_ns()?;
            let canonical: BTreeMap<String, Value> = body
                .as_object()
                .expect("validated object")
                .iter()
                .map(|(k, v)| (k.clone(), v.clone()))
                .collect();
            let signature = hex::encode(
                key.sign(&legacy_signing_message(
                    timestamp,
                    "userPreferences",
                    &canonical,
                )?)
                .to_bytes(),
            );
            request = HttpRequest::new(HttpMethod::Patch, &self.base_url, path)
                .json(body)
                .header("X-API-Key", hex::encode(key.verifying_key().to_bytes()))
                .header("X-Timestamp", timestamp.to_string())
                .header("X-Signature", signature);
        } else if name == "delete_user_preference_signed" {
            // The query-only DELETE canonical message is not specified unambiguously.
            // Forward caller-provided signing headers without inventing signing semantics.
            let key = p
                .get("key")
                .filter(|k| KEYS.contains(&k.as_str()))
                .ok_or_else(|| invalid("known preference key is required"))?;
            let timestamp = p
                .get("timestamp")
                .filter(|s| s.parse::<u64>().is_ok_and(|v| v > 0))
                .ok_or_else(|| invalid("nanosecond timestamp is required"))?;
            let signature = p
                .get("signature")
                .filter(|s| s.len() == 128 && s.bytes().all(|b| b.is_ascii_hexdigit()))
                .ok_or_else(|| invalid("128-character signature is required"))?;
            let api_key = self
                .api_key
                .as_ref()
                .ok_or_else(|| invalid("API key is required"))?;
            request = HttpRequest::new(HttpMethod::Delete, &self.base_url, path)
                .header("X-API-Key", api_key)
                .header("X-Timestamp", timestamp)
                .header("X-Signature", signature);
            request.query = vec![("key".into(), key.clone())];
        } else {
            request.query = p.into_iter().collect();
        }
        self.execute(request).await
    }
}
