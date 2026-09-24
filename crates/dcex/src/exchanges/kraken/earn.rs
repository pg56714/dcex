use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::{KrakenAuth, KrakenClient};
use super::endpoints::*;
use super::params::KrakenParams;

impl KrakenClient {
    pub(super) async fn earn_private_request(
        &self,
        method_name: &str,
        params: &KrakenParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_earn_strategies" => {
                validate_optional_bool(params, "ascending")?;
                validate_optional_limit(params)?;
                self.private_post(
                    KrakenAuth::Spot,
                    EARN_STRATEGIES,
                    params.only(&["ascending", "asset", "cursor", "limit", "lock_type"]),
                )
                .await
            }
            "get_earn_allocations" => {
                validate_optional_bool(params, "ascending")?;
                validate_optional_bool(params, "hide_zero_allocations")?;
                validate_optional_limit(params)?;
                self.private_post(
                    KrakenAuth::Spot,
                    EARN_ALLOCATIONS,
                    params.only(&[
                        "ascending",
                        "converted_asset",
                        "cursor",
                        "hide_zero_allocations",
                        "limit",
                    ]),
                )
                .await
            }
            "allocate_earn_funds" | "deallocate_earn_funds" => {
                require_strategy_amount(params)?;
                let path = if method_name == "allocate_earn_funds" {
                    EARN_ALLOCATE
                } else {
                    EARN_DEALLOCATE
                };
                self.private_post(
                    KrakenAuth::Spot,
                    path,
                    params.only(&["strategy_id", "amount"]),
                )
                .await
            }
            "get_earn_allocation_status" | "get_earn_deallocation_status" => {
                params.required("strategy_id")?;
                let path = if method_name == "get_earn_allocation_status" {
                    EARN_ALLOCATE_STATUS
                } else {
                    EARN_DEALLOCATE_STATUS
                };
                self.private_post(KrakenAuth::Spot, path, params.only(&["strategy_id"]))
                    .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn require_strategy_amount(params: &KrakenParams) -> Result<()> {
    params.required("strategy_id")?;
    let amount = params.required("amount")?;
    if amount.parse::<f64>().is_ok_and(|value| value > 0.0) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "amount must be a positive number".to_string(),
        ))
    }
}

fn validate_optional_bool(params: &KrakenParams, key: &str) -> Result<()> {
    if let Some(value) = params.get(key) {
        if !matches!(value, "true" | "false") {
            return Err(DcexError::InvalidInput(format!(
                "{key} must be true or false"
            )));
        }
    }
    Ok(())
}

fn validate_optional_limit(params: &KrakenParams) -> Result<()> {
    if let Some(value) = params.get("limit") {
        if value.parse::<u16>().is_err() {
            return Err(DcexError::InvalidInput(
                "limit must be an unsigned 16-bit integer".to_string(),
            ));
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn allocation_requires_a_positive_amount() {
        let params = KrakenParams::from_pairs(vec![
            ("strategy_id".to_string(), "strategy".to_string()),
            ("amount".to_string(), "0".to_string()),
        ]);
        assert!(require_strategy_amount(&params).is_err());
    }

    #[test]
    fn earn_flags_accept_only_booleans() {
        let params = KrakenParams::from_pairs(vec![(
            "hide_zero_allocations".to_string(),
            "yes".to_string(),
        )]);
        assert!(validate_optional_bool(&params, "hide_zero_allocations").is_err());
    }
}
