use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};
use serde_json::{Map, Value};

use super::client::ExtendedClient;
use super::endpoints::*;
use super::params::{
    body_object, json_bool, json_string, json_u64, object_allowed, object_required, path_with_id,
    validate_non_negative_decimal, validate_positive_decimal, ExtendedParams,
};
use super::signing::{
    build_signed_order, extract_market_from_param, extract_market_from_response,
    signed_order_response, StarknetDomain,
};

impl ExtendedClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = ExtendedParams::from_pairs(params);
        if let Some(response) = self.account_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.trade_private_request(method_name, &params).await? {
            return Ok(response);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Extended private method: {method_name}"
        )))
    }

    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &ExtendedParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "get_open_orders" => {
                params.ensure_allowed(&["market", "type", "side"], &["market"])?;
                params.optional_one_of("type", &["LIMIT", "CONDITIONAL", "TPSL", "TWAP"])?;
                params.optional_one_of("side", &["BUY", "SELL"])?;
                self.private_get(ORDERS, params.only(&["market", "type", "side"]))
                    .await
            }
            "get_orders_history" | "get_order_history" => {
                params.ensure_allowed(
                    &[
                        "id",
                        "externalId",
                        "market",
                        "type",
                        "side",
                        "cursor",
                        "limit",
                        "sort",
                    ],
                    &["id", "externalId", "market"],
                )?;
                params.repeated_u64_range("id", 1, u64::MAX)?;
                params
                    .optional_one_of("type", &["LIMIT", "MARKET", "CONDITIONAL", "TPSL", "TWAP"])?;
                params.optional_one_of("side", &["BUY", "SELL"])?;
                params.optional_one_of("sort", &["ID", "UPDATED_AT"])?;
                params.optional_u64_range("cursor", 0, u64::MAX)?;
                params.optional_u64_range("limit", 1, 10_000)?;
                self.private_get(
                    ORDERS_HISTORY,
                    params.only(&[
                        "id",
                        "externalId",
                        "market",
                        "type",
                        "side",
                        "cursor",
                        "limit",
                        "sort",
                    ]),
                )
                .await
            }
            "get_order" => {
                params.ensure_allowed(&["id"], &[])?;
                params.required_u64_range("id", 1, u64::MAX)?;
                let path = path_with_id(ORDERS, params.required("id")?);
                self.private_get(&path, Vec::new()).await
            }
            "get_orders_by_external_id" | "get_order_by_external_id" => {
                params.ensure_allowed(&["externalId", "external_id"], &[])?;
                params.ensure_exactly_one(&["externalId", "external_id"])?;
                let external_id = if params.get("externalId").is_some() {
                    params.path_segment("externalId")?
                } else {
                    params.path_segment("external_id")?
                };
                let path = format!("{ORDERS}/external/{}", external_id);
                self.private_get(&path, Vec::new()).await
            }
            "place_order" | "create_order" => match params.body_optional()? {
                Some(body) => {
                    params.ensure_allowed(&["body", "order"], &[])?;
                    validate_order_body(&body, self.signing_domain())?;
                    self.private_post_value(ORDER, body, Vec::new()).await
                }
                None => {
                    validate_signing_params(params)?;
                    self.place_signed_limit_order(params).await
                }
            },
            "place_limit_order" | "create_limit_order" => {
                validate_signing_params(params)?;
                self.place_signed_limit_order(params).await
            }
            "sign_create_order" | "sign_order" => {
                validate_signing_params(params)?;
                let signed = self.signed_order_from_params(params).await?;
                return Ok(Some(signed_order_response(signed.body, signed.order_hash)));
            }
            "cancel_order" => {
                params.ensure_allowed(&["id"], &[])?;
                params.required_u64_range("id", 1, u64::MAX)?;
                let path = path_with_id(ORDER, params.required("id")?);
                self.private_delete(&path, Vec::new()).await
            }
            "cancel_order_by_external_id" => {
                params.ensure_allowed(&["externalId"], &[])?;
                self.private_delete(
                    ORDER,
                    vec![(
                        "externalId".to_string(),
                        params.required("externalId")?.to_string(),
                    )],
                )
                .await
            }
            "mass_cancel" => {
                params.ensure_allowed(&["body"], &[])?;
                let body = params.body_required()?;
                validate_mass_cancel_body(&body)?;
                self.private_post_value(MASS_CANCEL, body, Vec::new()).await
            }
            "set_deadmanswitch" | "set_deadman_switch" => {
                params.ensure_allowed(&["countdownTime"], &[])?;
                params.required_u64_range("countdownTime", 0, u64::MAX)?;
                self.request(
                    crate::http::HttpMethod::Post,
                    DEADMAN_SWITCH,
                    params.only(&["countdownTime"]),
                    None,
                    true,
                    std::collections::BTreeMap::new(),
                )
                .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    async fn place_signed_limit_order(&self, params: &ExtendedParams) -> Result<ValidatedResponse> {
        let signed = self.signed_order_from_params(params).await?;
        self.private_post_value(ORDER, signed.body, Vec::new())
            .await
    }

    async fn signed_order_from_params(
        &self,
        params: &ExtendedParams,
    ) -> Result<super::signing::ExtendedSignedOrder> {
        let credentials = self.signing_credentials()?.clone();
        let market_name = self.signed_order_market(params)?;
        let market = match extract_market_from_param(params, &market_name)? {
            Some(market) => market,
            None => {
                let response = self
                    .public_get(MARKETS, vec![("market".to_string(), market_name.clone())])
                    .await?;
                extract_market_from_response(&response.data, &market_name)?
            }
        };
        let params = self.with_order_fee(params, &market_name).await?;
        build_signed_order(&params, market, &credentials, self.signing_domain())
    }

    async fn with_order_fee(
        &self,
        params: &ExtendedParams,
        market: &str,
    ) -> Result<ExtendedParams> {
        if params.first(&["fee", "taker_fee", "takerFee"]).is_some() {
            return Ok(params.clone());
        }

        let mut query = vec![("market".to_string(), market.to_string())];
        if let Some(builder_id) = params.first(&["builder_id", "builderId"]) {
            query.push(("builderId".to_string(), builder_id.to_string()));
        }
        let response = self.private_get(FEES, query).await?;
        let post_only = matches!(
            params.first(&["post_only", "postOnly"]),
            Some("true" | "TRUE" | "1" | "yes" | "YES")
        );
        Ok(params.with("fee", fee_from_response(&response.data, market, post_only)?))
    }

    fn signed_order_market(&self, params: &ExtendedParams) -> Result<String> {
        if let Some(product_symbol) = params.get("product_symbol") {
            return self.exchange_symbol(product_symbol);
        }
        if let Some(market) = params.get("market") {
            return self.exchange_symbol(market);
        }
        Err(DcexError::InvalidInput(
            "missing required parameter: market or product_symbol".to_string(),
        ))
    }
}

fn validate_signing_params(params: &ExtendedParams) -> Result<()> {
    const ALLOWED: &[&str] = &[
        "market",
        "product_symbol",
        "side",
        "qty",
        "quantity",
        "amount",
        "amount_of_synthetic",
        "price",
        "type",
        "order_type",
        "orderType",
        "post_only",
        "postOnly",
        "time_in_force",
        "timeInForce",
        "reduce_only",
        "reduceOnly",
        "expiry_epoch_millis",
        "expiryEpochMillis",
        "expire_time_ms",
        "nonce",
        "fee",
        "taker_fee",
        "takerFee",
        "self_trade_protection_level",
        "selfTradeProtectionLevel",
        "id",
        "external_id",
        "externalId",
        "order_external_id",
        "builder_fee",
        "builderFee",
        "builder_id",
        "builderId",
    ];
    params.ensure_allowed(ALLOWED, &[])?;
    params.ensure_exactly_one(&["market", "product_symbol"])?;
    params.ensure_exactly_one(&["qty", "quantity", "amount", "amount_of_synthetic"])?;
    for group in [
        &["type", "order_type", "orderType"][..],
        &["post_only", "postOnly"],
        &["time_in_force", "timeInForce"],
        &["reduce_only", "reduceOnly"],
        &["expiry_epoch_millis", "expiryEpochMillis", "expire_time_ms"],
        &["fee", "taker_fee", "takerFee"],
        &["self_trade_protection_level", "selfTradeProtectionLevel"],
        &["id", "external_id", "externalId", "order_external_id"],
        &["builder_fee", "builderFee"],
        &["builder_id", "builderId"],
    ] {
        params.ensure_at_most_one(group)?;
    }
    params.first_required(&["side"])?;
    params.required_positive_decimal("price")?;
    let qty = params.first_required(&["qty", "quantity", "amount", "amount_of_synthetic"])?;
    validate_positive_decimal("qty", qty)?;
    if let Some(order_type) = params.first(&["type", "order_type", "orderType"]) {
        if !order_type.eq_ignore_ascii_case("LIMIT") {
            return Err(DcexError::InvalidInput(
                "Extended automatic order signing currently supports LIMIT orders only".to_string(),
            ));
        }
    }
    for key in ["post_only", "postOnly", "reduce_only", "reduceOnly"] {
        params.optional_bool(key)?;
    }
    if let Some(time_in_force) = params.first(&["time_in_force", "timeInForce"]) {
        if !matches!(time_in_force, "GTT" | "IOC") {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Extended time_in_force: {time_in_force}"
            )));
        }
    }
    for key in ["expiry_epoch_millis", "expiryEpochMillis", "expire_time_ms"] {
        params.optional_u64_range(key, 1, u64::MAX)?;
    }
    params.optional_u64_range("nonce", 1, 1u64 << 31)?;
    if let Some(fee) = params.first(&["fee", "taker_fee", "takerFee"]) {
        validate_fraction("fee", fee)?;
    }
    if let Some(level) = params.first(&["self_trade_protection_level", "selfTradeProtectionLevel"])
    {
        if !matches!(level, "DISABLED" | "ACCOUNT" | "CLIENT") {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Extended self trade protection level: {level}"
            )));
        }
    }
    if let Some(builder_fee) = params.first(&["builder_fee", "builderFee"]) {
        validate_fraction("builderFee", builder_fee)?;
    }
    for key in ["builder_id", "builderId"] {
        params.optional_u64_range(key, 1, u64::MAX)?;
    }
    if params.first(&["builder_fee", "builderFee"]).is_some()
        != params.first(&["builder_id", "builderId"]).is_some()
    {
        return Err(DcexError::InvalidInput(
            "Extended builderFee and builderId must be provided together".to_string(),
        ));
    }
    Ok(())
}

fn validate_order_body(body: &Value, domain: StarknetDomain) -> Result<()> {
    let body = body_object(body, "order body")?;
    object_allowed(
        body,
        &[
            "id",
            "market",
            "type",
            "side",
            "qty",
            "price",
            "reduceOnly",
            "postOnly",
            "timeInForce",
            "expiryEpochMillis",
            "fee",
            "cancelId",
            "settlement",
            "nonce",
            "selfTradeProtectionLevel",
            "trigger",
            "tpSlType",
            "takeProfit",
            "stopLoss",
            "builderFee",
            "builderId",
            "debuggingAmounts",
        ],
    )?;
    for key in ["id", "market"] {
        json_string(body, key, true)?;
    }
    let order_type = required_json_enum(body, "type", &["LIMIT", "MARKET", "CONDITIONAL", "TPSL"])?;
    required_json_enum(body, "side", &["BUY", "SELL"])?;
    let qty = json_decimal(body, "qty", true)?.expect("required qty");
    validate_non_negative_decimal("qty", qty)?;
    required_json_enum(body, "timeInForce", &["GTT", "IOC"])?;
    let expiry = json_u64(body, "expiryEpochMillis", true)?.expect("required expiry");
    validate_expiry(expiry, domain)?;
    let fee = json_decimal(body, "fee", true)?.expect("required fee");
    validate_fraction("fee", fee)?;
    let nonce = json_u64(body, "nonce", true)?.expect("required nonce");
    if !(1..=(1u64 << 31)).contains(&nonce) {
        return Err(DcexError::InvalidInput(
            "Extended JSON field nonce must be between 1 and 2147483648".to_string(),
        ));
    }
    required_json_enum(
        body,
        "selfTradeProtectionLevel",
        &["DISABLED", "ACCOUNT", "CLIENT"],
    )?;
    let reduce_only = json_bool(body, "reduceOnly")?.unwrap_or(false);
    let post_only = json_bool(body, "postOnly")?.unwrap_or(false);
    let price = json_decimal(body, "price", order_type != "TPSL")?;
    if let Some(price) = price {
        if order_type == "TPSL" {
            validate_non_negative_decimal("price", price)?;
        } else {
            validate_positive_decimal("price", price)?;
        }
    }
    if let Some(cancel_id) = body.get("cancelId") {
        if !cancel_id.is_null() {
            json_string(body, "cancelId", false)?;
        }
    }
    if let Some(builder_fee) = json_decimal(body, "builderFee", false)? {
        validate_fraction("builderFee", builder_fee)?;
    }
    let builder_id = json_u64(body, "builderId", false)?;
    if body.get("builderFee").is_some() != builder_id.is_some() {
        return Err(DcexError::InvalidInput(
            "Extended builderFee and builderId must be provided together".to_string(),
        ));
    }
    if matches!(order_type, "LIMIT" | "MARKET" | "CONDITIONAL") {
        let settlement = object_required(body, "settlement")?;
        validate_settlement(settlement, "settlement")?;
    }
    match order_type {
        "LIMIT" => {
            if !qty_is_positive(qty)? {
                return Err(DcexError::InvalidInput(
                    "Extended LIMIT order qty must be greater than zero".to_string(),
                ));
            }
        }
        "MARKET" => {
            if post_only || json_string(body, "timeInForce", true)? != Some("IOC") {
                return Err(DcexError::InvalidInput(
                    "Extended MARKET orders require IOC and cannot be post-only".to_string(),
                ));
            }
            if !qty_is_positive(qty)? {
                return Err(DcexError::InvalidInput(
                    "Extended MARKET order qty must be greater than zero".to_string(),
                ));
            }
        }
        "CONDITIONAL" => {
            if !qty_is_positive(qty)? {
                return Err(DcexError::InvalidInput(
                    "Extended CONDITIONAL order qty must be greater than zero".to_string(),
                ));
            }
            validate_trigger(object_required(body, "trigger")?)?;
        }
        "TPSL" => {
            if !reduce_only || post_only {
                return Err(DcexError::InvalidInput(
                    "Extended TPSL orders must be reduce-only and cannot be post-only".to_string(),
                ));
            }
            let tp_sl_type = required_json_enum(body, "tpSlType", &["ORDER", "POSITION"])?;
            let qty = qty.parse::<f64>().map_err(|error| {
                DcexError::InvalidInput(format!("invalid Extended decimal qty: {error}"))
            })?;
            if (tp_sl_type == "ORDER" && qty <= 0.0) || (tp_sl_type == "POSITION" && qty != 0.0) {
                return Err(DcexError::InvalidInput(
                    "Extended TPSL ORDER qty must be positive and POSITION qty must be zero"
                        .to_string(),
                ));
            }
            if price.is_some_and(|price| price.parse::<f64>().ok() != Some(0.0)) {
                return Err(DcexError::InvalidInput(
                    "Extended TPSL price must be zero when provided".to_string(),
                ));
            }
            if body.get("takeProfit").is_none() && body.get("stopLoss").is_none() {
                return Err(DcexError::InvalidInput(
                    "Extended TPSL orders require takeProfit or stopLoss".to_string(),
                ));
            }
            for key in ["takeProfit", "stopLoss"] {
                if let Some(value) = body.get(key) {
                    validate_tpsl_trigger(value, key)?;
                }
            }
        }
        _ => unreachable!(),
    }
    Ok(())
}

fn validate_mass_cancel_body(body: &Value) -> Result<()> {
    let body = body_object(body, "mass cancel body")?;
    object_allowed(
        body,
        &["markets", "cancelAll", "orderIds", "externalOrderIds"],
    )?;
    if body.is_empty() {
        return Err(DcexError::InvalidInput(
            "Extended mass cancel requires at least one field".to_string(),
        ));
    }
    json_bool(body, "cancelAll")?;
    validate_non_empty_array(body, "markets", |value| {
        value.as_str().is_some_and(|value| !value.trim().is_empty())
    })?;
    validate_non_empty_array(body, "externalOrderIds", |value| {
        value.as_str().is_some_and(|value| !value.trim().is_empty())
    })?;
    validate_non_empty_array(body, "orderIds", |value| {
        value.as_u64().is_some_and(|value| value > 0)
    })?;
    Ok(())
}

fn validate_non_empty_array(
    object: &Map<String, Value>,
    key: &str,
    valid: impl Fn(&Value) -> bool,
) -> Result<()> {
    let Some(value) = object.get(key) else {
        return Ok(());
    };
    let values = value.as_array().ok_or_else(|| {
        DcexError::InvalidInput(format!("Extended JSON field {key} must be an array"))
    })?;
    if values.is_empty() || !values.iter().all(valid) {
        return Err(DcexError::InvalidInput(format!(
            "Extended JSON field {key} must be a non-empty array of valid values"
        )));
    }
    Ok(())
}

fn required_json_enum<'a>(
    object: &'a Map<String, Value>,
    key: &str,
    allowed: &[&str],
) -> Result<&'a str> {
    let value = json_string(object, key, true)?.expect("required string");
    if !allowed.contains(&value) {
        return Err(DcexError::InvalidInput(format!(
            "invalid Extended JSON field {key}: {value}; expected one of {}",
            allowed.join(", ")
        )));
    }
    Ok(value)
}

fn json_decimal<'a>(
    object: &'a Map<String, Value>,
    key: &str,
    required: bool,
) -> Result<Option<&'a str>> {
    let Some(value) = object.get(key) else {
        if required {
            object_required(object, key)?;
        }
        return Ok(None);
    };
    let value = value.as_str().ok_or_else(|| {
        DcexError::InvalidInput(format!(
            "Extended JSON field {key} must be a decimal string"
        ))
    })?;
    if value.trim().is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "Extended JSON field {key} must not be empty"
        )));
    }
    Ok(Some(value))
}

fn validate_trigger(value: &Value) -> Result<()> {
    let trigger = body_object(value, "trigger")?;
    object_allowed(
        trigger,
        &[
            "triggerPrice",
            "triggerPriceType",
            "direction",
            "executionPriceType",
        ],
    )?;
    validate_positive_decimal(
        "trigger.triggerPrice",
        json_decimal(trigger, "triggerPrice", true)?.expect("required trigger price"),
    )?;
    required_json_enum(trigger, "triggerPriceType", &["LAST", "MARK", "INDEX"])?;
    required_json_enum(trigger, "direction", &["UP", "DOWN"])?;
    required_json_enum(trigger, "executionPriceType", &["LIMIT", "MARKET"])?;
    Ok(())
}

fn validate_tpsl_trigger(value: &Value, key: &str) -> Result<()> {
    let trigger = body_object(value, key)?;
    object_allowed(
        trigger,
        &[
            "triggerPrice",
            "triggerPriceType",
            "price",
            "priceType",
            "settlement",
            "debuggingAmounts",
        ],
    )?;
    for field in ["triggerPrice", "price"] {
        validate_positive_decimal(
            &format!("{key}.{field}"),
            json_decimal(trigger, field, true)?.expect("required TPSL decimal"),
        )?;
    }
    required_json_enum(trigger, "triggerPriceType", &["LAST", "MARK", "INDEX"])?;
    required_json_enum(trigger, "priceType", &["LIMIT", "MARKET"])?;
    validate_settlement(
        object_required(trigger, "settlement")?,
        &format!("{key}.settlement"),
    )?;
    Ok(())
}

fn validate_settlement(value: &Value, field: &str) -> Result<()> {
    let settlement = body_object(value, field)?;
    object_allowed(settlement, &["signature", "starkKey", "collateralPosition"])?;
    let signature = body_object(
        object_required(settlement, "signature")?,
        &format!("{field}.signature"),
    )?;
    object_allowed(signature, &["r", "s"])?;
    for key in ["r", "s"] {
        let value = json_string(signature, key, true)?.expect("required signature value");
        if !is_hex(value) {
            return Err(DcexError::InvalidInput(format!(
                "Extended JSON field {field}.signature.{key} must be hexadecimal"
            )));
        }
    }
    let stark_key = json_string(settlement, "starkKey", true)?.expect("required Stark key");
    if !is_hex(stark_key) {
        return Err(DcexError::InvalidInput(format!(
            "Extended JSON field {field}.starkKey must be hexadecimal"
        )));
    }
    let collateral =
        json_string(settlement, "collateralPosition", true)?.expect("required collateral position");
    collateral.parse::<u64>().map_err(|error| {
        DcexError::InvalidInput(format!(
            "invalid Extended JSON field {field}.collateralPosition: {error}"
        ))
    })?;
    Ok(())
}

fn validate_fraction(key: &str, value: &str) -> Result<()> {
    validate_non_negative_decimal(key, value)?;
    let value = value.parse::<f64>().map_err(|error| {
        DcexError::InvalidInput(format!("invalid Extended decimal {key}: {error}"))
    })?;
    if value > 1.0 {
        return Err(DcexError::InvalidInput(format!(
            "Extended {key} must not exceed 1"
        )));
    }
    Ok(())
}

fn is_hex(value: &str) -> bool {
    let value = value.strip_prefix("0x").unwrap_or(value);
    !value.is_empty() && value.chars().all(|character| character.is_ascii_hexdigit())
}

fn validate_expiry(expiry_epoch_millis: u64, domain: StarknetDomain) -> Result<()> {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_err(|error| DcexError::Runtime(error.to_string()))?;
    let now =
        u64::try_from(now.as_millis()).map_err(|error| DcexError::Runtime(error.to_string()))?;
    let max_days = if domain.chain_id == "SN_SEPOLIA" {
        28
    } else {
        90
    };
    let max_order_lifetime_ms = max_days * 24 * 60 * 60 * 1_000;
    if expiry_epoch_millis <= now || expiry_epoch_millis - now > max_order_lifetime_ms {
        return Err(DcexError::InvalidInput(
            format!(
                "Extended expiryEpochMillis must be in the future and no more than {max_days} days away"
            ),
        ));
    }
    Ok(())
}

fn qty_is_positive(qty: &str) -> Result<bool> {
    let qty = qty.parse::<f64>().map_err(|error| {
        DcexError::InvalidInput(format!("invalid Extended decimal qty: {error}"))
    })?;
    Ok(qty.is_finite() && qty > 0.0)
}

fn fee_from_response(data: &Value, market: &str, post_only: bool) -> Result<String> {
    let fees = data.get("data").and_then(Value::as_array).ok_or_else(|| {
        DcexError::Decode("Extended get_fees response did not contain data".to_string())
    })?;
    let fee = fees
        .iter()
        .find(|entry| entry.get("market").and_then(Value::as_str) == Some(market))
        .and_then(|entry| {
            entry.get(if post_only {
                "makerFeeRate"
            } else {
                "takerFeeRate"
            })
        })
        .and_then(Value::as_str)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| {
            DcexError::Decode(format!(
                "Extended get_fees response did not contain a fee rate for {market}"
            ))
        })?;
    Ok(fee.to_string())
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::fee_from_response;

    #[test]
    fn selects_maker_or_taker_rate_from_fee_response() {
        let data = json!({
            "status": "OK",
            "data": [{
                "market": "BTC-USD",
                "makerFeeRate": "0.00000",
                "takerFeeRate": "0.00025"
            }]
        });

        assert_eq!(
            fee_from_response(&data, "BTC-USD", true).unwrap(),
            "0.00000"
        );
        assert_eq!(
            fee_from_response(&data, "BTC-USD", false).unwrap(),
            "0.00025"
        );
    }
}
