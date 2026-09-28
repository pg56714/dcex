//! Builder and wallet-authorized withdrawals from the official V3 examples.
use super::{AsterClient, AsterMarket, params::AsterParams};
use crate::{DcexError, Result, exchange::ValidatedResponse, http::HttpMethod};

impl AsterClient {
    pub(super) async fn completion_private_request(
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
        let (market, solana) = match name {
            "withdraw_spot_signed" => (AsterMarket::Spot, false),
            "withdraw_spot_solana_signed" => (AsterMarket::Spot, true),
            "withdraw_futures_signed" => (AsterMarket::Futures, false),
            "withdraw_futures_solana_signed" => (AsterMarket::Futures, true),
            _ => return Ok(None),
        };
        let mut fields = vec![
            "chainId",
            "asset",
            "amount",
            "fee",
            "receiver",
            "userNonce",
            "userSignature",
        ];
        if !solana {
            fields.push("signatureType");
            fields.push("signatureChainId");
        }
        p.ensure_allowed(&fields, &[])?;
        for field in ["chainId", "asset", "amount", "fee", "receiver"] {
            p.required(field)?;
        }
        if !crate::common::is_positive_plain_decimal(p.required("amount")?) {
            return Err(invalid("amount requires a positive plain decimal string"));
        }
        p.optional_non_negative_decimal("fee")?;
        p.required_u64_range("chainId", 1, u64::MAX)?;
        if solana {
            p.required_one_of("chainId", &["101"])?;
            if let Some(signature) = p.get("userSignature")
                && !bs58::decode(signature)
                    .into_vec()
                    .is_ok_and(|v| v.len() == 64)
            {
                return Err(invalid("userSignature requires a Base58 Ed25519 signature"));
            }
        } else {
            p.required("userNonce")?;
            p.required("userSignature")?;
            p.optional_one_of("signatureType", &["EOA", "SafeWallet"])?;
        }
        let prefix = if market == AsterMarket::Spot {
            "/api/v3"
        } else {
            "/fapi/v3"
        };
        let action = if solana {
            "user-solana-withdraw"
        } else {
            "user-withdraw"
        };
        // Preserve wallet authorization; add ordinary V3 agent authentication separately.
        self.request(
            HttpMethod::Post,
            market,
            format!("{prefix}/aster/{action}"),
            p.only(&fields),
            true,
        )
        .await
        .map(Some)
    }
}

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Aster: {message}"))
}
