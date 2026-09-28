//! Rewards operations.
use crate::exchanges::extended::{client::ExtendedClient, params::ExtendedParams};
use crate::{Result, exchange::ValidatedResponse};
impl ExtendedClient {
    pub(in crate::exchanges::extended) async fn rewards_schema_request(
        &self,
        name: &str,
        params: &ExtendedParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, is_public, fields, required): (&str, bool, &[&str], &[&str]) = match name {
            "get_earned_points" => ("/api/v1/user/rewards/earned", false, &[], &[]),
            "get_points_leaderboard_stats" => {
                ("/api/v1/user/rewards/leaderboard/stats", false, &[], &[])
            }
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
