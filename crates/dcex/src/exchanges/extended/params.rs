use serde_json::Value;

use crate::{DcexError, Result};

pub(super) struct ExtendedParams(Vec<(String, String)>);

impl ExtendedParams {
    pub(super) fn from_pairs(params: Vec<(String, String)>) -> Self {
        Self(params)
    }

    pub(super) fn get(&self, key: &str) -> Option<&str> {
        self.0
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    pub(super) fn first(&self, keys: &[&str]) -> Option<&str> {
        keys.iter().find_map(|key| self.get(key))
    }

    pub(super) fn first_required(&self, keys: &[&str]) -> Result<&str> {
        self.first(keys).ok_or_else(|| {
            DcexError::InvalidInput(format!("missing required parameter: {}", keys.join(" or ")))
        })
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

    pub(super) fn body_required(&self) -> Result<Value> {
        self.body_optional()?.ok_or_else(|| {
            DcexError::InvalidInput("missing required parameter: body or order JSON".to_string())
        })
    }

    pub(super) fn body_optional(&self) -> Result<Option<Value>> {
        let Some(body) = self.get("body").or_else(|| self.get("order")) else {
            return Ok(None);
        };
        serde_json::from_str(body)
            .map(Some)
            .map_err(|error| DcexError::InvalidInput(format!("invalid JSON body: {error}")))
    }
}

pub(super) fn path_with_id(base: &str, id: &str) -> String {
    format!("{}/{}", base.trim_end_matches('/'), id)
}
