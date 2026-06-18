use base64::Engine;
use hmac::{Hmac, Mac};
use sha2::{Digest, Sha256, Sha512};

use crate::{DcexError, Result};

pub fn sha256(data: &[u8]) -> [u8; 32] {
    Sha256::digest(data).into()
}

pub fn sha512_hex(data: &[u8]) -> String {
    hex::encode(Sha512::digest(data))
}

pub fn hmac_sha256(secret: &[u8], message: &[u8]) -> Result<[u8; 32]> {
    let mut mac = Hmac::<Sha256>::new_from_slice(secret)
        .map_err(|error| DcexError::InvalidInput(error.to_string()))?;
    mac.update(message);
    Ok(mac.finalize().into_bytes().into())
}

pub fn hmac_sha512(secret: &[u8], message: &[u8]) -> Result<[u8; 64]> {
    let mut mac = Hmac::<Sha512>::new_from_slice(secret)
        .map_err(|error| DcexError::InvalidInput(error.to_string()))?;
    mac.update(message);
    Ok(mac.finalize().into_bytes().into())
}

pub fn hmac_sha256_hex(secret: &[u8], message: &[u8]) -> Result<String> {
    Ok(hex::encode(hmac_sha256(secret, message)?))
}

pub fn hmac_sha256_base64(secret: &[u8], message: &[u8]) -> Result<String> {
    Ok(base64::engine::general_purpose::STANDARD.encode(hmac_sha256(secret, message)?))
}

pub fn hmac_sha512_hex(secret: &[u8], message: &[u8]) -> Result<String> {
    Ok(hex::encode(hmac_sha512(secret, message)?))
}

pub fn hmac_sha512_base64(secret: &[u8], message: &[u8]) -> Result<String> {
    Ok(base64::engine::general_purpose::STANDARD.encode(hmac_sha512(secret, message)?))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hmac_sha256_matches_known_vector() {
        assert_eq!(
            hmac_sha256_hex(b"key", b"The quick brown fox jumps over the lazy dog").expect("hmac"),
            "f7bc83f430538424b13298e6aa6fb143ef4d59a14946175997479dbc2d1a3cd8"
        );
    }
}
