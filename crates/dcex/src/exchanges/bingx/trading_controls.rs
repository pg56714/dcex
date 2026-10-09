//! Additional documented swap lifecycle and risk controls.
use super::client::BingxClient;
use super::params::{
    BingxParams, require_one_identifier, validate_bool, validate_client_id, validate_enum,
    validate_positive_number, validate_time_range, validate_u64_range,
};
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

impl BingxClient {
    pub(super) async fn trading_controls_request(
        &self,
        name: &str,
        params: &BingxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, post, fields, required): (&str, bool, &[&str], &[&str]) = match name {
            "set_swap_cancel_all_after" => (
                "/openApi/swap/v2/trade/cancelAllAfter",
                true,
                &["type", "timeOut", "recvWindow"],
                &["type", "timeOut"],
            ),
            "get_swap_open_order" => (
                "/openApi/swap/v2/trade/openOrder",
                false,
                &["product_symbol", "orderId", "clientOrderId", "recvWindow"],
                &["product_symbol"],
            ),
            "get_swap_force_orders" => (
                "/openApi/swap/v2/trade/forceOrders",
                false,
                &[
                    "product_symbol",
                    "currency",
                    "autoCloseType",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ],
                &[],
            ),
            "get_swap_trade_fills" => (
                "/openApi/swap/v2/trade/allFillOrders",
                false,
                &[
                    "tradingUnit",
                    "startTs",
                    "endTs",
                    "orderId",
                    "currency",
                    "recvWindow",
                ],
                &["tradingUnit", "startTs", "endTs"],
            ),
            "adjust_swap_position_margin" => (
                "/openApi/swap/v2/trade/positionMargin",
                true,
                &[
                    "product_symbol",
                    "amount",
                    "positionSide",
                    "positionId",
                    "type",
                    "recvWindow",
                ],
                &["product_symbol", "amount", "type"],
            ),
            "amend_swap_order" => (
                "/openApi/swap/v1/trade/amend",
                true,
                &[
                    "product_symbol",
                    "orderId",
                    "clientOrderId",
                    "quantity",
                    "recvWindow",
                ],
                &["product_symbol", "quantity"],
            ),
            "place_swap_twap_order" => (
                "/openApi/swap/v1/twap/order",
                true,
                &[
                    "product_symbol",
                    "side",
                    "positionSide",
                    "priceType",
                    "priceVariance",
                    "triggerPrice",
                    "interval",
                    "amountPerOrder",
                    "totalAmount",
                    "recvWindow",
                ],
                &[
                    "product_symbol",
                    "side",
                    "positionSide",
                    "priceType",
                    "priceVariance",
                    "triggerPrice",
                    "interval",
                    "amountPerOrder",
                    "totalAmount",
                ],
            ),
            "cancel_swap_twap_order" => (
                "/openApi/swap/v1/twap/cancelOrder",
                true,
                &["mainOrderId", "recvWindow"],
                &["mainOrderId"],
            ),
            "get_swap_open_twap_orders" => (
                "/openApi/swap/v1/twap/openOrders",
                false,
                &["product_symbol", "recvWindow"],
                &[],
            ),
            "get_swap_twap_order_history" => (
                "/openApi/swap/v1/twap/historyOrders",
                false,
                &[
                    "product_symbol",
                    "pageIndex",
                    "pageSize",
                    "startTime",
                    "endTime",
                    "recvWindow",
                ],
                &["pageIndex", "pageSize", "startTime", "endTime"],
            ),
            "get_swap_twap_order" => (
                "/openApi/swap/v1/twap/orderDetail",
                false,
                &["mainOrderId", "recvWindow"],
                &["mainOrderId"],
            ),
            "get_swap_asset_mode" => (
                "/openApi/swap/v1/trade/assetMode",
                false,
                &["recvWindow"],
                &[],
            ),
            "set_swap_asset_mode" => (
                "/openApi/swap/v1/trade/assetMode",
                true,
                &["assetMode", "recvWindow"],
                &["assetMode"],
            ),
            "get_swap_multi_asset_rules" => (
                "/openApi/swap/v1/trade/multiAssetsRules",
                false,
                &["recvWindow"],
                &[],
            ),
            "get_swap_margin_assets" => (
                "/openApi/swap/v1/user/marginAssets",
                false,
                &["recvWindow"],
                &[],
            ),
            "get_swap_full_orders" => (
                "/openApi/swap/v1/trade/fullOrder",
                false,
                &[
                    "product_symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ],
                &["limit"],
            ),
            "get_swap_fill_history" => (
                "/openApi/swap/v2/trade/fillHistory",
                false,
                &[
                    "product_symbol",
                    "currency",
                    "orderId",
                    "lastFillId",
                    "startTs",
                    "endTs",
                    "pageIndex",
                    "pageSize",
                    "recvWindow",
                ],
                &["product_symbol", "startTs", "endTs"],
            ),
            "get_swap_position_history" => (
                "/openApi/swap/v1/trade/positionHistory",
                false,
                &[
                    "product_symbol",
                    "currency",
                    "positionId",
                    "startTs",
                    "endTs",
                    "pageIndex",
                    "pageSize",
                    "recvWindow",
                ],
                &["product_symbol", "startTs", "endTs"],
            ),
            "get_swap_margin_history" => (
                "/openApi/swap/v1/positionMargin/history",
                false,
                &[
                    "product_symbol",
                    "positionId",
                    "startTime",
                    "endTime",
                    "pageIndex",
                    "pageSize",
                    "recvWindow",
                ],
                &[
                    "product_symbol",
                    "positionId",
                    "startTime",
                    "endTime",
                    "pageIndex",
                    "pageSize",
                ],
            ),
            "get_swap_maintenance_margin_ratios" => (
                "/openApi/swap/v1/maintMarginRatio",
                false,
                &["product_symbol", "recvWindow"],
                &["product_symbol"],
            ),
            "set_swap_auto_add_margin" => (
                "/openApi/swap/v1/trade/autoAddMargin",
                true,
                &[
                    "product_symbol",
                    "positionId",
                    "functionSwitch",
                    "amount",
                    "recvWindow",
                ],
                &["product_symbol", "positionId", "functionSwitch"],
            ),
            _ => return Ok(None),
        };
        params.ensure_allowed(fields)?;
        for key in required {
            params.required(key)?;
        }
        validate_u64_range(params, "recvWindow", 1, 5000)?;
        for key in ["orderId", "positionId", "pageIndex"] {
            validate_u64_range(params, key, 1, u64::MAX)?;
        }
        validate_u64_range(params, "lastFillId", 0, u64::MAX)?;
        validate_u64_range(
            params,
            "limit",
            1,
            if name == "get_swap_force_orders" {
                100
            } else {
                1000
            },
        )?;
        validate_u64_range(
            params,
            "pageSize",
            1,
            if ["get_swap_position_history", "get_swap_margin_history"].contains(&name) {
                100
            } else {
                1000
            },
        )?;
        validate_time_range(params, "startTime", "endTime", None)?;
        validate_time_range(
            params,
            "startTs",
            "endTs",
            if name == "get_swap_position_history" {
                Some(90 * 86_400_000)
            } else {
                None
            },
        )?;
        validate_enum(params, "currency", &["USDT", "USDC"])?;
        validate_enum(params, "positionSide", &["LONG", "SHORT"])?;
        validate_enum(params, "side", &["BUY", "SELL"])?;
        validate_enum(params, "autoCloseType", &["LIQUIDATION", "ADL"])?;
        validate_enum(params, "tradingUnit", &["COIN", "CONT"])?;
        validate_enum(params, "assetMode", &["singleAssetMode", "multiAssetsMode"])?;
        validate_enum(params, "priceType", &["constant", "percentage"])?;
        validate_client_id(params, "clientOrderId", false)?;
        for key in [
            "amount",
            "quantity",
            "priceVariance",
            "triggerPrice",
            "amountPerOrder",
            "totalAmount",
        ] {
            validate_positive_number(params, key)?;
        }
        validate_bool(params, "functionSwitch")?;
        if ["get_swap_open_order", "amend_swap_order"].contains(&name) {
            require_one_identifier(params, &["orderId", "clientOrderId"])?;
        }
        if name == "adjust_swap_position_margin" {
            validate_enum(params, "type", &["1", "2"])?;
        }
        if name == "set_swap_cancel_all_after" {
            validate_enum(params, "type", &["ACTIVATE", "CLOSE"])?;
            validate_u64_range(params, "timeOut", 10, 120)?;
        }
        if name == "place_swap_twap_order" {
            validate_u64_range(params, "interval", 5, 120)?;
            if params.required("amountPerOrder")?.parse::<f64>().unwrap()
                > params.required("totalAmount")?.parse::<f64>().unwrap()
            {
                return Err(DcexError::InvalidInput(
                    "amountPerOrder must not exceed totalAmount".into(),
                ));
            }
        }
        let mut query = params.only(fields);
        query.retain(|(key, _)| key != "product_symbol");
        self.push_optional_symbol(&mut query, params)?;
        Ok(Some(if post {
            self.private_post(path, query).await?
        } else {
            self.private_get(path, query).await?
        }))
    }
}
