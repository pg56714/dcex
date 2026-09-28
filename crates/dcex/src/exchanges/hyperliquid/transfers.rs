//! Transfers between owned accounts.

mod trade_operations {
    use crate::exchange::{ValidatedResponse, unix_timestamp_ms};
    use crate::exchanges::hyperliquid::client::HyperliquidClient;
    use crate::exchanges::hyperliquid::endpoints::EXCHANGE;
    use crate::exchanges::hyperliquid::msgpack::encode_msgpack;
    use crate::exchanges::hyperliquid::params::HyperliquidParams;
    use crate::exchanges::hyperliquid::trade::*;
    use crate::http::HttpMethod;
    use crate::{DcexError, Result};

    impl HyperliquidClient {
        pub(in crate::exchanges::hyperliquid) async fn transfer_between_dexes_from_params(
            &self,
            params: &HyperliquidParams,
        ) -> Result<ValidatedResponse> {
            let source_dex = params.get("sourceDex").unwrap_or("");
            let destination_dex = params.get("destinationDex").unwrap_or("");
            if source_dex == destination_dex {
                return Err(DcexError::InvalidInput(
                    "Hyperliquid internal transfer requires distinct source and destination DEXes"
                        .to_string(),
                ));
            }
            let destination = self.wallet_address.as_deref().ok_or_else(|| {
                DcexError::InvalidInput(
                    "Hyperliquid internal transfer requires wallet address".to_string(),
                )
            })?;
            let token = params.required("token")?;
            let amount = params.positive_decimal("amount")?;
            let nonce = unix_timestamp_ms()?;
            let action = object(vec![
                ("type", string("agentSendAsset")),
                ("destination", string(destination)),
                ("sourceDex", string(source_dex)),
                ("destinationDex", string(destination_dex)),
                ("token", string(token)),
                ("amount", string(amount)),
                ("fromSubAccount", string("")),
                ("nonce", uint(nonce)),
            ]);
            let payload = serde_json::json!({"action": action.to_json()});
            self.exchange_payload_at_nonce(payload, encode_msgpack(&action), nonce)
                .await
        }

        pub(in crate::exchanges::hyperliquid) async fn transfer_usdc_spot_perp_from_params(
            &self,
            params: &HyperliquidParams,
        ) -> Result<ValidatedResponse> {
            let amount = params.positive_decimal("amount")?;
            let to_perp = params.required_bool("toPerp")?;
            let (nonce, signature_chain_id, signature) = user_signed_fields(params)?;
            let chain = if self.is_testnet() {
                "Testnet"
            } else {
                "Mainnet"
            };
            let payload = serde_json::json!({
                "action": {
                    "type": "usdClassTransfer",
                    "hyperliquidChain": chain,
                    "signatureChainId": signature_chain_id,
                    "amount": amount,
                    "toPerp": to_perp,
                    "nonce": nonce,
                },
                "nonce": nonce,
                "signature": signature,
            });
            let body = serde_json::to_vec(&payload)
                .map_err(|error| DcexError::Decode(error.to_string()))?;
            self.request(HttpMethod::Post, EXCHANGE, body, None, false)
                .await
        }
    }
}

mod signed_requests {
    use crate::exchanges::hyperliquid::trade::*;
    impl HyperliquidClient {
        pub(in crate::exchanges::hyperliquid) async fn dispatch_transfer_sub_account_usd(
            &self,
            params: &HyperliquidParams,
        ) -> Result<ValidatedResponse> {
            {
                if params.required_u64("usd")? == 0 {
                    return Err(DcexError::InvalidInput("usd must be positive".into()));
                }
                self.submit_action(
                    object(vec![
                        ("type", string("subAccountTransfer")),
                        ("subAccountUser", string(&params.address("subAccountUser")?)),
                        ("isDeposit", bool_value(params.required_bool("isDeposit")?)),
                        ("usd", uint(params.required_u64("usd")?)),
                    ]),
                    params,
                )
                .await
            }
        }
        pub(in crate::exchanges::hyperliquid) async fn dispatch_transfer_sub_account_spot(
            &self,
            params: &HyperliquidParams,
        ) -> Result<ValidatedResponse> {
            {
                if !params
                    .required("amount")?
                    .parse::<f64>()
                    .is_ok_and(|v| v.is_finite() && v > 0.0)
                {
                    return Err(DcexError::InvalidInput("amount must be positive".into()));
                }
                self.submit_action(
                    object(vec![
                        ("type", string("subAccountSpotTransfer")),
                        ("subAccountUser", string(&params.address("subAccountUser")?)),
                        ("isDeposit", bool_value(params.required_bool("isDeposit")?)),
                        ("token", string(params.required("token")?)),
                        ("amount", string(params.required("amount")?)),
                    ]),
                    params,
                )
                .await
            }
        }
        pub(in crate::exchanges::hyperliquid) async fn dispatch_transfer_vault_usd(
            &self,
            params: &HyperliquidParams,
        ) -> Result<ValidatedResponse> {
            {
                if params.required_u64("usd")? == 0 {
                    return Err(DcexError::InvalidInput("amount must be positive".into()));
                }
                self.submit_action(
                    object(vec![
                        ("type", string("vaultTransfer")),
                        ("vaultAddress", string(&params.address("targetVault")?)),
                        ("isDeposit", bool_value(params.required_bool("isDeposit")?)),
                        ("usd", uint(params.required_u64("usd")?)),
                    ]),
                    params,
                )
                .await
            }
        }
        pub(in crate::exchanges::hyperliquid) async fn dispatch_transfer_hip3_liquidator(
            &self,
            params: &HyperliquidParams,
        ) -> Result<ValidatedResponse> {
            {
                if params.required_u64("ntl")? == 0 {
                    return Err(DcexError::InvalidInput("amount must be positive".into()));
                }
                self.submit_action(
                    object(vec![
                        ("type", string("hip3LiquidatorTransfer")),
                        ("dex", string(params.required("dex")?)),
                        ("ntl", uint(params.required_u64("ntl")?)),
                        ("isDeposit", bool_value(params.required_bool("isDeposit")?)),
                    ]),
                    params,
                )
                .await
            }
        }
    }
}

mod wrappers {
    use crate::exchanges::hyperliquid::HyperliquidClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; HyperliquidClient;
     public [

     ];
     private [
    transfer_between_dexes(
                source_dex => "sourceDex",
                destination_dex => "destinationDex",
                token => "token",
                amount => "amount"
            ),
    transfer_usdc_spot_perp(
                amount => "amount",
                to_perp => "toPerp",
                nonce => "nonce",
                signature => "signature",
                signature_chain_id => "signatureChainId"
            ),
    transfer_vault_usd(target_vault => "targetVault", is_deposit => "isDeposit", usd => "usd"),
    transfer_hip3_liquidator(dex => "dex", ntl => "ntl", is_deposit => "isDeposit"),
    transfer_sub_account_usd(
                sub_account_user => "subAccountUser",
                is_deposit => "isDeposit",
                usd => "usd"
            ),
    transfer_sub_account_spot(
                sub_account_user => "subAccountUser",
                is_deposit => "isDeposit",
                token => "token",
                amount => "amount"
            )
     ];
    }
}
