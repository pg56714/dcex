//! Builder operations.
use crate::exchanges::aster::{AsterClient, AsterMarket, params::AsterParams};
use crate::{Result, exchange::ValidatedResponse, http::HttpMethod};

impl AsterClient {
    pub(in crate::exchanges::aster) async fn builder_private_request(
        &self,
        name: &str,
        p: &AsterParams,
    ) -> Result<Option<ValidatedResponse>> {
        let builder = match name {
            "get_builder_user_accounts" => Some(("userAccounts", true, false)),
            "get_builder_user_open_orders" => Some(("userOpenOrders", true, false)),
            "get_builder_user_balances" => Some(("userBalances", false, false)),
            "get_builder_user_position_risk" => Some(("userPositionRisk", true, false)),
            "get_builder_user_commission_rates" => Some(("userCommissionRates", true, false)),
            "get_builder_user_trades" => Some(("userTrades", false, true)),
            "get_builder_user_all_orders" => Some(("userAllOrders", true, true)),
            "get_builder_approved_users" => Some(("approvedUserList", false, true)),
            _ => None,
        };
        if let Some((suffix, symbol, times)) = builder {
            let mut fields = vec!["page", "limit"];
            if suffix != "approvedUserList" {
                fields.push("userAddresses");
            }
            if symbol {
                fields.push("symbol");
            }
            if times {
                fields.extend(["startTime", "endTime"]);
            }
            p.ensure_allowed(&fields, &[])?;
            if suffix == "userCommissionRates" {
                p.required("symbol")?;
            }
            p.optional_u64_range("page", 1, u64::MAX)?;
            p.optional_u64_range("limit", 1, 1000)?;
            p.ensure_time_order("startTime", "endTime")?;
            if let Some(addresses) = p.get("userAddresses") {
                let list: Vec<_> = addresses.split(',').collect();
                if list.len() > 50 || list.iter().any(|a| a.trim().is_empty()) {
                    return Err(invalid("userAddresses requires 1..50 nonempty addresses"));
                }
            }
            return self
                .request(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    format!("/fapi/v3/builder/{suffix}"),
                    p.only(&fields),
                    true,
                )
                .await
                .map(Some);
        }
        Ok(None)
    }
}

use crate::exchanges::aster::params::invalid;
