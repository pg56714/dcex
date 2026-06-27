use serde_json::{Map, Value};

use crate::{DcexError, Result};

pub(super) struct OkxParams(Vec<(String, String)>);

impl OkxParams {
    pub(super) fn from_pairs(params: Vec<(String, String)>) -> Self {
        Self(params)
    }

    pub(super) fn get(&self, key: &str) -> Option<&str> {
        self.0
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    pub(super) fn required(&self, key: &str) -> Result<&str> {
        self.get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
    }

    pub(super) fn only(&self, keys: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| keys.contains(&key.as_str()))
            .cloned()
            .collect()
    }

    pub(super) fn required_only(&self, keys: &[&str]) -> Result<Vec<(String, String)>> {
        keys.iter()
            .map(|key| Ok(((*key).to_string(), self.required(key)?.to_string())))
            .collect()
    }

    pub(super) fn without(&self, excluded: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| !excluded.contains(&key.as_str()))
            .cloned()
            .collect()
    }

    pub(super) fn body(&self, keys: &[&str]) -> Map<String, Value> {
        keys.iter()
            .filter_map(|key| {
                self.get(key)
                    .map(|value| ((*key).to_string(), Value::String(value.to_string())))
            })
            .collect()
    }

    pub(super) fn required_body(&self, keys: &[&str]) -> Result<Map<String, Value>> {
        keys.iter()
            .map(|key| {
                Ok((
                    (*key).to_string(),
                    Value::String(self.required(key)?.to_string()),
                ))
            })
            .collect()
    }

    pub(super) fn csv(&self, key: &str) -> Result<Option<String>> {
        let Some(value) = self.get(key) else {
            return Ok(None);
        };
        if value.trim_start().starts_with('[') {
            let items = serde_json::from_str::<Vec<String>>(value).map_err(|error| {
                DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
            })?;
            Ok(Some(items.join(",")))
        } else {
            Ok(Some(value.to_string()))
        }
    }

    pub(super) fn json_required(&self, key: &str) -> Result<Value> {
        serde_json::from_str(self.required(key)?).map_err(|error| {
            DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
        })
    }
}

pub(super) fn normalize_inst_id_query(params: &mut [(String, String)]) {
    for (key, value) in params.iter_mut() {
        if key == "product_symbol" {
            *key = "instId".to_string();
            *value = exchange_symbol_fallback(value);
        } else if key == "instId" {
            *value = exchange_symbol_fallback(value);
        }
    }
}

pub(super) fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.contains('-')
}

pub(super) fn exchange_symbol_fallback(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some("SPOT")) => format!("{base}-{quote}"),
        (Some(base), Some(quote), Some(kind)) => format!("{base}-{quote}-{kind}"),
        _ => product_symbol.to_string(),
    }
}

pub(super) fn push_optional(params: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
}

pub(super) fn push_optional_owned(
    params: &mut Vec<(String, String)>,
    key: &str,
    value: Option<String>,
) {
    if let Some(value) = value {
        params.push((key.to_string(), value));
    }
}

pub(super) fn insert_optional_string(
    body: &mut Map<String, Value>,
    key: &str,
    value: Option<&str>,
) {
    if let Some(value) = value {
        body.insert(key.to_string(), Value::String(value.to_string()));
    }
}

pub(super) fn insert_optional_bool(
    body: &mut Map<String, Value>,
    key: &str,
    value: Option<&str>,
) -> Result<()> {
    if let Some(value) = value {
        let parsed = match value.to_ascii_lowercase().as_str() {
            "true" => true,
            "false" => false,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "invalid boolean parameter {key}: {value}"
                )));
            }
        };
        body.insert(key.to_string(), Value::Bool(parsed));
    }
    Ok(())
}

pub(super) fn okx_account_id(account: &str) -> &str {
    match account {
        "FUND" => "6",
        "TRADING" => "18",
        _ => account,
    }
}

pub(super) fn validate_deposit_withdraw_status(params: &OkxParams) -> Result<()> {
    let has_wd_id = params.get("wdId").is_some();
    let has_tx_id = params.get("txId").is_some();
    if has_wd_id == has_tx_id {
        return Err(DcexError::InvalidInput(
            "Exactly one of wdId or txId is required.".to_string(),
        ));
    }
    if has_tx_id {
        let missing = ["ccy", "to", "chain"]
            .into_iter()
            .filter(|key| params.get(key).is_none())
            .collect::<Vec<_>>();
        if !missing.is_empty() {
            return Err(DcexError::InvalidInput(format!(
                "{} required when querying deposit status by txId.",
                missing.join(", ")
            )));
        }
    }
    Ok(())
}
