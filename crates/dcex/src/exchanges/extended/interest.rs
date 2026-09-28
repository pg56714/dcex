//! Interest operations.
use crate::exchanges::extended::{client::ExtendedClient, params::ExtendedParams};
use crate::{Result, exchange::ValidatedResponse};
impl ExtendedClient {
    pub(in crate::exchanges::extended) async fn interest_schema_request(
        &self,
        name: &str,
        params: &ExtendedParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, is_public, fields, required): (&str, bool, &[&str], &[&str]) = match name {
            "get_interest_rate_curves_history" => (
                "/api/v1/interest/info/rate-curves",
                true,
                &["interval"],
                &["interval"],
            ),
            "get_latest_interest_rate_curve" => {
                ("/api/v1/interest/info/latest-rate-curves", true, &[], &[])
            }
            "get_interest_key_metrics" => (
                "/api/v1/interest/key-metrics",
                false,
                &["accountId"],
                &["accountId"],
            ),
            "get_interest_daily_metrics" => (
                "/api/v1/interest/daily-metrics",
                false,
                &["accountId", "interval"],
                &["accountId", "interval"],
            ),
            "get_interest_payment_chart" => (
                "/api/v1/interest/payment-chart",
                false,
                &["accountId", "interval", "bucket"],
                &["accountId", "interval"],
            ),
            "get_interest_payments_history" => (
                "/api/v1/interest/payments",
                false,
                &["accountId", "interval"],
                &["accountId", "interval"],
            ),
            _ => return Ok(None),
        };
        if is_public != public {
            return Ok(None);
        }
        params.ensure_allowed(fields, &["accountId", "market", "priceMarket"])?;
        for key in required {
            params.required(key)?;
        }
        params.repeated_u64_range("accountId", 0, u64::MAX)?;
        params.optional_one_of("interval", &["DAY", "WEEK", "MONTH", "YEAR", "ALL"])?;
        if name == "get_vault_performance" {
            params.optional_one_of("interval", &["WEEK", "MONTH", "YEAR", "ALL"])?;
        }
        params.optional_one_of("pnlType", &["TOTAL_PNL", "REALISED_PNL"])?;
        params.optional_one_of("instrumentType", &["ALL", "PERPS", "SPOT"])?;
        params.optional_one_of("marketType", &["ALL", "PERPS", "SPOT"])?;
        params.optional_one_of("bucket", &["HOURLY", "DAILY"])?;
        params.optional_u64_range("limit", 1, 500)?;
        params.u64("cursor")?;
        let query = params.only(fields);
        Ok(Some(if public {
            self.public_get(path, query).await?
        } else {
            self.private_get(path, query).await?
        }))
    }
}
