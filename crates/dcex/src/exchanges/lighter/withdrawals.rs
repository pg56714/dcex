//! L2 withdrawals and recipient transfers.

mod from_trade_withdraw {
    // Transaction 13 and 45 follow lighter-go's typed transaction hashes.
    use crate::exchanges::lighter::trade::*;

    impl LighterClient {
        pub(in crate::exchanges::lighter) async fn sign_withdrawal_or_approval(
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
                let integrator =
                    p.required_u64_range("integrator_account_index", 0, (1 << 48) - 2)?;
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
}

mod from_trade_transfer {
    // L2 transfers follow lighter-go L2TransferTxInfo; account-family eligibility is exchange-enforced.
    use crate::exchanges::lighter::trade::*;
    impl LighterClient {
        pub(in crate::exchanges::lighter) async fn sign_internal_transfer(
            &self,
            p: &LighterParams,
        ) -> Result<LighterSignedTransaction> {
            p.ensure_allowed(&[
                "to_account_index",
                "asset_index",
                "from_route_type",
                "to_route_type",
                "amount",
                "usdc_fee",
                "memo_hex",
                "skip_nonce",
                "nonce",
                "api_key_index",
                "price_protection",
            ])?;
            let to = p.required_u64_range("to_account_index", 0, 281474976710654)?;
            let asset = p.required_u64_range("asset_index", 1, 62)?;
            let from_route = p.required_u64_range("from_route_type", 0, 1)?;
            let to_route = p.required_u64_range("to_route_type", 0, 1)?;
            let amount = p.required_u64_range("amount", 1, 1152921504606846975)?;
            let fee = p
                .optional_u64_range("usdc_fee", 0, 1152921504606846975)?
                .unwrap_or(0);
            let memo = hex::decode(
                p.get("memo_hex")
                    .unwrap_or("0000000000000000000000000000000000000000000000000000000000000000"),
            )
            .map_err(|_| {
                DcexError::InvalidInput("memo_hex must contain exactly 32 bytes".into())
            })?;
            if memo.len() != 32 {
                return Err(DcexError::InvalidInput(
                    "memo_hex must contain exactly 32 bytes".into(),
                ));
            }
            p.optional_bool("price_protection")?;
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
            let values = vec![
                chain as i128,
                12,
                nonce as i128,
                expiry as i128,
                account as i128,
                api_key as i128,
                to as i128,
                asset as i128,
                from_route as i128,
                to_route as i128,
                (amount & 0xffffffff) as i128,
                (amount >> 32) as i128,
                (fee & 0xffffffff) as i128,
                (fee >> 32) as i128,
            ];
            let payload = json!({"FromAccountIndex":account,"ApiKeyIndex":api_key,"ToAccountIndex":to,"AssetIndex":asset,"FromRouteType":from_route,"ToRouteType":to_route,"Amount":amount,"USDCFee":fee,"Memo":memo,"Nonce":nonce,"ExpiredAt":expiry,"L1Sig":""});
            self.sign_tx(12, values, payload, attrs, api_key)
        }
    }
}

mod wrappers_from_wrappers {
    use crate::exchanges::lighter::LighterClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; LighterClient;
     public [
    get_withdrawal_delay()
     ];
     private [
    get_fastwithdraw_info(),
    get_withdraw_history()
     ];
    }
}
