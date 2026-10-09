use super::client::BinanceClient;
use super::endpoints::*;
use super::params::{
    BinanceAccountTradesParams, BinanceAlgoOrderLookupParams, BinanceAllFuturesAlgoOrdersParams,
    BinanceAllOpenOrdersParams, BinanceAllOrdersParams, BinanceFundingWalletParams,
    BinanceIncomeHistoryParams, BinanceLimitOrderParams, BinanceMarketOrderParams,
    BinanceOpenFuturesAlgoOrdersParams, BinanceOrderLookupParams, BinancePostOnlyOrderParams,
    BinanceUniversalTransferHistoryParams, BinanceUniversalTransferParams,
    BinanceWalletBalanceParams, PublicParams,
};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl BinanceClient {
    pub fn create_oco_order(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "create_oco_order",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn create_oto_order(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "create_oto_order",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn create_otoco_order(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "create_otoco_order",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_prevented_matches(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_prevented_matches",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_allocations(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_allocations",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_order_rate_limit(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_order_rate_limit", Vec::new())
    }

    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        crate::exchanges::input_contracts::pairs("binance", method_name, &params)?;
        let params = PublicParams(params);
        if let Some(response) = self.catalog_request(method_name, &params, false).await? {
            return Ok(response);
        }
        if let Some(response) = self.field_schema_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.table_request(method_name, &params, false).await? {
            return Ok(response);
        }
        if let Some(result) = self.batch_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(response) = self
            .trading_controls_private_request(method_name, &params)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self
            .portfolio_margin_private_request(method_name, &params)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self
            .coin_futures_private_request(method_name, &params)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self.convert_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self
            .subaccount_private_request(method_name, &params)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self.staking_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.loan_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self
            .simple_earn_private_request(method_name, &params)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self.equity_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.options_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.margin_private_request(method_name, &params).await? {
            return Ok(response);
        }
        match method_name {
            "get_spot_fee_rates" => {
                params.ensure_allowed(&["product_symbol"])?;
                self.get_spot_fee_rates(params.required("product_symbol")?)
                    .await
            }
            "get_futures_fee_rates" => {
                params.ensure_allowed(&["product_symbol"])?;
                self.get_futures_fee_rates(params.required("product_symbol")?)
                    .await
            }
            "get_account_balance" => {
                params.ensure_allowed(&["market_type", "omitZeroBalances"])?;
                self.get_account_balance(
                    params.get("market_type").unwrap_or("swap"),
                    params.get("omitZeroBalances"),
                )
                .await
            }
            "get_income_history" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "incomeType",
                    "startTime",
                    "endTime",
                    "page",
                    "limit",
                ])?;
                self.send_get_income_history(BinanceIncomeHistoryParams {
                    product_symbol: params.get("product_symbol"),
                    income_type: params.get("incomeType"),
                    start_time: params.u64("startTime")?,
                    end_time: params.u64("endTime")?,
                    page: params.u64("page")?,
                    limit: params.u64("limit")?,
                })
                .await
            }
            "get_futures_account_info" => {
                params.ensure_allowed(&[])?;
                self.get_futures_account_info().await
            }
            "get_wallet_balance" => {
                params.ensure_allowed(&["quoteAsset"])?;
                self.send_get_wallet_balance(BinanceWalletBalanceParams {
                    quote_asset: params.get("quoteAsset"),
                })
                .await
            }
            "get_funding_wallet" => {
                params.ensure_allowed(&["asset", "needBtcValuation"])?;
                self.send_get_funding_wallet(BinanceFundingWalletParams {
                    asset: params.get("asset"),
                    need_btc_valuation: params.get("needBtcValuation"),
                })
                .await
            }
            "create_universal_transfer" => {
                params.ensure_allowed(&["type", "asset", "amount", "fromSymbol", "toSymbol"])?;
                self.send_create_universal_transfer(
                    params.required("type")?,
                    params.required("asset")?,
                    params.required("amount")?,
                    BinanceUniversalTransferParams {
                        from_symbol: params.get("fromSymbol"),
                        to_symbol: params.get("toSymbol"),
                    },
                )
                .await
            }
            "get_universal_transfer_history" => {
                params.ensure_allowed(&[
                    "type",
                    "startTime",
                    "endTime",
                    "current",
                    "size",
                    "fromSymbol",
                    "toSymbol",
                ])?;
                self.send_get_universal_transfer_history(
                    params.required("type")?,
                    BinanceUniversalTransferHistoryParams {
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                        current: params.u64("current")?,
                        size: params.u64("size")?,
                        from_symbol: params.get("fromSymbol"),
                        to_symbol: params.get("toSymbol"),
                    },
                )
                .await
            }
            "create_futures_listen_key" => {
                params.ensure_allowed(&[])?;
                self.create_futures_listen_key().await
            }
            // A caller-supplied `listenKey` is ignored: these endpoints take no parameters.
            "keep_alive_futures_listen_key" => {
                params.ensure_allowed(&["listenKey"])?;
                self.keep_alive_futures_listen_key().await
            }
            "close_futures_listen_key" => {
                params.ensure_allowed(&["listenKey"])?;
                self.close_futures_listen_key().await
            }
            "set_leverage" => {
                params.ensure_allowed(&["product_symbol", "leverage"])?;
                self.set_leverage(
                    params.required("product_symbol")?,
                    params.required("leverage")?,
                )
                .await
            }
            "place_order" => {
                self.send_place_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type")?,
                    params.without(&["product_symbol", "side", "type"]),
                )
                .await
            }
            "test_order" => {
                self.send_test_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type")?,
                    params.without(&["product_symbol", "side", "type"]),
                )
                .await
            }
            "create_oco_order" => {
                self.spot_signed_request(HttpMethod::Post, SPOT_ORDER_LIST_OCO, params, true)
                    .await
            }
            "create_oto_order" => {
                self.spot_signed_request(HttpMethod::Post, SPOT_ORDER_LIST_OTO, params, true)
                    .await
            }
            "create_otoco_order" => {
                self.spot_signed_request(HttpMethod::Post, SPOT_ORDER_LIST_OTOCO, params, true)
                    .await
            }
            "get_prevented_matches" => {
                // Checked after the symbol so a missing symbol is reported first.
                if params.get("product_symbol").is_some()
                    && params.get("orderId").is_some() == params.get("preventedMatchId").is_some()
                {
                    return Err(crate::DcexError::InvalidInput(
                        "Binance: exactly one of orderId and preventedMatchId is required"
                            .to_string(),
                    ));
                }
                self.spot_signed_request(HttpMethod::Get, SPOT_PREVENTED_MATCHES, params, true)
                    .await
            }
            "get_allocations" => {
                self.spot_signed_request(HttpMethod::Get, SPOT_ALLOCATIONS, params, true)
                    .await
            }
            "get_order_rate_limit" => {
                self.spot_signed_request(HttpMethod::Get, SPOT_ORDER_RATE_LIMIT, params, false)
                    .await
            }
            "place_futures_algo_order" => {
                self.send_place_futures_algo_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type")?,
                    params.get("algoType").unwrap_or("CONDITIONAL"),
                    params.without(&["product_symbol", "side", "type", "algoType"]),
                )
                .await
            }
            "cancel_futures_algo_order" => {
                params.ensure_allowed(&["algoId", "clientAlgoId"])?;
                self.futures_algo_order_request(
                    crate::http::HttpMethod::Delete,
                    BinanceAlgoOrderLookupParams {
                        algo_id: params.get("algoId"),
                        client_algo_id: params.get("clientAlgoId"),
                    },
                )
                .await
            }
            "get_futures_algo_order" => {
                params.ensure_allowed(&["algoId", "clientAlgoId"])?;
                self.futures_algo_order_request(
                    crate::http::HttpMethod::Get,
                    BinanceAlgoOrderLookupParams {
                        algo_id: params.get("algoId"),
                        client_algo_id: params.get("clientAlgoId"),
                    },
                )
                .await
            }
            "get_all_open_futures_algo_orders" => {
                params.ensure_allowed(&["product_symbol", "algoType", "algoId"])?;
                self.send_get_all_open_futures_algo_orders(BinanceOpenFuturesAlgoOrdersParams {
                    product_symbol: params.get("product_symbol"),
                    algo_type: params.get("algoType"),
                    algo_id: params.get("algoId"),
                })
                .await
            }
            "get_all_futures_algo_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "algoId",
                    "startTime",
                    "endTime",
                    "limit",
                ])?;
                self.send_get_all_futures_algo_orders(
                    params.required("product_symbol")?,
                    BinanceAllFuturesAlgoOrdersParams {
                        algo_id: params.get("algoId"),
                        start_time: params.get("startTime"),
                        end_time: params.get("endTime"),
                        limit: params.get("limit"),
                    },
                )
                .await
            }
            "cancel_all_open_futures_algo_orders" => {
                params.ensure_allowed(&["product_symbol"])?;
                self.cancel_all_open_futures_algo_orders(params.required("product_symbol")?)
                    .await
            }
            "place_market_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "side",
                    "quantity",
                    "positionSide",
                    "reduceOnly",
                    "newOrderRespType",
                ])?;
                self.send_place_market_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("quantity")?,
                    BinanceMarketOrderParams {
                        position_side: params.get("positionSide"),
                        reduce_only: params.get("reduceOnly"),
                        new_order_resp_type: params.get("newOrderRespType"),
                    },
                )
                .await
            }
            "place_market_buy_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "quantity",
                    "positionSide",
                    "reduceOnly",
                    "newOrderRespType",
                ])?;
                self.send_place_market_buy_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    BinanceMarketOrderParams {
                        position_side: params.get("positionSide"),
                        reduce_only: params.get("reduceOnly"),
                        new_order_resp_type: params.get("newOrderRespType"),
                    },
                )
                .await
            }
            "place_market_sell_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "quantity",
                    "positionSide",
                    "reduceOnly",
                    "newOrderRespType",
                ])?;
                self.send_place_market_sell_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    BinanceMarketOrderParams {
                        position_side: params.get("positionSide"),
                        reduce_only: params.get("reduceOnly"),
                        new_order_resp_type: params.get("newOrderRespType"),
                    },
                )
                .await
            }
            "place_limit_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "side",
                    "quantity",
                    "price",
                    "timeInForce",
                    "positionSide",
                    "reduceOnly",
                ])?;
                self.send_place_limit_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("timeInForce").unwrap_or("GTC"),
                    BinanceLimitOrderParams {
                        position_side: params.get("positionSide"),
                        reduce_only: params.get("reduceOnly"),
                    },
                )
                .await
            }
            "place_limit_buy_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "quantity",
                    "price",
                    "timeInForce",
                    "positionSide",
                    "reduceOnly",
                ])?;
                self.send_place_limit_buy_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("timeInForce").unwrap_or("GTC"),
                    BinanceLimitOrderParams {
                        position_side: params.get("positionSide"),
                        reduce_only: params.get("reduceOnly"),
                    },
                )
                .await
            }
            "place_limit_sell_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "quantity",
                    "price",
                    "timeInForce",
                    "positionSide",
                    "reduceOnly",
                ])?;
                self.send_place_limit_sell_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("timeInForce").unwrap_or("GTC"),
                    BinanceLimitOrderParams {
                        position_side: params.get("positionSide"),
                        reduce_only: params.get("reduceOnly"),
                    },
                )
                .await
            }
            "place_post_only_limit_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "side",
                    "quantity",
                    "price",
                    "positionSide",
                    "reduceOnly",
                ])?;
                self.send_place_post_only_limit_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    BinancePostOnlyOrderParams {
                        position_side: params.get("positionSide"),
                        reduce_only: params.get("reduceOnly"),
                    },
                )
                .await
            }
            "place_post_only_limit_buy_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "quantity",
                    "price",
                    "positionSide",
                    "reduceOnly",
                ])?;
                self.send_place_post_only_limit_buy_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    BinancePostOnlyOrderParams {
                        position_side: params.get("positionSide"),
                        reduce_only: params.get("reduceOnly"),
                    },
                )
                .await
            }
            "place_post_only_limit_sell_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "quantity",
                    "price",
                    "positionSide",
                    "reduceOnly",
                ])?;
                self.send_place_post_only_limit_sell_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    BinancePostOnlyOrderParams {
                        position_side: params.get("positionSide"),
                        reduce_only: params.get("reduceOnly"),
                    },
                )
                .await
            }
            "cancel_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "orderId",
                    "origClientOrderId",
                    "newClientOrderId",
                    "cancelRestrictions",
                ])?;
                self.order_lookup_request(
                    crate::http::HttpMethod::Delete,
                    params.required("product_symbol")?,
                    BinanceOrderLookupParams {
                        order_id: params.get("orderId"),
                        orig_client_order_id: params.get("origClientOrderId"),
                        new_client_order_id: params.get("newClientOrderId"),
                        cancel_restrictions: params.get("cancelRestrictions"),
                    },
                )
                .await
            }
            "get_order" => {
                params.ensure_allowed(&["product_symbol", "orderId", "origClientOrderId"])?;
                self.order_lookup_request(
                    crate::http::HttpMethod::Get,
                    params.required("product_symbol")?,
                    BinanceOrderLookupParams {
                        order_id: params.get("orderId"),
                        orig_client_order_id: params.get("origClientOrderId"),
                        new_client_order_id: None,
                        cancel_restrictions: None,
                    },
                )
                .await
            }
            "get_open_orders" => {
                params.ensure_allowed(&["product_symbol", "orderId", "origClientOrderId"])?;
                self.send_get_open_orders(
                    params.required("product_symbol")?,
                    BinanceOrderLookupParams {
                        order_id: params.get("orderId"),
                        orig_client_order_id: params.get("origClientOrderId"),
                        new_client_order_id: None,
                        cancel_restrictions: None,
                    },
                )
                .await
            }
            "get_all_open_orders" => {
                params.ensure_allowed(&["product_symbol", "market_type"])?;
                self.send_get_all_open_orders(BinanceAllOpenOrdersParams {
                    product_symbol: params.get("product_symbol"),
                    market_type: params.get("market_type"),
                })
                .await
            }
            "cancel_all_open_orders" => {
                params.ensure_allowed(&["product_symbol"])?;
                self.cancel_all_open_orders(params.required("product_symbol")?)
                    .await
            }
            "get_future_all_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "limit",
                ])?;
                self.send_get_future_all_order(
                    params.required("product_symbol")?,
                    BinanceAllOrdersParams {
                        order_id: params.get("orderId"),
                        start_time: params.get("startTime"),
                        end_time: params.get("endTime"),
                        limit: params.get("limit"),
                    },
                )
                .await
            }
            "get_all_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "limit",
                ])?;
                self.send_get_all_orders(
                    params.required("product_symbol")?,
                    BinanceAllOrdersParams {
                        order_id: params.get("orderId"),
                        start_time: params.get("startTime"),
                        end_time: params.get("endTime"),
                        limit: params.get("limit"),
                    },
                )
                .await
            }
            "get_account_trades" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "fromId",
                    "limit",
                ])?;
                self.send_get_account_trades(
                    params.required("product_symbol")?,
                    BinanceAccountTradesParams {
                        order_id: params.get("orderId"),
                        start_time: params.get("startTime"),
                        end_time: params.get("endTime"),
                        from_id: params.get("fromId"),
                        limit: params.get("limit"),
                    },
                )
                .await
            }
            "get_future_position" => {
                params.ensure_allowed(&["product_symbol"])?;
                self.send_get_future_position(params.get("product_symbol"))
                    .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Binance private method: {method_name}"
            ))),
        }
    }

    async fn spot_signed_request(
        &self,
        method: HttpMethod,
        path: &str,
        params: PublicParams,
        require_symbol: bool,
    ) -> Result<ValidatedResponse> {
        let product_symbol = params.get("product_symbol");
        if require_symbol && product_symbol.is_none() {
            return Err(DcexError::InvalidInput(
                "Binance product_symbol is required.".to_string(),
            ));
        }

        let mut query = params.without(&["product_symbol"]);
        if let Some(product_symbol) = product_symbol {
            query.push((
                "symbol".to_string(),
                self.exchange_symbol_for(product_symbol, super::client::BinanceMarket::Spot)?,
            ));
        }
        self.request(
            method,
            super::client::BinanceMarket::Spot,
            path,
            query,
            true,
        )
        .await
    }
}

impl crate::exchanges::ExchangeMethodRequestClient for BinanceClient {
    fn input_exchange(&self) -> &'static str {
        Self::INPUT_EXCHANGE
    }
    fn public_request_boxed<'a>(
        &'a self,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> crate::exchanges::ExchangeMethodFuture<'a> {
        Box::pin(async move { self.public_request(method_name, params).await })
    }

    fn private_request_boxed<'a>(
        &'a self,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> crate::exchanges::ExchangeMethodFuture<'a> {
        Box::pin(async move { self.private_request(method_name, params).await })
    }
}
