//! Same-master-account transfers follow lighter-go L2TransferTxInfo without an L1 signature.
use super::*;
impl LighterClient {
    pub(super) async fn sign_internal_transfer(
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
        .map_err(|_| DcexError::InvalidInput("memo_hex must contain exactly 32 bytes".into()))?;
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
