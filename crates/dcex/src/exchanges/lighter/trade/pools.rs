//! Pool and staking transaction layouts verified against official lighter-go txtypes.
use super::*;
impl LighterClient {
    pub(super) async fn sign_pool_from_params(
        &self,
        name: &str,
        p: &LighterParams,
    ) -> Result<LighterSignedTransaction> {
        let (tx_type, mut payload, specific) = pool_fields(name, p)?;
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
        if tx_type == 10 && account > (1 << 47) - 1 {
            return Err(DcexError::InvalidInput(
                "public pools require a master account".into(),
            ));
        }
        let api_key = self.signing_api_key_index(p)?;
        let chain = self.signing_chain_id()?;
        let nonce = self.next_nonce(validate_nonce(p)?, Some(api_key)).await?;
        let expiry = expiry_ms()?;
        let mut values = vec![
            chain as i128,
            tx_type as i128,
            nonce as i128,
            expiry as i128,
            account as i128,
            api_key as i128,
        ];
        values.extend(specific);
        payload["AccountIndex"] = account.into();
        payload["ApiKeyIndex"] = api_key.into();
        payload["Nonce"] = nonce.into();
        payload["ExpiredAt"] = expiry.into();
        self.sign_tx(tx_type, values, payload, attrs, api_key)
    }
}

fn pool_fields(name: &str, p: &LighterParams) -> Result<(u64, serde_json::Value, Vec<i128>)> {
    let (tx_type, fields): (u64, &[(&str, &str, u64, u64)]) = match name {
        "create_public_pool" => (
            10,
            &[
                ("operator_fee", "OperatorFee", 0, 1000000),
                (
                    "initial_total_shares",
                    "InitialTotalShares",
                    1,
                    1000000000000,
                ),
                ("min_operator_share_rate", "MinOperatorShareRate", 0, 10000),
            ],
        ),
        "update_public_pool" => (
            11,
            &[
                ("public_pool_index", "PublicPoolIndex", 0, 281474976710654),
                ("status", "Status", 0, 1),
                ("operator_fee", "OperatorFee", 0, 1000000),
                ("min_operator_share_rate", "MinOperatorShareRate", 0, 10000),
            ],
        ),
        "mint_shares" => (
            18,
            &[
                (
                    "public_pool_index",
                    "PublicPoolIndex",
                    140737488355328,
                    281474976710654,
                ),
                ("share_amount", "ShareAmount", 1, 1152921504606846975),
            ],
        ),
        "burn_shares" => (
            19,
            &[
                (
                    "public_pool_index",
                    "PublicPoolIndex",
                    140737488355328,
                    281474976710654,
                ),
                ("share_amount", "ShareAmount", 1, 1152921504606846975),
            ],
        ),
        "stake_assets" => (
            35,
            &[
                (
                    "staking_pool_index",
                    "StakingPoolIndex",
                    140737488355328,
                    281474976710654,
                ),
                ("share_amount", "ShareAmount", 1, 1152921504606846975),
            ],
        ),
        "unstake_assets" => (
            36,
            &[
                (
                    "staking_pool_index",
                    "StakingPoolIndex",
                    140737488355328,
                    281474976710654,
                ),
                ("share_amount", "ShareAmount", 1, 1152921504606846975),
            ],
        ),
        _ => return Err(DcexError::InvalidInput("unknown pool action".into())),
    };
    let mut allowed: Vec<&str> = fields.iter().map(|f| f.0).collect();
    allowed.extend(["skip_nonce", "nonce", "api_key_index", "price_protection"]);
    p.ensure_allowed(&allowed)?;
    p.optional_bool("price_protection")?;
    let mut payload = json!({});
    let mut specific = Vec::new();
    for &(key, wire, lo, hi) in fields {
        let value = p.required_u64_range(key, lo, hi)?;
        payload[wire] = value.into();
        specific.push(value as i128);
    }

    Ok((tx_type, payload, specific))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn pool_field_order_matches_independent_official_go_poseidon_vectors() {
        // Generated with github.com/elliottech/poseidon_crypto and lighter-go txtypes field order.
        let p = LighterParams::from_pairs(vec![
            ("operator_fee".into(), "1".into()),
            ("initial_total_shares".into(), "1".into()),
            ("min_operator_share_rate".into(), "1".into()),
        ]);
        let (ty, _, specific) = pool_fields("create_public_pool", &p).expect("pool fields");
        let mut values = vec![304, ty as i128, 5, 1700000600000, 12, 3];
        values.extend(specific);
        assert_eq!(
            hex::encode(crate::lighter::transaction_hash(&values, &[])),
            "ea10599b03574c0e4505c4c7dfca0b59533920b158165990c877e752afd99122bdd2fbe8b015863a"
        );
        let p = LighterParams::from_pairs(vec![
            ("public_pool_index".into(), "1".into()),
            ("status".into(), "1".into()),
            ("operator_fee".into(), "1".into()),
            ("min_operator_share_rate".into(), "1".into()),
        ]);
        let (ty, _, specific) = pool_fields("update_public_pool", &p).expect("pool fields");
        let mut values = vec![304, ty as i128, 5, 1700000600000, 12, 3];
        values.extend(specific);
        assert_eq!(
            hex::encode(crate::lighter::transaction_hash(&values, &[])),
            "458857d1955a2e0d168cf0e43c4edfd7af95e4c5a17223032819409f95786b859d8da8b1d3f6219d"
        );
        let p = LighterParams::from_pairs(vec![
            ("public_pool_index".into(), "140737488355328".into()),
            ("share_amount".into(), "1".into()),
        ]);
        let (ty, _, specific) = pool_fields("mint_shares", &p).expect("pool fields");
        let mut values = vec![304, ty as i128, 5, 1700000600000, 12, 3];
        values.extend(specific);
        assert_eq!(
            hex::encode(crate::lighter::transaction_hash(&values, &[])),
            "1fead477bbb31e9c4b7dc565f43faf4253a4e5b6aad088fdfed06918e1495364a8dbd145e4dace1b"
        );
        let p = LighterParams::from_pairs(vec![
            ("public_pool_index".into(), "140737488355328".into()),
            ("share_amount".into(), "1".into()),
        ]);
        let (ty, _, specific) = pool_fields("burn_shares", &p).expect("pool fields");
        let mut values = vec![304, ty as i128, 5, 1700000600000, 12, 3];
        values.extend(specific);
        assert_eq!(
            hex::encode(crate::lighter::transaction_hash(&values, &[])),
            "6a00f7fa778bbfb5c3fcd7618e213c451cad45314c7f87a5534a058680f7f24176c7be45aeca1118"
        );
        let p = LighterParams::from_pairs(vec![
            ("staking_pool_index".into(), "140737488355328".into()),
            ("share_amount".into(), "1".into()),
        ]);
        let (ty, _, specific) = pool_fields("stake_assets", &p).expect("pool fields");
        let mut values = vec![304, ty as i128, 5, 1700000600000, 12, 3];
        values.extend(specific);
        assert_eq!(
            hex::encode(crate::lighter::transaction_hash(&values, &[])),
            "720b9e6a419b5ace6cf5d49b18405ebe0cb9241dcc6f58b38978fbe3148defd9811f63c1a3665b49"
        );
        let p = LighterParams::from_pairs(vec![
            ("staking_pool_index".into(), "140737488355328".into()),
            ("share_amount".into(), "1".into()),
        ]);
        let (ty, _, specific) = pool_fields("unstake_assets", &p).expect("pool fields");
        let mut values = vec![304, ty as i128, 5, 1700000600000, 12, 3];
        values.extend(specific);
        assert_eq!(
            hex::encode(crate::lighter::transaction_hash(&values, &[])),
            "842e82c3d7b67d78d73a42e2e018b88dc7f1cfc6eeda846da2fbc0fff3fde285224555c478a729d3"
        );
    }
}
