//! Binary SBE snapshot adapter.
use super::*;

impl OkxClient {
    /// Fetch the public 400-level SBE snapshot as raw bytes (message template 1006).
    /// Callers decode the payload using OKX's versioned SBE XML schema.
    pub async fn get_sbe_orderbook(&self, inst_id_code: u64) -> Result<Vec<u8>> {
        if inst_id_code == 0 {
            return Err(invalid("instIdCode must be positive"));
        }
        let response = self
            .request_raw(
                HttpMethod::Get,
                "/api/v5/market/books-sbe",
                vec![
                    ("instIdCode".into(), inst_id_code.to_string()),
                    ("source".into(), "0".into()),
                ],
                None,
                false,
            )
            .await?;
        response.ensure_success()?;
        let content_type = response
            .headers
            .iter()
            .find(|(key, _)| key.eq_ignore_ascii_case("content-type"))
            .map(|(_, value)| value.as_str())
            .unwrap_or_default();
        if content_type.starts_with("application/json") {
            super::super::signing::validate_response(&response)?;
            return Err(DcexError::Decode(
                "OKX SBE snapshot returned JSON instead of binary data".into(),
            ));
        }
        if !content_type.starts_with("application/sbe") || response.body.is_empty() {
            return Err(DcexError::Decode(
                "OKX SBE snapshot requires a nonempty application/sbe response".into(),
            ));
        }
        Ok(response.body)
    }
}
