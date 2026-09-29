//! Shape validation for deployment actions and their named variants.
use crate::Result;
use serde_json::{Map, Value};

pub(super) fn validate_action_shape(
    object: &Map<String, Value>,
    variants: &[&str],
    required_fields: &[String],
    variant: &str,
) -> Result<()> {
    if !variants.is_empty() {
        if object.len() != 2 || variants.iter().filter(|v| object.contains_key(**v)).count() != 1 {
            return Err(invalid(
                "action must contain exactly one documented variant",
            ));
        }
    } else {
        for field in required_fields {
            if !object.contains_key(field) {
                return Err(invalid(format!("action is missing {field}")));
            }
        }
    }
    if !variant.is_empty() && object.len() != 2 {
        return Err(invalid(
            "deploy action must contain only type and its named variant",
        ));
    }
    Ok(())
}

use crate::exchanges::hyperliquid::params::invalid;
