//! Transaction 13 and 45 follow lighter-go's typed transaction hashes.
use super::*;

impl LighterClient {
    pub(super) async fn sign_withdrawal_or_approval(
        &self,
        p: &LighterParams,
        approval: bool,
    ) -> Result<LighterSignedTransaction> {
        let fields: &[&str] = if approval {
            &[
                "integrator_account_index",
                "max_perps_taker_fee",
                "max_perps_maker_fee",
                "max_spot_taker_fee",
                "max_spot_maker_fee",
                "approval_expiry",
                "l1_signature",
                "nonce",
                "api_key_index",
                "skip_nonce",
            ]
        } else {
            &[
                "asset_index",
                "route_type",
                "amount",
                "nonce",
                "api_key_index",
                "skip_nonce",
            ]
        };
        p.ensure_allowed(fields)?;
        let mut suffix = Vec::new();
        let mut payload = json!({});
        if approval {
            let integrator = p.required_u64_range("integrator_account_index", 0, (1 << 48) - 2)?;
            suffix.push(integrator as i128);
            payload["IntegratorAccountIndex"] = integrator.into();
            let mut all_zero = true;
            for (param, key) in [
                ("max_perps_taker_fee", "MaxPerpsTakerFee"),
                ("max_perps_maker_fee", "MaxPerpsMakerFee"),
                ("max_spot_taker_fee", "MaxSpotTakerFee"),
                ("max_spot_maker_fee", "MaxSpotMakerFee"),
            ] {
                let fee = p.required_u64_range(param, 0, 1_000_000)?;
                all_zero &= fee == 0;
                suffix.push(fee as i128);
                payload[key] = fee.into();
            }
            let expiry = p.required_u64_range("approval_expiry", 0, (1 << 48) - 1)?;
            if expiry == 0 && !all_zero {
                return Err(DcexError::InvalidInput(
                    "revocation requires all fees to be zero".into(),
                ));
            }
            suffix.push(expiry as i128);
            payload["ApprovalExpiry"] = expiry.into();
            let signature = p
                .required("l1_signature")?
                .strip_prefix("0x")
                .unwrap_or(p.required("l1_signature")?);
            let bytes = hex::decode(signature)
                .map_err(|_| DcexError::InvalidInput("invalid L1 signature hex".into()))?;
            if bytes.len() != 65 || !matches!(bytes[64], 0 | 1 | 27 | 28) {
                return Err(DcexError::InvalidInput(
                    "L1 signature must be a recoverable 65-byte Ethereum signature".into(),
                ));
            }
            p.required_u64("nonce")?;
            payload["L1Sig"] = format!("0x{signature}").into();
        } else {
            let asset = p.required_u64_range("asset_index", 1, 62)?;
            let route = p.required_u64_range("route_type", 0, 1)?;
            let amount = p.required_u64_range("amount", 1, (1 << 60) - 1)?;
            suffix.extend([
                asset as i128,
                route as i128,
                (amount & 0xffffffff) as i128,
                (amount >> 32) as i128,
            ]);
            payload["AssetIndex"] = asset.into();
            payload["RouteType"] = route.into();
            payload["Amount"] = amount.into();
        }
        let attrs = attributes(
            0,
            0,
            0,
            p.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
            0,
            0,
        )?;
        let account = self.private_account_index(None)?;
        let api_key = self.signing_api_key_index(p)?;
        let chain = self.signing_chain_id()?;
        let nonce = self.next_nonce(validate_nonce(p)?, Some(api_key)).await?;
        let expiry = expiry_ms()?;
        let kind = if approval { 45 } else { 13 };
        let mut values = vec![
            chain as i128,
            kind as i128,
            nonce as i128,
            expiry as i128,
            account as i128,
            api_key as i128,
        ];
        values.extend(suffix);
        payload[if approval {
            "AccountIndex"
        } else {
            "FromAccountIndex"
        }] = account.into();
        payload["ApiKeyIndex"] = api_key.into();
        payload["Nonce"] = nonce.into();
        payload["ExpiredAt"] = expiry.into();
        self.sign_tx(kind, values, payload, attrs, api_key)
    }
}
