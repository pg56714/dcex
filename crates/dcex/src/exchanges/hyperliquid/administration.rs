//! Administration action variants and multi-signature envelope validation.
use crate::{DcexError, Result};
use serde_json::Value;

pub(super) fn action_variants(kind: &str) -> &'static [&'static str] {
    match kind {
        "userOutcome" => &[
            "splitOutcome",
            "mergeOutcome",
            "mergeQuestion",
            "negateOutcome",
        ],
        "activateOutcomeDeployer" => &["activate", "deactivate"],
        "CSignerAction" => &["unjailSelf", "jailSelf"],
        "CValidatorAction" => &["register", "changeProfile", "unregister"],
        _ => &[],
    }
}

pub(super) fn validate_multisig_nonce(kind: &str, value: &Value, nonce: u64) -> Result<()> {
    if kind == "convertToMultiSigUser" && value["nonce"].as_u64() != Some(nonce) {
        return Err(DcexError::InvalidInput(
            "Hyperliquid: action nonce must match the envelope nonce".into(),
        ));
    }
    Ok(())
}
