use super::trade::*;

impl AsterClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        crate::exchanges::input_contracts::pairs("aster", method_name, &params)?;
        let mut scoped = self.clone();
        scoped.symbol_product_type = Some(
            if method_name.contains("_spot_") || method_name.ends_with("_spot") {
                "spot"
            } else {
                "swap"
            },
        );
        scoped.private_request_scoped(method_name, params).await
    }

    async fn private_request_scoped(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let incomplete = match method_name {
            "place_spot_batch_orders_raw" => Some(HttpMethod::Post),
            "cancel_spot_batch_orders_raw" => Some(HttpMethod::Delete),
            _ => None,
        };
        if let Some(method) = incomplete {
            return self
                .request(
                    method,
                    AsterMarket::Spot,
                    "/api/v3/batchOrders",
                    params,
                    true,
                )
                .await;
        }
        let method_name = if method_name == "trigger_futures_asset_exchange" {
            "trigger_futures_asset_exchange"
        } else {
            method_name
        };
        let params = super::super::operation_guards::validate("aster", method_name, params)?;
        let params = AsterParams::from_pairs(normalize_order_side(method_name, params));
        if let Some(response) = self
            .prediction_dispatch(method_name, &params, false)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self
            .market_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self
            .asset_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self
            .subaccount_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self
            .agents_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self.builder_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self
            .withdrawals_private_request(method_name, &params)
            .await?
        {
            return Ok(response);
        }
        validate_private_params(method_name, &params)?;
        if let Some(response) = self.account_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.trade_private_request(method_name, &params).await? {
            return Ok(response);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Aster private method: {method_name}"
        )))
    }
}
