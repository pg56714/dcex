//! Withdrawals operations.
use crate::exchanges::aster::{AsterClient, AsterMarket, params::AsterParams};
use crate::{Result, exchange::ValidatedResponse, http::HttpMethod};

impl AsterClient {
    pub(in crate::exchanges::aster) async fn withdrawals_private_request(
        &self,
        name: &str,
        p: &AsterParams,
    ) -> Result<Option<ValidatedResponse>> {
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
            if p.get("signatureChainId").is_some() {
                p.required_u64_range("signatureChainId", 1, u64::MAX)?;
            }
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

use crate::exchanges::aster::params::invalid;

impl super::client::AsterClient {
    pub(in crate::exchanges::aster) async fn withdrawals_prediction_dispatch(
        &self,
        name: &str,
        p: &super::params::AsterParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        if crate::exchanges::schema::fund_domain(name)
            != Some(crate::exchanges::schema::FundDomain::Withdrawals)
        {
            return Err(crate::DcexError::InvalidInput(
                "fund operation routed to the wrong owner".into(),
            ));
        }
        self.prediction_dispatch_transport(name, p, public).await
    }
}
