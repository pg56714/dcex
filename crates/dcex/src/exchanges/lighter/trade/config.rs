//! Account settings use transaction types 41/42 from the official lighter-go SDK.
use super::*;

impl LighterClient {
    pub(super) async fn sign_account_config_from_params(
        &self,
        params: &LighterParams,
        asset: bool,
    ) -> Result<LighterSignedTransaction> {
        let fields: &[&str] = if asset {
            &[
                "asset_index",
                "asset_margin_mode",
                "skip_nonce",
                "nonce",
                "api_key_index",
                "price_protection",
            ]
        } else {
            &[
                "account_trading_mode",
                "skip_nonce",
                "nonce",
                "api_key_index",
                "price_protection",
            ]
        };
        params.ensure_allowed(fields)?;
        params.optional_bool("price_protection")?;
        let asset_index = if asset {
            Some(params.required_u64_range("asset_index", 1, 62)?)
        } else {
            None
        };
        let mode = params.required_u64_range(
            if asset {
                "asset_margin_mode"
            } else {
                "account_trading_mode"
            },
            0,
            1,
        )?;
        let attrs = attributes(
            0,
            0,
            0,
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
            0,
            0,
        )?;
        let api_key_index = self.signing_api_key_index(params)?;
        let account = self.private_account_index(None)?;
        let chain = self.signing_chain_id()?;
        let nonce = self
            .next_nonce(validate_nonce(params)?, Some(api_key_index))
            .await?;
        let expiry = expiry_ms()?;
        let tx_type = if asset { 42 } else { 41 };
        let mut values = vec![
            chain as i128,
            tx_type as i128,
            nonce as i128,
            expiry as i128,
            account as i128,
            api_key_index as i128,
        ];
        let mut payload = json!({"AccountIndex":account,"ApiKeyIndex":api_key_index,"Nonce":nonce,"ExpiredAt":expiry});
        if let Some(index) = asset_index {
            values.push(index as i128);
            payload["AssetIndex"] = index.into();
            payload["AssetMarginMode"] = mode.into();
        } else {
            payload["AccountTradingMode"] = mode.into();
        }
        values.push(mode as i128);
        self.sign_tx(tx_type, values, payload, attrs, api_key_index)
    }
}

impl LighterClient {
    pub(super) async fn sign_account_admin_from_params(
        &self,
        params: &LighterParams,
        key_change: bool,
    ) -> Result<LighterSignedTransaction> {
        use base64::Engine;
        let fields: &[&str] = if key_change {
            &[
                "new_pubkey",
                "l1_signature",
                "nonce",
                "api_key_index",
                "skip_nonce",
                "price_protection",
            ]
        } else {
            &["nonce", "api_key_index", "skip_nonce", "price_protection"]
        };
        params.ensure_allowed(fields)?;
        params.optional_bool("price_protection")?;
        let account = self.private_account_index(None)?;
        if !key_change && account > (1 << 47) - 1 {
            return Err(DcexError::InvalidInput(
                "Lighter subaccounts must be created by a master account".into(),
            ));
        }
        let api_key = self.signing_api_key_index(params)?;
        let mut pubkey_bytes = Vec::new();
        if key_change {
            let key = params.required("new_pubkey")?;
            pubkey_bytes = hex::decode(key.strip_prefix("0x").unwrap_or(key))
                .map_err(|_| DcexError::InvalidInput("invalid Lighter public key hex".into()))?;
            if pubkey_bytes.len() != 40
                || pubkey_bytes
                    .chunks_exact(8)
                    .any(|b| u64::from_le_bytes(b.try_into().unwrap()) >= 0xffff_ffff_0000_0001)
            {
                return Err(DcexError::InvalidInput(
                    "Lighter public key must contain five canonical Goldilocks elements".into(),
                ));
            }
            let signature = params.required("l1_signature")?;
            let bytes = hex::decode(signature.strip_prefix("0x").unwrap_or(signature))
                .map_err(|_| DcexError::InvalidInput("invalid L1 signature hex".into()))?;
            if bytes.len() != 65 || !matches!(bytes[64], 0 | 1 | 27 | 28) {
                return Err(DcexError::InvalidInput(
                    "L1 signature must be a recoverable 65-byte Ethereum signature".into(),
                ));
            }
            params.required_u64("nonce")?;
        }
        let attrs = attributes(
            0,
            0,
            0,
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
            0,
            0,
        )?;
        let nonce = self
            .next_nonce(validate_nonce(params)?, Some(api_key))
            .await?;
        let expiry = expiry_ms()?;
        let tx_type = if key_change { 8 } else { 9 };
        let mut values = vec![
            self.signing_chain_id()? as i128,
            tx_type as i128,
            nonce as i128,
            expiry as i128,
            account as i128,
            api_key as i128,
        ];
        let mut payload =
            json!({"AccountIndex":account,"ApiKeyIndex":api_key,"Nonce":nonce,"ExpiredAt":expiry});
        if key_change {
            values.extend(
                pubkey_bytes
                    .chunks_exact(8)
                    .map(|b| u64::from_le_bytes(b.try_into().unwrap()) as i128),
            );
            payload["PubKey"] = base64::engine::general_purpose::STANDARD
                .encode(pubkey_bytes)
                .into();
            payload["L1Sig"] = format!(
                "0x{}",
                params.required("l1_signature")?.trim_start_matches("0x")
            )
            .into();
        }
        self.sign_tx(tx_type, values, payload, attrs, api_key)
    }
}
