//! Address utilities.
use crate::{DcexError, Result};

pub fn address_to_bytes(address: &str) -> Result<Vec<u8>> {
    let address = address.strip_prefix("0x").unwrap_or(address);
    hex::decode(address)
        .map_err(|error| DcexError::InvalidInput(format!("invalid hexadecimal address: {error}")))
}
