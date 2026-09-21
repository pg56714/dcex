use std::collections::BTreeMap;
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::Value;

use crate::{DcexError, Result};

pub(super) fn timestamp_ns() -> Result<u64> {
    let elapsed = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|error| DcexError::Runtime(error.to_string()))?;
    u64::try_from(elapsed.as_nanos())
        .map_err(|_| DcexError::Runtime("Arcus timestamp overflow".into()))
}

pub(super) fn legacy_signing_message(
    timestamp: u64,
    action: &str,
    body: &BTreeMap<String, Value>,
) -> Result<Vec<u8>> {
    let canonical_body =
        serde_json::to_string(body).map_err(|error| DcexError::Decode(error.to_string()))?;
    Ok(format!("{timestamp}{action}{canonical_body}").into_bytes())
}
