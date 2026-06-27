use super::client::BinanceClient;
use super::params::{
    BinanceAccountTradesParams, BinanceAlgoOrderLookupParams, BinanceAllFuturesAlgoOrdersParams,
    BinanceAllOpenOrdersParams, BinanceAllOrdersParams, BinanceFundingWalletParams,
    BinanceIncomeHistoryParams, BinanceLimitOrderParams, BinanceMarketOrderParams,
    BinanceOpenFuturesAlgoOrdersParams, BinanceOrderLookupParams, BinancePostOnlyOrderParams,
    BinanceUniversalTransferHistoryParams, BinanceUniversalTransferParams,
    BinanceWalletBalanceParams, PublicParams,
};
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

impl BinanceClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = PublicParams(params);
        match method_name {
            "get_account_balance" => {
                self.get_account_balance(params.get("market_type").unwrap_or("swap"))
                    .await
            }
            "get_income_history" => {
                self.get_income_history_with(BinanceIncomeHistoryParams {
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
                self.get_wallet_balance_with(BinanceWalletBalanceParams {
                    quote_asset: params.get("quoteAsset"),
                })
                .await
            }
            "get_funding_wallet" => {
                self.get_funding_wallet_with(BinanceFundingWalletParams {
                    asset: params.get("asset"),
                    need_btc_valuation: params.get("needBtcValuation"),
                })
                .await
            }
            "create_universal_transfer" => {
                self.create_universal_transfer_with(
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
                self.get_universal_transfer_history_with(
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
                self.place_order_with(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type_")?,
                    params.without(&["product_symbol", "side", "type_"]),
                )
                .await
            }
            "test_order" => {
                self.test_order_with(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type_")?,
                    params.without(&["product_symbol", "side", "type_"]),
                )
                .await
            }
            "place_futures_algo_order" => {
                self.place_futures_algo_order_with(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type_")?,
                    params.get("algoType").unwrap_or("CONDITIONAL"),
                    params.without(&["product_symbol", "side", "type_", "algoType"]),
                )
                .await
            }
            "cancel_futures_algo_order" => {
                self.cancel_futures_algo_order(BinanceAlgoOrderLookupParams {
                    algo_id: params.get("algoId"),
                    client_algo_id: params.get("clientAlgoId"),
                })
                .await
            }
            "get_futures_algo_order" => {
                self.get_futures_algo_order(BinanceAlgoOrderLookupParams {
                    algo_id: params.get("algoId"),
                    client_algo_id: params.get("clientAlgoId"),
                })
                .await
            }
            "get_all_open_futures_algo_orders" => {
                self.get_all_open_futures_algo_orders_with(BinanceOpenFuturesAlgoOrdersParams {
                    product_symbol: params.get("product_symbol"),
                    algo_type: params.get("algoType"),
                    algo_id: params.get("algoId"),
                })
                .await
            }
            "get_all_futures_algo_orders" => {
                self.get_all_futures_algo_orders_with(
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
                self.place_market_order_with(
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
                self.place_market_buy_order_with(
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
                self.place_market_sell_order_with(
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
                self.place_limit_order_with(
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
                self.place_limit_buy_order_with(
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
                self.place_limit_sell_order_with(
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
                self.place_post_only_limit_order_with(
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
                self.place_post_only_limit_buy_order_with(
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
                self.place_post_only_limit_sell_order_with(
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
                self.cancel_order(
                    params.required("product_symbol")?,
                    BinanceOrderLookupParams {
                        order_id: params.get("orderId"),
                        orig_client_order_id: params.get("origClientOrderId"),
                    },
                )
                .await
            }
            "get_order" => {
                self.get_order(
                    params.required("product_symbol")?,
                    BinanceOrderLookupParams {
                        order_id: params.get("orderId"),
                        orig_client_order_id: params.get("origClientOrderId"),
                    },
                )
                .await
            }
            "get_open_orders" => {
                self.get_open_orders_with(
                    params.required("product_symbol")?,
                    BinanceOrderLookupParams {
                        order_id: params.get("orderId"),
                        orig_client_order_id: params.get("origClientOrderId"),
                    },
                )
                .await
            }
            "get_all_open_orders" => {
                self.get_all_open_orders_with(BinanceAllOpenOrdersParams {
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
                self.get_future_all_order_with(
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
                self.get_all_orders_with(
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
                self.get_account_trades_with(
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
                self.get_future_position(params.required("product_symbol")?)
                    .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Binance private method: {method_name}"
            ))),
        }
    }
}
