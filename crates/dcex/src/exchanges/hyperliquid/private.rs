use super::trade::*;

impl HyperliquidClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        crate::exchanges::input_contracts::pairs("hyperliquid", method_name, &params)?;
        let params = HyperliquidParams::from_pairs(params);
        if let Some(response) = self.catalog_request(method_name, &params, false).await? {
            return Ok(response);
        }
        if let Some(response) = self.transfers_schema_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.builder_schema_request(method_name, &params).await? {
            return Ok(response);
        }
        validate_private_params(method_name, &params)?;
        match method_name {
            "borrow_lend_signed" => {
                let action: Value = serde_json::from_str(params.required("action")?)
                    .map_err(|e| DcexError::InvalidInput(e.to_string()))?;
                if action.get("type").and_then(Value::as_str) != Some("borrowLend") {
                    return Err(DcexError::InvalidInput(
                        "action.type must be borrowLend".into(),
                    ));
                }
                let nonce = params.required_u64("nonce")?;
                let signature = signature_param(&params)?;
                // The public exchange docs and official SDK do not currently specify
                // borrowLend signing. Preserve a caller-signed envelope; do not guess
                // whether it uses L1 or user EIP-712 signing.
                let mut payload =
                    serde_json::json!({"action":action,"nonce":nonce,"signature":signature});
                if params.get("vaultAddress").is_some() {
                    payload["vaultAddress"] = params.address("vaultAddress")?.into();
                }
                if params.get("expiresAfter").is_some() {
                    payload["expiresAfter"] = params.required_u64("expiresAfter")?.into();
                }
                self.request(
                    HttpMethod::Post,
                    EXCHANGE,
                    serde_json::to_vec(&payload).map_err(|e| DcexError::Decode(e.to_string()))?,
                    None,
                    false,
                )
                .await
            }
            "approve_agent_signed" => self.additional_user_action("approveAgent", &params).await,
            "create_sub_account" => {
                self.submit_action(
                    object(vec![
                        ("type", string("createSubAccount")),
                        ("name", string(params.required("name")?)),
                    ]),
                    &params,
                )
                .await
            }
            "transfer_sub_account_usd" => self.dispatch_transfer_sub_account_usd(&params).await,
            "transfer_sub_account_spot" => self.dispatch_transfer_sub_account_spot(&params).await,
            "transfer_vault_usd" => self.dispatch_transfer_vault_usd(&params).await,
            "enable_agent_dex_abstraction" => {
                self.submit_action(
                    object(vec![("type", string("agentEnableDexAbstraction"))]),
                    &params,
                )
                .await
            }
            "transfer_hip3_liquidator" => self.dispatch_transfer_hip3_liquidator(&params).await,
            "deposit_staking_signed" => self.additional_user_action("cDeposit", &params).await,
            "withdraw_staking_signed" => self.dispatch_withdraw_staking_signed(&params).await,
            "delegate_tokens_signed" => self.additional_user_action("tokenDelegate", &params).await,
            "set_user_dex_abstraction_signed" => {
                self.additional_user_action("userDexAbstraction", &params)
                    .await
            }
            "reserve_request_weight" => {
                let weight = params.required_u64("weight")?;
                if weight == 0 {
                    return Err(DcexError::InvalidInput("weight must be positive".into()));
                }
                self.submit_action(
                    object(vec![
                        ("type", string("reserveRequestWeight")),
                        ("weight", uint(weight)),
                    ]),
                    &params,
                )
                .await
            }
            "set_agent_abstraction" => {
                let mode = params.required_one_of("abstraction", &["i", "u", "p"])?;
                self.submit_action(
                    object(vec![
                        ("type", string("agentSetAbstraction")),
                        ("abstraction", string(mode)),
                    ]),
                    &params,
                )
                .await
            }
            "set_user_abstraction" => self.set_user_abstraction_from_params(&params).await,
            "noop" => {
                params.required_u64("nonce")?;
                self.submit_action(object(vec![("type", string("noop"))]), &params)
                    .await
            }
            "place_order" => self.place_order_from_params(&params, None, None).await,
            "place_future_market_order" => self.place_market_order_from_params(&params, None).await,
            "place_future_market_buy_order" => {
                self.place_market_order_from_params(&params, Some(true))
                    .await
            }
            "place_future_market_sell_order" => {
                self.place_market_order_from_params(&params, Some(false))
                    .await
            }
            "place_future_limit_order" => {
                self.place_order_from_params(&params, None, Some(false))
                    .await
            }
            "place_future_limit_buy_order" => {
                self.place_order_from_params(&params, Some(true), Some(false))
                    .await
            }
            "place_future_limit_sell_order" => {
                self.place_order_from_params(&params, Some(false), Some(false))
                    .await
            }
            "place_batch_orders" => self.place_batch_orders_from_params(&params).await,
            "cancel_order" => self.cancel_order_from_params(&params).await,
            "cancel_order_by_cloid" => self.cancel_order_by_cloid_from_params(&params).await,
            "cancel_batch_orders" => self.cancel_batch_orders_from_params(&params).await,
            "cancel_batch_orders_by_cloid" => {
                self.cancel_batch_orders_by_cloid_from_params(&params).await
            }
            "schedule_cancel" => self.schedule_cancel_from_params(&params).await,
            "transfer_between_dexes" => self.transfer_between_dexes_from_params(&params).await,
            "transfer_usdc_spot_perp" => self.transfer_usdc_spot_perp_from_params(&params).await,
            "modify_order" => self.modify_order_from_params(&params).await,
            "modify_batch_orders" => self.modify_batch_orders_from_params(&params).await,
            "update_leverage" => self.update_leverage_from_params(&params).await,
            "update_isolated_margin" => self.update_isolated_margin_from_params(&params).await,
            "place_twap_order" => self.place_twap_order_from_params(&params).await,
            "cancel_twap_order" => self.cancel_twap_order_from_params(&params).await,
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Hyperliquid private method: {method_name}"
            ))),
        }
    }
}
