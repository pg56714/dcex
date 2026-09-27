//! Portfolio and borrowing risk queries. Account and market filters preserve repeated keys.
use super::{client::ExtendedClient, params::ExtendedParams};
use crate::{Result, exchange::ValidatedResponse};
impl ExtendedClient {
    pub(super) async fn risk_request(
        &self,
        name: &str,
        params: &ExtendedParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, is_public, fields, required): (&str, bool, &[&str], &[&str]) = match name {
            "get_account_equity_history" => (
                "/api/v1/portfolio/charts/equities",
                false,
                &["accountId", "interval"],
                &["accountId", "interval"],
            ),
            "get_account_pnl_history" => (
                "/api/v1/portfolio/charts/pnl",
                false,
                &["accountId", "interval", "pnlType", "instrumentType"],
                &["accountId", "interval", "pnlType"],
            ),
            "get_account_pnl_percentage_history" => (
                "/api/v1/portfolio/charts/pnl/percentage",
                false,
                &[
                    "accountId",
                    "interval",
                    "pnlType",
                    "priceMarket",
                    "instrumentType",
                ],
                &["accountId", "interval", "pnlType"],
            ),
            "get_cumulative_account_pnl_history" => (
                "/api/v1/portfolio/charts/pnl/cumulative",
                false,
                &["accountId", "interval", "pnlType", "instrumentType"],
                &["accountId", "interval", "pnlType"],
            ),
            "get_cumulative_account_pnl_percentage_history" => (
                "/api/v1/portfolio/charts/pnl/cumulative/percentage",
                false,
                &[
                    "accountId",
                    "interval",
                    "pnlType",
                    "priceMarket",
                    "instrumentType",
                ],
                &["accountId", "interval", "pnlType"],
            ),
            "get_account_vault_equity_history" => (
                "/api/v1/portfolio/charts/vault-equities",
                false,
                &["accountId", "interval"],
                &["accountId", "interval"],
            ),
            "get_account_max_drawdown_history" => (
                "/api/v1/portfolio/charts/max-drawdown",
                false,
                &["accountId", "interval"],
                &["accountId", "interval"],
            ),
            "get_account_funding_chart" => (
                "/api/v1/portfolio/charts/funding",
                false,
                &["accountId", "interval", "market"],
                &["accountId", "interval"],
            ),
            "get_account_portfolio_summary" => (
                "/api/v1/portfolio/accounts/summary",
                false,
                &["accountId", "interval", "instrumentType"],
                &["accountId", "interval"],
            ),
            "get_account_performance" => (
                "/api/v1/portfolio/accounts/performance",
                false,
                &["accountId", "interval", "marketType"],
                &["accountId", "interval"],
            ),
            "get_account_funding_stats" => (
                "/api/v1/portfolio/funding/stats",
                false,
                &["accountId", "interval", "market"],
                &["accountId", "interval"],
            ),
            "get_account_funding_history" => (
                "/api/v1/portfolio/funding/history",
                false,
                &["accountId", "interval", "market", "cursor", "limit"],
                &["accountId", "interval"],
            ),
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
            "get_vault_performance" => (
                "/api/v1/vault/public/performance",
                true,
                &["interval"],
                &["interval"],
            ),
            "get_vault_summary" => ("/api/v1/vault/public/summary", true, &[], &[]),
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
