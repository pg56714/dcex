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
        static ROUTES: std::sync::OnceLock<Vec<crate::exchanges::schema::Route>> =
            std::sync::OnceLock::new();
        let Some(route) = crate::exchanges::schema::route(
            &ROUTES,
            include_str!("schemas/routes_interest.json"),
            name,
        ) else {
            return Ok(None);
        };
        let (path, is_public, fields, required) =
            (route.path, route.is_public, route.fields, route.required);
        if is_public != public {
            return Ok(None);
        }
        route.validate(|key| params.get(key))?;
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
