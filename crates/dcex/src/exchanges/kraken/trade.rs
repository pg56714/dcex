use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::{KrakenAuth, KrakenClient};
use super::endpoints::*;
use super::params::{push_optional, require_one_identifier, KrakenParams};

impl KrakenClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &KrakenParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_spot_order" => {
                self.place_spot_order_request(params, None, None, None)
                    .await
            }
            "place_spot_market_order" => {
                self.place_spot_order_request(params, None, Some("market"), None)
                    .await
            }
            "place_spot_market_buy_order" => {
                self.place_spot_order_request(params, Some("buy"), Some("market"), None)
                    .await
            }
            "place_spot_market_sell_order" => {
                self.place_spot_order_request(params, Some("sell"), Some("market"), None)
                    .await
            }
            "place_spot_limit_order" => {
                self.place_spot_order_request(params, None, Some("limit"), None)
                    .await
            }
            "place_spot_limit_buy_order" => {
                self.place_spot_order_request(params, Some("buy"), Some("limit"), None)
                    .await
            }
            "place_spot_limit_sell_order" => {
                self.place_spot_order_request(params, Some("sell"), Some("limit"), None)
                    .await
            }
            "place_spot_post_only_limit_order" => {
                self.place_spot_order_request(params, None, Some("limit"), Some("post"))
                    .await
            }
            "place_spot_post_only_limit_buy_order" => {
                self.place_spot_order_request(params, Some("buy"), Some("limit"), Some("post"))
                    .await
            }
            "place_spot_post_only_limit_sell_order" => {
                self.place_spot_order_request(params, Some("sell"), Some("limit"), Some("post"))
                    .await
            }
            "get_spot_open_orders" => {
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_OPEN_ORDERS,
                    params.only(&["trades", "userref", "cl_ord_id"]),
                )
                .await
            }
            "get_spot_closed_orders" => {
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_CLOSED_ORDERS,
                    params.only(&["trades", "userref", "start", "end", "ofs", "closetime"]),
                )
                .await
            }
            "get_spot_orders" => {
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_QUERY_ORDERS,
                    params.only(&["txid", "trades", "userref"]),
                )
                .await
            }
            "get_spot_trade_history" => {
                let mut query = params.only(&[
                    "trades",
                    "start",
                    "end",
                    "ofs",
                    "without_count",
                    "consolidate_taker",
                ]);
                push_optional(
                    &mut query,
                    "type",
                    params.get("type").or_else(|| params.get("type_")),
                );
                self.private_post(KrakenAuth::Spot, SPOT_TRADES_HISTORY, query)
                    .await
            }
            "cancel_spot_order" => {
                require_one_identifier(params, &["txid", "userref", "cl_ord_id"])?;
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_CANCEL_ORDER,
                    params.only(&["txid", "userref", "cl_ord_id"]),
                )
                .await
            }
            "cancel_spot_all_orders" => {
                self.private_post(KrakenAuth::Spot, SPOT_CANCEL_ALL, Vec::new())
                    .await
            }
            "cancel_spot_all_orders_after" => {
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_CANCEL_ALL_AFTER,
                    params.only(&["timeout"]),
                )
                .await
            }
            "get_spot_websocket_token" => {
                self.private_post(
                    KrakenAuth::Spot,
                    SPOT_WEBSOCKET_TOKEN,
                    params.only(&["permissions"]),
                )
                .await
            }
            "place_futures_order" => {
                self.place_futures_order_request(params, None, None, None)
                    .await
            }
            "place_futures_market_order" => {
                self.place_futures_order_request(params, None, Some("mkt"), None)
                    .await
            }
            "place_futures_market_buy_order" => {
                self.place_futures_order_request(params, Some("buy"), Some("mkt"), None)
                    .await
            }
            "place_futures_market_sell_order" => {
                self.place_futures_order_request(params, Some("sell"), Some("mkt"), None)
                    .await
            }
            "place_futures_limit_order" => {
                self.place_futures_order_request(params, None, Some("lmt"), Some("price"))
                    .await
            }
            "place_futures_limit_buy_order" => {
                self.place_futures_order_request(params, Some("buy"), Some("lmt"), Some("price"))
                    .await
            }
            "place_futures_limit_sell_order" => {
                self.place_futures_order_request(params, Some("sell"), Some("lmt"), Some("price"))
                    .await
            }
            "place_futures_post_only_limit_order" => {
                self.place_futures_order_request(params, None, Some("post"), Some("price"))
                    .await
            }
            "place_futures_post_only_limit_buy_order" => {
                self.place_futures_order_request(params, Some("buy"), Some("post"), Some("price"))
                    .await
            }
            "place_futures_post_only_limit_sell_order" => {
                self.place_futures_order_request(params, Some("sell"), Some("post"), Some("price"))
                    .await
            }
            "get_futures_open_orders" => {
                self.private_get(KrakenAuth::Futures, FUTURES_OPEN_ORDERS, Vec::new())
                    .await
            }
            "get_futures_order_status" => {
                self.private_post(
                    KrakenAuth::Futures,
                    FUTURES_ORDER_STATUS,
                    params.only(&["orderIds", "cliOrdIds"]),
                )
                .await
            }
            "cancel_futures_order" => {
                require_one_identifier(params, &["order_id", "cliOrdId"])?;
                self.private_post(
                    KrakenAuth::Futures,
                    FUTURES_CANCEL_ORDER,
                    params.only(&["order_id", "cliOrdId"]),
                )
                .await
            }
            "cancel_futures_all_orders" => {
                let mut query = Vec::new();
                self.push_product_symbol(&mut query, params, "symbol", "PF_")?;
                self.private_post(KrakenAuth::Futures, FUTURES_CANCEL_ALL, query)
                    .await
            }
            _ => return Ok(None),
        };

        Ok(Some(result?))
    }

    async fn place_spot_order_request(
        &self,
        params: &KrakenParams,
        side: Option<&str>,
        ordertype: Option<&str>,
        oflags: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut query = Vec::new();
        self.push_required_product_symbol(&mut query, params, "pair", "")?;
        push_required_or_override(&mut query, "type", side, params, "side")?;
        push_required_or_override(&mut query, "ordertype", ordertype, params, "ordertype")?;
        push_required_param(&mut query, params, "volume")?;
        push_optional(&mut query, "price", params.get("price"));
        push_optional(&mut query, "price2", params.get("price2"));
        push_optional(&mut query, "displayvol", params.get("displayvol"));
        push_optional(&mut query, "leverage", params.get("leverage"));
        push_optional(&mut query, "oflags", params.get("oflags").or(oflags));
        push_optional(&mut query, "timeinforce", params.get("timeinforce"));
        push_optional(&mut query, "expiretm", params.get("expiretm"));
        push_optional(&mut query, "starttm", params.get("starttm"));
        push_optional(&mut query, "asset_class", params.get("asset_class"));
        push_optional(&mut query, "trigger", params.get("trigger"));
        push_optional(&mut query, "stptype", params.get("stptype"));
        push_optional(&mut query, "reduce_only", params.get("reduce_only"));
        push_optional(&mut query, "userref", params.get("userref"));
        push_optional(&mut query, "cl_ord_id", params.get("cl_ord_id"));
        push_optional(&mut query, "validate", params.get("validate"));
        push_optional(&mut query, "deadline", params.get("deadline"));
        push_optional(&mut query, "broker", params.get("broker"));
        push_optional(
            &mut query,
            "close[ordertype]",
            params.get("close[ordertype]"),
        );
        push_optional(&mut query, "close[price]", params.get("close[price]"));
        push_optional(&mut query, "close[price2]", params.get("close[price2]"));

        self.private_post(KrakenAuth::Spot, SPOT_ADD_ORDER, query)
            .await
    }

    async fn place_futures_order_request(
        &self,
        params: &KrakenParams,
        side: Option<&str>,
        order_type: Option<&str>,
        limit_price_alias: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut query = Vec::new();
        self.push_required_product_symbol(&mut query, params, "symbol", "PF_")?;
        push_required_or_override(&mut query, "side", side, params, "side")?;
        push_required_or_override(&mut query, "orderType", order_type, params, "orderType")?;
        push_required_param(&mut query, params, "size")?;

        let limit_price = params
            .get("limitPrice")
            .or_else(|| limit_price_alias.and_then(|alias| params.get(alias)));
        push_optional(&mut query, "limitPrice", limit_price);
        push_optional(&mut query, "stopPrice", params.get("stopPrice"));
        push_optional(&mut query, "cliOrdId", params.get("cliOrdId"));
        push_optional(&mut query, "triggerSignal", params.get("triggerSignal"));
        push_optional(&mut query, "reduceOnly", params.get("reduceOnly"));
        push_optional(&mut query, "processBefore", params.get("processBefore"));
        push_optional(
            &mut query,
            "trailingStopMaxDeviation",
            params.get("trailingStopMaxDeviation"),
        );
        push_optional(
            &mut query,
            "trailingStopDeviationUnit",
            params.get("trailingStopDeviationUnit"),
        );
        push_optional(
            &mut query,
            "limitPriceOffsetValue",
            params.get("limitPriceOffsetValue"),
        );
        push_optional(
            &mut query,
            "limitPriceOffsetUnit",
            params.get("limitPriceOffsetUnit"),
        );
        push_optional(&mut query, "broker", params.get("broker"));

        self.private_post(KrakenAuth::Futures, FUTURES_SEND_ORDER, query)
            .await
    }
}

fn push_required_or_override(
    query: &mut Vec<(String, String)>,
    key: &str,
    override_value: Option<&str>,
    params: &KrakenParams,
    fallback_key: &str,
) -> Result<()> {
    let value = match override_value {
        Some(value) => value,
        None => params.required(fallback_key)?,
    };
    query.push((key.to_string(), value.to_string()));
    Ok(())
}

fn push_required_param(
    query: &mut Vec<(String, String)>,
    params: &KrakenParams,
    key: &str,
) -> Result<()> {
    query.push((key.to_string(), params.required(key)?.to_string()));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn push_required_or_override_uses_override_without_fallback_key() {
        let params = KrakenParams::from_pairs(Vec::new());
        let mut query = Vec::new();

        push_required_or_override(&mut query, "side", Some("buy"), &params, "side")
            .expect("override should be enough");

        assert_eq!(query, vec![("side".to_string(), "buy".to_string())]);
    }

    #[test]
    fn push_required_or_override_requires_fallback_without_override() {
        let params = KrakenParams::from_pairs(Vec::new());
        let mut query = Vec::new();

        let error = push_required_or_override(&mut query, "side", None, &params, "side")
            .expect_err("fallback should be required");

        assert!(error
            .to_string()
            .contains("missing required parameter: side"));
    }
}
