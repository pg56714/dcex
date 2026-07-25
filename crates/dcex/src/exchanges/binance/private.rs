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
        let params = PublicParams(params);
        match method_name {
            "get_spot_fee_rates" => {
                self.get_spot_fee_rates(params.required("product_symbol")?)
                    .await
            }
            "get_futures_fee_rates" => {
                self.get_futures_fee_rates(params.required("product_symbol")?)
                    .await
            }
            "get_account_balance" => {
                self.get_account_balance(
                    params.get("market_type").unwrap_or("swap"),
                    params.get("omitZeroBalances"),
                )
                .await
            }
            "get_income_history" => {
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
            "get_futures_account_info" => self.get_futures_account_info().await,
            "get_wallet_balance" => {
                self.send_get_wallet_balance(BinanceWalletBalanceParams {
                    quote_asset: params.get("quoteAsset"),
                })
                .await
            }
            "get_funding_wallet" => {
                self.send_get_funding_wallet(BinanceFundingWalletParams {
                    asset: params.get("asset"),
                    need_btc_valuation: params.get("needBtcValuation"),
                })
                .await
            }
            "create_universal_transfer" => {
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
            "create_futures_listen_key" => self.create_futures_listen_key().await,
            "keep_alive_futures_listen_key" => {
                self.keep_alive_futures_listen_key(params.required("listenKey")?)
                    .await
            }
            "close_futures_listen_key" => {
                self.close_futures_listen_key(params.required("listenKey")?)
                    .await
            }
            "set_leverage" => {
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
                    params.required("type_")?,
                    params.without(&["product_symbol", "side", "type_"]),
                )
                .await
            }
            "test_order" => {
                self.send_test_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type_")?,
                    params.without(&["product_symbol", "side", "type_"]),
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
                    params.required("type_")?,
                    params.get("algoType").unwrap_or("CONDITIONAL"),
                    params.without(&["product_symbol", "side", "type_", "algoType"]),
                )
                .await
            }
            "cancel_futures_algo_order" => {
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
                self.send_get_all_open_futures_algo_orders(BinanceOpenFuturesAlgoOrdersParams {
                    product_symbol: params.get("product_symbol"),
                    algo_type: params.get("algoType"),
                    algo_id: params.get("algoId"),
                })
                .await
            }
            "get_all_futures_algo_orders" => {
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
                self.cancel_all_open_futures_algo_orders(params.required("product_symbol")?)
                    .await
            }
            "place_market_order" => {
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
                self.send_get_all_open_orders(BinanceAllOpenOrdersParams {
                    product_symbol: params.get("product_symbol"),
                    market_type: params.get("market_type"),
                })
                .await
            }
            "cancel_all_open_orders" => {
                self.cancel_all_open_orders(params.required("product_symbol")?)
                    .await
            }
            "get_future_all_order" => {
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
            query.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
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
