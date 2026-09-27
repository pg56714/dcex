//! Grouped orders follow the official lighter-go transaction type 28.
use super::*;
use serde::Deserialize;
use std::collections::BTreeSet;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct GroupOrder {
    market_index: i64,
    client_order_index: i64,
    base_amount: i64,
    price: u32,
    is_ask: bool,
    order_type: u8,
    time_in_force: u8,
    #[serde(default)]
    reduce_only: bool,
    #[serde(default)]
    trigger_price: u32,
    order_expiry: Option<i64>,
}

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Lighter grouped orders: {message}"))
}

impl LighterClient {
    pub(super) async fn sign_grouped_orders_from_params(
        &self,
        params: &LighterParams,
    ) -> Result<LighterSignedTransaction> {
        params.ensure_allowed(&[
            "grouping_type",
            "orders",
            "integrator_account_index",
            "integrator_taker_fee",
            "integrator_maker_fee",
            "self_trade_behavior_mode",
            "self_trade_equality_mode",
            "skip_nonce",
            "nonce",
            "api_key_index",
            "price_protection",
        ])?;
        params.optional_bool("price_protection")?;
        let grouping = params.required_u64_range("grouping_type", 1, 3)?;
        let mut orders: Vec<GroupOrder> = serde_json::from_str(params.required("orders")?)
            .map_err(|error| invalid(&format!("invalid orders JSON: {error}")))?;
        if orders.len() != if grouping == 3 { 3 } else { 2 } {
            return Err(invalid("OTO/OCO require two orders; OTOCO requires three"));
        }
        let default_expiry = order_expiry_ms()? as i64;
        let market = orders[0].market_index;
        validate_market_index(market)?;
        self.validate_perps_market_index(market)?;
        let mut identifiers = BTreeSet::new();
        for order in &mut orders {
            if order.market_index != market {
                return Err(invalid("market indexes must match"));
            }
            if !(0..=(1_i64 << 48) - 1).contains(&order.client_order_index)
                || order.client_order_index != 0 && !identifiers.insert(order.client_order_index)
            {
                return Err(invalid("client order indexes must be in range and unique"));
            }
            if !(0..=(1_i64 << 48) - 1).contains(&order.base_amount)
                || order.price == 0
                || order.order_type > 5
                || order.time_in_force > 2
            {
                return Err(invalid(
                    "invalid amount, price, order type or time in force",
                ));
            }
            let expiry = match order.order_expiry {
                None | Some(-1) => {
                    if order.order_type <= 1 && order.time_in_force == 0 {
                        0
                    } else {
                        default_expiry
                    }
                }
                Some(value) => value,
            };
            order.order_expiry = Some(expiry);
            validate_create_order(
                false,
                order.base_amount,
                order.order_type.into(),
                order.time_in_force.into(),
                order.reduce_only,
                order.trigger_price.into(),
                expiry,
            )?;
        }
        let first = &orders[0];
        let children = if grouping == 2 {
            &orders[..]
        } else {
            &orders[1..]
        };
        if grouping != 2 && first.order_type > 1 {
            return Err(invalid("parent must be a market or limit order"));
        }
        for child in children {
            if child.order_type < 2 || !child.reduce_only {
                return Err(invalid("children must be reduce-only TP/SL orders"));
            }
            if grouping != 2 && (child.base_amount != 0 || child.is_ask == first.is_ask) {
                return Err(invalid(
                    "OTO/OTOCO children require zero size and opposite side",
                ));
            }
            if first.order_expiry != Some(0) && child.order_expiry != first.order_expiry {
                return Err(invalid("nonzero order expiries must match"));
            }
        }
        if grouping == 2
            && (orders[0].base_amount != orders[1].base_amount
                || orders[0].is_ask != orders[1].is_ask)
        {
            return Err(invalid("OCO orders require equal sizes and the same side"));
        }
        if children.len() == 2
            && (!(2..=3).contains(&children[0].order_type)
                == !(2..=3).contains(&children[1].order_type)
                || children[0].order_expiry != children[1].order_expiry)
        {
            return Err(invalid(
                "siblings require one TP, one SL, and matching expiry",
            ));
        }
        let attrs = attributes(
            params
                .optional_u64("integrator_account_index")?
                .unwrap_or(0),
            params.optional_u64("integrator_taker_fee")?.unwrap_or(0),
            params.optional_u64("integrator_maker_fee")?.unwrap_or(0),
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
            params
                .optional_u64("self_trade_behavior_mode")?
                .unwrap_or(0),
            params
                .optional_u64("self_trade_equality_mode")?
                .unwrap_or(0),
        )?;
        let api_key_index = self.signing_api_key_index(params)?;
        let account = self.private_account_index(None)?;
        let chain = self.signing_chain_id()?;
        let explicit_nonce = validate_nonce(params)?;
        let nonce = self.next_nonce(explicit_nonce, Some(api_key_index)).await?;
        let expired_at = expiry_ms()?;
        let fields: Vec<[u64; 10]> = orders
            .iter()
            .map(|order| {
                [
                    order.market_index as u64,
                    order.client_order_index as u64,
                    order.base_amount as u64,
                    order.price.into(),
                    order.is_ask.into(),
                    order.order_type.into(),
                    order.time_in_force.into(),
                    order.reduce_only.into(),
                    order.trigger_price.into(),
                    order.order_expiry.unwrap() as u64,
                ]
            })
            .collect();
        let mut values = vec![
            chain as i128,
            28,
            nonce as i128,
            expired_at as i128,
            account as i128,
            api_key_index as i128,
            grouping as i128,
        ];
        values.extend(crate::lighter::grouped_order_hash(&fields)?.map(i128::from));
        let payload_orders: Vec<_> = fields
            .iter()
            .map(|o| {
                json!({
                    "MarketIndex":o[0], "ClientOrderIndex":o[1], "BaseAmount":o[2], "Price":o[3],
                    "IsAsk":o[4], "Type":o[5], "TimeInForce":o[6], "ReduceOnly":o[7],
                    "TriggerPrice":o[8], "OrderExpiry":o[9],
                })
            })
            .collect();
        self.sign_tx(
            28,
            values,
            json!({"AccountIndex":account,"ApiKeyIndex":api_key_index,
            "GroupingType":grouping,"Orders":payload_orders,"Nonce":nonce,"ExpiredAt":expired_at}),
            attrs,
            api_key_index,
        )
    }
}
