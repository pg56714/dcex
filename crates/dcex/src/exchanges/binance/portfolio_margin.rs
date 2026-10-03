use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::PublicParams;

impl BinanceClient {
    fn pm_request(
        &self,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, method_name, params)
    }

    pub fn get_pm_account(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_account", Vec::new())
    }

    pub fn get_pm_um_account(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_um_account", Vec::new())
    }

    pub fn get_pm_um_position_risk(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_um_position_risk", Vec::new())
    }

    pub fn get_pm_um_open_orders(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_um_open_orders", Vec::new())
    }

    pub fn get_pm_um_order(
        &self,
        product_symbol: &str,
        order_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_um_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("orderId".into(), order_id.into()),
            ],
        )
    }

    pub fn cancel_pm_um_order(
        &self,
        product_symbol: &str,
        order_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_pm_um_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("orderId".into(), order_id.into()),
            ],
        )
    }

    pub fn cancel_all_pm_um_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_all_pm_um_orders",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn place_pm_um_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
        quantity: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "place_pm_um_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("side".into(), side.into()),
                ("type_".into(), order_type.into()),
                ("quantity".into(), quantity.into()),
            ],
        )
    }

    pub fn place_pm_um_algo_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "place_pm_um_algo_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("side".into(), side.into()),
                ("type_".into(), order_type.into()),
            ],
        )
    }

    pub fn get_pm_um_algo_order(
        &self,
        algo_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_um_algo_order",
            vec![("algoId".into(), algo_id.into())],
        )
    }

    pub fn get_pm_um_algo_order_by_client_id(
        &self,
        client_algo_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_um_algo_order",
            vec![("clientAlgoId".into(), client_algo_id.into())],
        )
    }

    pub fn cancel_pm_um_algo_order(
        &self,
        algo_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_pm_um_algo_order",
            vec![("algoId".into(), algo_id.into())],
        )
    }

    pub fn cancel_pm_um_algo_order_by_client_id(
        &self,
        client_algo_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_pm_um_algo_order",
            vec![("clientAlgoId".into(), client_algo_id.into())],
        )
    }

    pub fn cancel_all_pm_um_algo_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_all_pm_um_algo_orders",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn get_pm_um_open_algo_orders(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_um_open_algo_orders", Vec::new())
    }

    pub fn get_pm_um_algo_order_history(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_um_algo_order_history",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn get_pm_cm_account(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_cm_account", Vec::new())
    }

    pub fn get_pm_cm_position_risk(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_cm_position_risk", Vec::new())
    }

    pub fn get_pm_um_account_config(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_um_account_config", Vec::new())
    }

    pub fn get_pm_um_symbol_config(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_um_symbol_config", Vec::new())
    }

    pub fn get_pm_um_leverage_bracket(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_um_leverage_bracket", Vec::new())
    }

    pub fn get_pm_um_api_trading_status(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_um_api_trading_status", Vec::new())
    }

    pub fn get_pm_cm_adl_quantile(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_cm_adl_quantile",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn get_pm_margin_max_borrowable(
        &self,
        asset: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_margin_max_borrowable",
            vec![("asset".into(), asset.into())],
        )
    }

    pub fn get_pm_um_force_orders(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_um_force_orders", Vec::new())
    }

    pub fn get_pm_cm_force_orders(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_cm_force_orders", Vec::new())
    }

    pub fn get_pm_margin_force_orders(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_margin_force_orders", Vec::new())
    }

    pub fn get_pm_um_all_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_um_all_orders",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn get_pm_um_user_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_um_user_trades",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn get_pm_cm_open_orders(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_cm_open_orders", Vec::new())
    }

    pub fn get_pm_cm_all_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_cm_all_orders",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn get_pm_cm_user_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_cm_user_trades",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn get_pm_margin_open_orders(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_margin_open_orders", Vec::new())
    }

    pub fn get_pm_margin_all_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_margin_all_orders",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn get_pm_margin_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_margin_trades",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn place_pm_cm_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
        quantity: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "place_pm_cm_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("side".into(), side.into()),
                ("type_".into(), order_type.into()),
                ("quantity".into(), quantity.into()),
            ],
        )
    }

    pub fn place_pm_margin_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
        quantity: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "place_pm_margin_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("side".into(), side.into()),
                ("type_".into(), order_type.into()),
                ("quantity".into(), quantity.into()),
            ],
        )
    }

    pub fn get_pm_cm_order(
        &self,
        product_symbol: &str,
        order_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_cm_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("orderId".into(), order_id.into()),
            ],
        )
    }

    pub fn cancel_pm_cm_order(
        &self,
        product_symbol: &str,
        order_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_pm_cm_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("orderId".into(), order_id.into()),
            ],
        )
    }

    pub fn get_pm_margin_order(
        &self,
        product_symbol: &str,
        order_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_margin_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("orderId".into(), order_id.into()),
            ],
        )
    }

    pub fn cancel_pm_margin_order(
        &self,
        product_symbol: &str,
        order_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_pm_margin_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("orderId".into(), order_id.into()),
            ],
        )
    }

    pub fn cancel_all_pm_cm_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_all_pm_cm_orders",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn cancel_all_pm_margin_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_all_pm_margin_orders",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn modify_pm_um_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_id: &str,
        quantity: &str,
        price: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "modify_pm_um_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("side".into(), side.into()),
                ("orderId".into(), order_id.into()),
                ("quantity".into(), quantity.into()),
                ("price".into(), price.into()),
            ],
        )
    }

    pub fn modify_pm_cm_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_id: &str,
        quantity: &str,
        price: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "modify_pm_cm_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("side".into(), side.into()),
                ("orderId".into(), order_id.into()),
                ("quantity".into(), quantity.into()),
                ("price".into(), price.into()),
            ],
        )
    }

    pub fn borrow_pm_margin(
        &self,
        asset: &str,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "borrow_pm_margin",
            vec![
                ("asset".into(), asset.into()),
                ("amount".into(), amount.into()),
            ],
        )
    }

    pub fn repay_pm_margin(
        &self,
        asset: &str,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "repay_pm_margin",
            vec![
                ("asset".into(), asset.into()),
                ("amount".into(), amount.into()),
            ],
        )
    }

    pub fn place_pm_cm_conditional_order(
        &self,
        product_symbol: &str,
        side: &str,
        strategy_type: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "place_pm_cm_conditional_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("side".into(), side.into()),
                ("strategyType".into(), strategy_type.into()),
            ],
        )
    }

    pub fn cancel_pm_cm_conditional_order(
        &self,
        product_symbol: &str,
        strategy_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_pm_cm_conditional_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("strategyId".into(), strategy_id.into()),
            ],
        )
    }

    pub fn cancel_all_pm_cm_conditional_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_all_pm_cm_conditional_orders",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn get_pm_cm_conditional_order(
        &self,
        product_symbol: &str,
        strategy_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_cm_conditional_order",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("strategyId".into(), strategy_id.into()),
            ],
        )
    }

    pub fn get_pm_cm_conditional_order_history(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_cm_conditional_order_history",
            vec![("product_symbol".into(), product_symbol.into())],
        )
    }

    pub fn get_pm_cm_open_conditional_orders(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_cm_open_conditional_orders", Vec::new())
    }

    pub fn get_pm_cm_all_conditional_orders(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_cm_all_conditional_orders", Vec::new())
    }

    pub fn place_pm_margin_oco(
        &self,
        product_symbol: &str,
        side: &str,
        quantity: &str,
        price: &str,
        stop_price: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "place_pm_margin_oco",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("side".into(), side.into()),
                ("quantity".into(), quantity.into()),
                ("price".into(), price.into()),
                ("stopPrice".into(), stop_price.into()),
            ],
        )
    }

    pub fn get_pm_margin_oco(
        &self,
        order_list_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_margin_oco",
            vec![("orderListId".into(), order_list_id.into())],
        )
    }

    pub fn cancel_pm_margin_oco(
        &self,
        product_symbol: &str,
        order_list_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "cancel_pm_margin_oco",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("orderListId".into(), order_list_id.into()),
            ],
        )
    }

    pub fn get_pm_margin_open_oco(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_margin_open_oco", Vec::new())
    }

    pub fn get_pm_margin_all_oco(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_margin_all_oco", Vec::new())
    }

    pub fn get_pm_balance(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_balance", Vec::new())
    }

    pub fn get_pm_cm_leverage_bracket(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_cm_leverage_bracket", Vec::new())
    }

    pub fn set_pm_um_leverage(
        &self,
        product_symbol: &str,
        leverage: u32,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "set_pm_um_leverage",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("leverage".into(), leverage.to_string()),
            ],
        )
    }

    pub fn set_pm_cm_leverage(
        &self,
        product_symbol: &str,
        leverage: u32,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "set_pm_cm_leverage",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("leverage".into(), leverage.to_string()),
            ],
        )
    }

    pub fn get_pm_um_position_mode(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_um_position_mode", Vec::new())
    }

    pub fn get_pm_cm_position_mode(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_cm_position_mode", Vec::new())
    }

    pub fn set_pm_um_position_mode(
        &self,
        dual_side_position: bool,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "set_pm_um_position_mode",
            vec![("dualSidePosition".into(), dual_side_position.to_string())],
        )
    }

    pub fn set_pm_cm_position_mode(
        &self,
        dual_side_position: bool,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "set_pm_cm_position_mode",
            vec![("dualSidePosition".into(), dual_side_position.to_string())],
        )
    }

    pub fn get_pm_um_adl_quantile(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("get_pm_um_adl_quantile", Vec::new())
    }

    pub fn repay_pm_margin_debt(
        &self,
        asset: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request("repay_pm_margin_debt", vec![("asset".into(), asset.into())])
    }

    pub fn get_pm_um_order_amendments(
        &self,
        product_symbol: &str,
        order_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_um_order_amendments",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("orderId".into(), order_id.into()),
            ],
        )
    }

    pub fn get_pm_cm_order_amendments(
        &self,
        product_symbol: &str,
        order_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.pm_request(
            "get_pm_cm_order_amendments",
            vec![
                ("product_symbol".into(), product_symbol.into()),
                ("orderId".into(), order_id.into()),
            ],
        )
    }

    pub(super) async fn portfolio_margin_private_request(
        &self,
        method_name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (method, path, mut query) = match method_name {
            "get_pm_account" => {
                params.ensure_allowed(&["recvWindow"])?;
                (HttpMethod::Get, PM_ACCOUNT, params.without(&[]))
            }
            "get_pm_um_account" => {
                params.ensure_allowed(&["recvWindow"])?;
                (HttpMethod::Get, PM_UM_ACCOUNT, params.without(&[]))
            }
            "get_pm_um_position_risk" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                (
                    HttpMethod::Get,
                    PM_UM_POSITION_RISK,
                    params.without(&["product_symbol"]),
                )
            }
            "get_pm_um_open_orders" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                (
                    HttpMethod::Get,
                    PM_UM_OPEN_ORDERS,
                    params.without(&["product_symbol"]),
                )
            }
            "get_pm_um_order" | "cancel_pm_um_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "orderId",
                    "origClientOrderId",
                    "recvWindow",
                ])?;
                require_one_order_id(params)?;
                let method = if method_name == "get_pm_um_order" {
                    HttpMethod::Get
                } else {
                    HttpMethod::Delete
                };
                (method, PM_UM_ORDER, params.without(&["product_symbol"]))
            }
            "cancel_all_pm_um_orders" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                (
                    HttpMethod::Delete,
                    PM_UM_ALL_OPEN_ORDERS,
                    params.without(&["product_symbol"]),
                )
            }
            "place_pm_um_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "side",
                    "type_",
                    "positionSide",
                    "timeInForce",
                    "quantity",
                    "price",
                    "reduceOnly",
                    "newClientOrderId",
                    "newOrderRespType",
                    "priceMatch",
                    "selfTradePreventionMode",
                    "goodTillDate",
                    "recvWindow",
                ])?;
                let side = params.required("side")?;
                if !matches!(side, "BUY" | "SELL") {
                    return Err(DcexError::InvalidInput(
                        "Binance PM side must be BUY or SELL".into(),
                    ));
                }
                let order_type = params.required("type_")?;
                if !matches!(order_type, "LIMIT" | "MARKET") {
                    return Err(DcexError::InvalidInput(
                        "Binance PM UM wrapper supports LIMIT and MARKET orders".into(),
                    ));
                }
                positive_decimal(params.required("quantity")?, "quantity")?;
                if order_type == "LIMIT" {
                    positive_decimal(params.required("price")?, "price")?;
                    params.required("timeInForce")?;
                }
                params.optional_bool("reduceOnly")?;
                let mut query = params.without(&["product_symbol", "type_"]);
                query.push(("type".into(), order_type.into()));
                (HttpMethod::Post, PM_UM_ORDER, query)
            }
            "place_pm_um_algo_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "side",
                    "type_",
                    "positionSide",
                    "timeInForce",
                    "quantity",
                    "price",
                    "triggerPrice",
                    "workingType",
                    "priceMatch",
                    "closePosition",
                    "priceProtect",
                    "reduceOnly",
                    "activatePrice",
                    "callbackRate",
                    "clientAlgoId",
                    "newOrderRespType",
                    "selfTradePreventionMode",
                    "goodTillDate",
                    "recvWindow",
                ])?;
                let side = params.required("side")?;
                if !matches!(side, "BUY" | "SELL") {
                    return Err(DcexError::InvalidInput(
                        "Binance PM algo side must be BUY or SELL".into(),
                    ));
                }
                let order_type = params.required("type_")?;
                if !matches!(
                    order_type,
                    "STOP"
                        | "TAKE_PROFIT"
                        | "STOP_MARKET"
                        | "TAKE_PROFIT_MARKET"
                        | "TRAILING_STOP_MARKET"
                ) {
                    return Err(DcexError::InvalidInput(
                        "unsupported Binance PM algo order type".into(),
                    ));
                }
                params.optional_bool("closePosition")?;
                let close_all = params.get("closePosition") == Some("true");
                params.optional_bool("reduceOnly")?;
                params.optional_bool("priceProtect")?;
                if close_all {
                    if !matches!(order_type, "STOP_MARKET" | "TAKE_PROFIT_MARKET")
                        || params.get("quantity").is_some()
                        || params.get("reduceOnly").is_some()
                    {
                        return Err(DcexError::InvalidInput(
                            "Binance PM closePosition=true requires a STOP_MARKET or TAKE_PROFIT_MARKET without quantity or reduceOnly".into()
                        ));
                    }
                } else {
                    positive_decimal(params.required("quantity")?, "quantity")?;
                }
                if order_type == "TRAILING_STOP_MARKET" {
                    let rate = params
                        .required("callbackRate")?
                        .parse::<f64>()
                        .map_err(|_| {
                            DcexError::InvalidInput("invalid Binance PM callbackRate".into())
                        })?;
                    if !(0.1..=10.0).contains(&rate) {
                        return Err(DcexError::InvalidInput(
                            "Binance PM callbackRate must be between 0.1 and 10".into(),
                        ));
                    }
                    if let Some(price) = params.get("activatePrice") {
                        positive_decimal(price, "activatePrice")?;
                    }
                } else {
                    positive_decimal(params.required("triggerPrice")?, "triggerPrice")?;
                }
                if matches!(order_type, "STOP" | "TAKE_PROFIT") {
                    positive_decimal(params.required("price")?, "price")?;
                }
                let mut query = params.without(&["product_symbol", "type_"]);
                query.push(("type".into(), order_type.into()));
                query.push(("algoType".into(), "CONDITIONAL".into()));
                (HttpMethod::Post, PM_UM_ALGO_ORDER, query)
            }
            "get_pm_um_algo_order" | "cancel_pm_um_algo_order" => {
                params.ensure_allowed(&["algoId", "clientAlgoId", "recvWindow"])?;
                require_one_algo_id(params)?;
                let method = if method_name == "get_pm_um_algo_order" {
                    HttpMethod::Get
                } else {
                    HttpMethod::Delete
                };
                let path = if method == HttpMethod::Get {
                    PM_UM_ALGO_DETAIL
                } else {
                    PM_UM_ALGO_ORDER
                };
                (method, path, params.without(&[]))
            }
            "cancel_all_pm_um_algo_orders" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                (
                    HttpMethod::Delete,
                    PM_UM_ALGO_CANCEL_ALL,
                    params.without(&["product_symbol"]),
                )
            }
            "get_pm_um_open_algo_orders" => {
                params.ensure_allowed(&["product_symbol", "algoId", "recvWindow"])?;
                let mut query = params.without(&["product_symbol"]);
                query.push(("algoType".into(), "CONDITIONAL".into()));
                (HttpMethod::Get, PM_UM_ALGO_OPEN, query)
            }
            "get_pm_um_algo_order_history" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "algoId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                (
                    HttpMethod::Get,
                    PM_UM_ALGO_HISTORY,
                    params.without(&["product_symbol"]),
                )
            }
            "get_pm_cm_account" => {
                params.ensure_allowed(&["recvWindow"])?;
                (HttpMethod::Get, PM_CM_ACCOUNT, params.without(&[]))
            }
            "get_pm_cm_position_risk" => {
                params.ensure_allowed(&["marginAsset", "pair", "recvWindow"])?;
                (HttpMethod::Get, PM_CM_POSITION_RISK, params.without(&[]))
            }
            "get_pm_um_account_config"
            | "get_pm_um_symbol_config"
            | "get_pm_um_leverage_bracket"
            | "get_pm_um_api_trading_status" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                let path = match method_name {
                    "get_pm_um_account_config" => PM_UM_ACCOUNT_CONFIG,
                    "get_pm_um_symbol_config" => PM_UM_SYMBOL_CONFIG,
                    "get_pm_um_leverage_bracket" => PM_UM_LEVERAGE_BRACKET,
                    _ => PM_UM_API_TRADING_STATUS,
                };
                (HttpMethod::Get, path, params.without(&["product_symbol"]))
            }
            "get_pm_cm_adl_quantile" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                (
                    HttpMethod::Get,
                    PM_CM_ADL_QUANTILE,
                    params.without(&["product_symbol"]),
                )
            }
            "get_pm_margin_max_borrowable" => {
                params.ensure_allowed(&["asset", "recvWindow"])?;
                params.required("asset")?;
                (
                    HttpMethod::Get,
                    PM_MARGIN_MAX_BORROWABLE,
                    params.without(&[]),
                )
            }
            "get_pm_um_force_orders" | "get_pm_cm_force_orders" | "get_pm_margin_force_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "autoCloseType",
                    "startTime",
                    "endTime",
                    "limit",
                    "current",
                    "size",
                    "recvWindow",
                ])?;
                let path = match method_name {
                    "get_pm_um_force_orders" => PM_UM_FORCE_ORDERS,
                    "get_pm_cm_force_orders" => PM_CM_FORCE_ORDERS,
                    _ => PM_MARGIN_FORCE_ORDERS,
                };
                (HttpMethod::Get, path, params.without(&["product_symbol"]))
            }
            "get_pm_um_all_orders" | "get_pm_cm_all_orders" | "get_pm_margin_all_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "pair",
                    "orderId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                let path = match method_name {
                    "get_pm_um_all_orders" => PM_UM_ALL_ORDERS,
                    "get_pm_cm_all_orders" => PM_CM_ALL_ORDERS,
                    _ => PM_MARGIN_ALL_ORDERS,
                };
                (HttpMethod::Get, path, params.without(&["product_symbol"]))
            }
            "get_pm_um_user_trades" | "get_pm_cm_user_trades" | "get_pm_margin_trades" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "pair",
                    "orderId",
                    "startTime",
                    "endTime",
                    "fromId",
                    "limit",
                    "recvWindow",
                ])?;
                let path = match method_name {
                    "get_pm_um_user_trades" => PM_UM_USER_TRADES,
                    "get_pm_cm_user_trades" => PM_CM_USER_TRADES,
                    _ => PM_MARGIN_MY_TRADES,
                };
                (HttpMethod::Get, path, params.without(&["product_symbol"]))
            }
            "get_pm_cm_open_orders" | "get_pm_margin_open_orders" => {
                params.ensure_allowed(&["product_symbol", "pair", "recvWindow"])?;
                let path = if method_name == "get_pm_cm_open_orders" {
                    PM_CM_OPEN_ORDERS
                } else {
                    PM_MARGIN_OPEN_ORDERS
                };
                (HttpMethod::Get, path, params.without(&["product_symbol"]))
            }
            "get_pm_cm_order"
            | "cancel_pm_cm_order"
            | "get_pm_margin_order"
            | "cancel_pm_margin_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "orderId",
                    "origClientOrderId",
                    "newClientOrderId",
                    "recvWindow",
                ])?;
                require_one_order_id(params)?;
                let method = if method_name.starts_with("get_") {
                    HttpMethod::Get
                } else {
                    HttpMethod::Delete
                };
                let path = if method_name.contains("_cm_") {
                    PM_CM_ORDER
                } else {
                    PM_MARGIN_ORDER
                };
                (method, path, params.without(&["product_symbol"]))
            }
            "cancel_all_pm_cm_orders" | "cancel_all_pm_margin_orders" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                let path = if method_name == "cancel_all_pm_cm_orders" {
                    PM_CM_ALL_OPEN_ORDERS
                } else {
                    PM_MARGIN_ALL_OPEN_ORDERS
                };
                (
                    HttpMethod::Delete,
                    path,
                    params.without(&["product_symbol"]),
                )
            }
            "place_pm_cm_order" | "place_pm_margin_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "side",
                    "type_",
                    "quantity",
                    "quoteOrderQty",
                    "positionSide",
                    "timeInForce",
                    "price",
                    "stopPrice",
                    "reduceOnly",
                    "priceMatch",
                    "newClientOrderId",
                    "newOrderRespType",
                    "sideEffectType",
                    "icebergQty",
                    "selfTradePreventionMode",
                    "autoRepayAtCancel",
                    "recvWindow",
                ])?;
                let side = params.required("side")?;
                if !matches!(side, "BUY" | "SELL") {
                    return Err(DcexError::InvalidInput(
                        "Binance PM side must be BUY or SELL".into(),
                    ));
                }
                let order_type = params.required("type_")?;
                if !matches!(order_type, "LIMIT" | "MARKET") {
                    return Err(DcexError::InvalidInput(
                        "Binance PM CM/Margin wrapper supports LIMIT and MARKET orders".into(),
                    ));
                }
                positive_decimal(params.required("quantity")?, "quantity")?;
                if order_type == "LIMIT" {
                    positive_decimal(params.required("price")?, "price")?;
                    params.required("timeInForce")?;
                }
                params.optional_bool("reduceOnly")?;
                params.optional_bool("autoRepayAtCancel")?;
                let path = if method_name == "place_pm_cm_order" {
                    PM_CM_ORDER
                } else {
                    PM_MARGIN_ORDER
                };
                let mut query = params.without(&["product_symbol", "type_"]);
                query.push(("type".into(), order_type.into()));
                (HttpMethod::Post, path, query)
            }
            "modify_pm_um_order" | "modify_pm_cm_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "side",
                    "orderId",
                    "origClientOrderId",
                    "quantity",
                    "price",
                    "priceMatch",
                    "modifyId",
                    "recvWindow",
                ])?;
                let side = params.required("side")?;
                if !matches!(side, "BUY" | "SELL") {
                    return Err(DcexError::InvalidInput(
                        "Binance PM side must be BUY or SELL".into(),
                    ));
                }
                require_one_order_id(params)?;
                positive_decimal(params.required("quantity")?, "quantity")?;
                positive_decimal(params.required("price")?, "price")?;
                if params.get("priceMatch").is_some() {
                    return Err(DcexError::InvalidInput(
                        "Binance PM price and priceMatch cannot be sent together".into(),
                    ));
                }
                let path = if method_name == "modify_pm_um_order" {
                    PM_UM_ORDER
                } else {
                    PM_CM_ORDER
                };
                (HttpMethod::Put, path, params.without(&["product_symbol"]))
            }
            "borrow_pm_margin" | "repay_pm_margin" => {
                params.ensure_allowed(&["asset", "amount", "recvWindow"])?;
                params.required("asset")?;
                positive_decimal(params.required("amount")?, "amount")?;
                let path = if method_name == "borrow_pm_margin" {
                    PM_MARGIN_LOAN
                } else {
                    PM_MARGIN_REPAY
                };
                (HttpMethod::Post, path, params.without(&[]))
            }
            "place_pm_cm_conditional_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "side",
                    "strategyType",
                    "positionSide",
                    "timeInForce",
                    "quantity",
                    "reduceOnly",
                    "price",
                    "workingType",
                    "priceProtect",
                    "newClientStrategyId",
                    "stopPrice",
                    "activationPrice",
                    "callbackRate",
                    "recvWindow",
                ])?;
                let side = params.required("side")?;
                if !matches!(side, "BUY" | "SELL") {
                    return Err(DcexError::InvalidInput(
                        "Binance PM side must be BUY or SELL".into(),
                    ));
                }
                let strategy_type = params.required("strategyType")?;
                if !matches!(
                    strategy_type,
                    "STOP"
                        | "STOP_MARKET"
                        | "TAKE_PROFIT"
                        | "TAKE_PROFIT_MARKET"
                        | "TRAILING_STOP_MARKET"
                ) {
                    return Err(DcexError::InvalidInput(
                        "unsupported Binance PM CM strategyType".into(),
                    ));
                }
                if strategy_type == "TRAILING_STOP_MARKET" {
                    let rate = params
                        .required("callbackRate")?
                        .parse::<f64>()
                        .map_err(|_| {
                            DcexError::InvalidInput("invalid Binance PM CM callbackRate".into())
                        })?;
                    if !(0.1..=5.0).contains(&rate) {
                        return Err(DcexError::InvalidInput(
                            "Binance PM CM callbackRate must be between 0.1 and 5".into(),
                        ));
                    }
                } else {
                    positive_decimal(params.required("stopPrice")?, "stopPrice")?;
                }
                if matches!(strategy_type, "STOP" | "TAKE_PROFIT") {
                    positive_decimal(params.required("price")?, "price")?;
                }
                if let Some(quantity) = params.get("quantity") {
                    positive_decimal(quantity, "quantity")?;
                }
                params.optional_bool("reduceOnly")?;
                params.optional_bool("priceProtect")?;
                (
                    HttpMethod::Post,
                    PM_CM_CONDITIONAL_ORDER,
                    params.without(&["product_symbol"]),
                )
            }
            "cancel_pm_cm_conditional_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "strategyId",
                    "newClientStrategyId",
                    "recvWindow",
                ])?;
                let count = ["strategyId", "newClientStrategyId"]
                    .iter()
                    .filter(|key| params.get(key).is_some())
                    .count();
                if count != 1 {
                    return Err(DcexError::InvalidInput(
                        "Binance PM CM requires exactly one strategy identifier".into(),
                    ));
                }
                params.optional_u64_range("strategyId", 1, u64::MAX)?;
                (
                    HttpMethod::Delete,
                    PM_CM_CONDITIONAL_ORDER,
                    params.without(&["product_symbol"]),
                )
            }
            "cancel_all_pm_cm_conditional_orders" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                (
                    HttpMethod::Delete,
                    PM_CM_CONDITIONAL_ALL_OPEN,
                    params.without(&["product_symbol"]),
                )
            }
            "get_pm_cm_conditional_order" | "get_pm_cm_conditional_order_history" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "strategyId",
                    "newClientStrategyId",
                    "recvWindow",
                ])?;
                if method_name == "get_pm_cm_conditional_order"
                    && params.get("strategyId").is_none()
                    && params.get("newClientStrategyId").is_none()
                {
                    return Err(DcexError::InvalidInput(
                        "Binance PM CM conditional order needs a strategy identifier".into(),
                    ));
                }
                params.optional_u64_range("strategyId", 1, u64::MAX)?;
                let path = if method_name == "get_pm_cm_conditional_order" {
                    PM_CM_CONDITIONAL_DETAIL
                } else {
                    PM_CM_CONDITIONAL_HISTORY
                };
                (HttpMethod::Get, path, params.without(&["product_symbol"]))
            }
            "get_pm_cm_open_conditional_orders" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                (
                    HttpMethod::Get,
                    PM_CM_CONDITIONAL_OPEN,
                    params.without(&["product_symbol"]),
                )
            }
            "get_pm_cm_all_conditional_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "strategyId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                params.optional_u64_range("strategyId", 1, u64::MAX)?;
                (
                    HttpMethod::Get,
                    PM_CM_CONDITIONAL_ALL_ORDERS,
                    params.without(&["product_symbol"]),
                )
            }
            "place_pm_margin_oco" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "side",
                    "quantity",
                    "price",
                    "stopPrice",
                    "stopLimitPrice",
                    "stopLimitTimeInForce",
                    "listClientOrderId",
                    "limitClientOrderId",
                    "stopClientOrderId",
                    "limitIcebergQty",
                    "stopIcebergQty",
                    "sideEffectType",
                    "newOrderRespType",
                    "recvWindow",
                ])?;
                let side = params.required("side")?;
                if !matches!(side, "BUY" | "SELL") {
                    return Err(DcexError::InvalidInput(
                        "Binance PM side must be BUY or SELL".into(),
                    ));
                }
                for key in ["quantity", "price", "stopPrice"] {
                    positive_decimal(params.required(key)?, key)?;
                }
                (
                    HttpMethod::Post,
                    PM_MARGIN_OCO,
                    params.without(&["product_symbol"]),
                )
            }
            "get_pm_margin_oco" | "cancel_pm_margin_oco" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "orderListId",
                    "listClientOrderId",
                    "recvWindow",
                ])?;
                if params.get("orderListId").is_none() && params.get("listClientOrderId").is_none()
                {
                    return Err(DcexError::InvalidInput(
                        "Binance PM OCO needs an order list identifier".into(),
                    ));
                }
                params.optional_u64_range("orderListId", 1, u64::MAX)?;
                let method = if method_name == "get_pm_margin_oco" {
                    HttpMethod::Get
                } else {
                    HttpMethod::Delete
                };
                (
                    method,
                    PM_MARGIN_ORDER_LIST,
                    params.without(&["product_symbol"]),
                )
            }
            "get_pm_margin_open_oco" | "get_pm_margin_all_oco" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "fromId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                let path = if method_name == "get_pm_margin_open_oco" {
                    PM_MARGIN_OPEN_ORDER_LIST
                } else {
                    PM_MARGIN_ALL_ORDER_LIST
                };
                (HttpMethod::Get, path, params.without(&["product_symbol"]))
            }
            "get_pm_balance" => {
                params.ensure_allowed(&["asset", "recvWindow"])?;
                (HttpMethod::Get, PM_BALANCE, params.without(&[]))
            }
            "get_pm_cm_leverage_bracket" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                (
                    HttpMethod::Get,
                    PM_CM_LEVERAGE_BRACKET,
                    params.without(&["product_symbol"]),
                )
            }
            "set_pm_um_leverage" | "set_pm_cm_leverage" => {
                params.ensure_allowed(&["product_symbol", "leverage", "recvWindow"])?;
                params.optional_u64_range("leverage", 1, 125)?;
                params.required("leverage")?;
                let path = if method_name == "set_pm_um_leverage" {
                    PM_UM_LEVERAGE
                } else {
                    PM_CM_LEVERAGE
                };
                (HttpMethod::Post, path, params.without(&["product_symbol"]))
            }
            "get_pm_um_position_mode"
            | "get_pm_cm_position_mode"
            | "set_pm_um_position_mode"
            | "set_pm_cm_position_mode" => {
                let set = method_name.starts_with("set_");
                if set {
                    params.ensure_allowed(&["dualSidePosition", "recvWindow"])?;
                    params.required("dualSidePosition")?;
                    params.optional_bool("dualSidePosition")?;
                } else {
                    params.ensure_allowed(&["recvWindow"])?;
                }
                let path = if method_name.contains("_um_") {
                    PM_UM_POSITION_MODE
                } else {
                    PM_CM_POSITION_MODE
                };
                (
                    if set {
                        HttpMethod::Post
                    } else {
                        HttpMethod::Get
                    },
                    path,
                    params.without(&[]),
                )
            }
            "get_pm_um_adl_quantile" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                (
                    HttpMethod::Get,
                    PM_UM_ADL_QUANTILE,
                    params.without(&["product_symbol"]),
                )
            }
            "repay_pm_margin_debt" => {
                params.ensure_allowed(&["asset", "amount", "specifyRepayAssets", "recvWindow"])?;
                params.required("asset")?;
                if let Some(amount) = params.get("amount") {
                    positive_decimal(amount, "amount")?;
                }
                (HttpMethod::Post, PM_MARGIN_REPAY_DEBT, params.without(&[]))
            }
            "get_pm_um_order_amendments" | "get_pm_cm_order_amendments" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "orderId",
                    "origClientOrderId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                require_one_order_id(params)?;
                let path = if method_name == "get_pm_um_order_amendments" {
                    PM_UM_ORDER_AMENDMENT
                } else {
                    PM_CM_ORDER_AMENDMENT
                };
                (HttpMethod::Get, path, params.without(&["product_symbol"]))
            }
            _ => return Ok(None),
        };
        if let Some(product_symbol) = params.get("product_symbol") {
            query.push((
                "symbol".into(),
                self.exchange_symbol_for(
                    product_symbol,
                    if path.contains("/cm/") {
                        BinanceMarket::CoinFutures
                    } else if path.contains("/margin/") {
                        BinanceMarket::Spot
                    } else {
                        BinanceMarket::Futures
                    },
                )?,
            ));
        } else if matches!(
            method_name,
            "get_pm_um_order"
                | "cancel_pm_um_order"
                | "cancel_all_pm_um_orders"
                | "place_pm_um_order"
                | "place_pm_um_algo_order"
                | "cancel_all_pm_um_algo_orders"
                | "get_pm_um_algo_order_history"
                | "get_pm_cm_adl_quantile"
                | "get_pm_um_all_orders"
                | "get_pm_um_user_trades"
                | "get_pm_cm_all_orders"
                | "get_pm_cm_user_trades"
                | "get_pm_margin_all_orders"
                | "get_pm_margin_trades"
                | "get_pm_cm_order"
                | "cancel_pm_cm_order"
                | "get_pm_margin_order"
                | "cancel_pm_margin_order"
                | "cancel_all_pm_cm_orders"
                | "cancel_all_pm_margin_orders"
                | "place_pm_cm_order"
                | "place_pm_margin_order"
                | "modify_pm_um_order"
                | "modify_pm_cm_order"
                | "place_pm_cm_conditional_order"
                | "cancel_pm_cm_conditional_order"
                | "cancel_all_pm_cm_conditional_orders"
                | "get_pm_cm_conditional_order"
                | "get_pm_cm_conditional_order_history"
                | "place_pm_margin_oco"
                | "cancel_pm_margin_oco"
                | "set_pm_um_leverage"
                | "set_pm_cm_leverage"
                | "get_pm_um_order_amendments"
                | "get_pm_cm_order_amendments"
        ) {
            return Err(DcexError::InvalidInput(
                "missing required parameter: product_symbol".into(),
            ));
        }
        params.optional_u64_range("recvWindow", 1, 60_000)?;
        Ok(Some(
            self.request(method, BinanceMarket::PortfolioMargin, path, query, true)
                .await?,
        ))
    }
}

fn require_one_order_id(params: &PublicParams) -> Result<()> {
    let supplied = ["orderId", "origClientOrderId"]
        .iter()
        .filter(|key| params.get(key).is_some())
        .count();
    if supplied != 1 {
        return Err(DcexError::InvalidInput(
            "Binance PM requires exactly one of orderId or origClientOrderId".into(),
        ));
    }
    params.optional_u64_range("orderId", 1, u64::MAX)?;
    Ok(())
}

fn positive_decimal(value: &str, key: &str) -> Result<()> {
    if value
        .parse::<f64>()
        .is_ok_and(|number| number.is_finite() && number > 0.0)
    {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(format!(
            "Binance PM {key} must be positive"
        )))
    }
}

fn require_one_algo_id(params: &PublicParams) -> Result<()> {
    if params.get("algoId").is_none() && params.get("clientAlgoId").is_none() {
        return Err(DcexError::InvalidInput(
            "Binance PM requires algoId or clientAlgoId".into(),
        ));
    }
    params.optional_u64_range("algoId", 1, u64::MAX)?;
    Ok(())
}
