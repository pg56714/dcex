use super::client::BinanceClient;
use super::params::PublicParams;
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
                self.get_income_history(
                    params.get("product_symbol"),
                    params.get("incomeType"),
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("page")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_account_info" => self.get_futures_account_info().await,
            "get_wallet_balance" => self.get_wallet_balance(params.get("quoteAsset")).await,
            "get_funding_wallet" => {
                self.get_funding_wallet(params.get("asset"), params.get("needBtcValuation"))
                    .await
            }
            "create_universal_transfer" => {
                self.create_universal_transfer(
                    params.required("type")?,
                    params.required("asset")?,
                    params.required("amount")?,
                    params.get("fromSymbol"),
                    params.get("toSymbol"),
                )
                .await
            }
            "get_universal_transfer_history" => {
                self.get_universal_transfer_history(
                    params.required("type")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("current")?,
                    params.u64("size")?,
                    params.get("fromSymbol"),
                    params.get("toSymbol"),
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
                self.place_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type_")?,
                    params.without(&["product_symbol", "side", "type_"]),
                )
                .await
            }
            "test_order" => {
                self.test_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type_")?,
                    params.without(&["product_symbol", "side", "type_"]),
                )
                .await
            }
            "place_futures_algo_order" => {
                self.place_futures_algo_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("type_")?,
                    params.get("algoType").unwrap_or("CONDITIONAL"),
                    params.without(&["product_symbol", "side", "type_", "algoType"]),
                )
                .await
            }
            "cancel_futures_algo_order" => {
                self.cancel_futures_algo_order(params.get("algoId"), params.get("clientAlgoId"))
                    .await
            }
            "get_futures_algo_order" => {
                self.get_futures_algo_order(params.get("algoId"), params.get("clientAlgoId"))
                    .await
            }
            "get_all_open_futures_algo_orders" => {
                self.get_all_open_futures_algo_orders(
                    params.get("product_symbol"),
                    params.get("algoType"),
                    params.get("algoId"),
                )
                .await
            }
            "get_all_futures_algo_orders" => {
                self.get_all_futures_algo_orders(
                    params.required("product_symbol")?,
                    params.get("algoId"),
                    params.get("startTime"),
                    params.get("endTime"),
                    params.get("limit"),
                )
                .await
            }
            "cancel_all_open_futures_algo_orders" => {
                self.cancel_all_open_futures_algo_orders(params.required("product_symbol")?)
                    .await
            }
            "place_market_order" => {
                self.place_market_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("quantity")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                    params.get("newOrderRespType"),
                )
                .await
            }
            "place_market_buy_order" => {
                self.place_market_buy_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                    params.get("newOrderRespType"),
                )
                .await
            }
            "place_market_sell_order" => {
                self.place_market_sell_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                    params.get("newOrderRespType"),
                )
                .await
            }
            "place_limit_order" => {
                self.place_limit_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("timeInForce").unwrap_or("GTC"),
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "place_limit_buy_order" => {
                self.place_limit_buy_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("timeInForce").unwrap_or("GTC"),
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "place_limit_sell_order" => {
                self.place_limit_sell_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("timeInForce").unwrap_or("GTC"),
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "place_post_only_limit_order" => {
                self.place_post_only_limit_order(
                    params.required("product_symbol")?,
                    params.required("side")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "place_post_only_limit_buy_order" => {
                self.place_post_only_limit_buy_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "place_post_only_limit_sell_order" => {
                self.place_post_only_limit_sell_order(
                    params.required("product_symbol")?,
                    params.required("quantity")?,
                    params.required("price")?,
                    params.get("positionSide"),
                    params.get("reduceOnly"),
                )
                .await
            }
            "cancel_order" => {
                self.cancel_order(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("origClientOrderId"),
                )
                .await
            }
            "get_order" => {
                self.get_order(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("origClientOrderId"),
                )
                .await
            }
            "get_open_orders" => {
                self.get_open_orders(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("origClientOrderId"),
                )
                .await
            }
            "get_all_open_orders" => {
                self.get_all_open_orders(
                    params.get("product_symbol"),
                    params.get("market_type").unwrap_or("spot"),
                )
                .await
            }
            "cancel_all_open_orders" => {
                self.cancel_all_open_orders(params.required("product_symbol")?)
                    .await
            }
            "get_future_all_order" => {
                self.get_future_all_order(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("startTime"),
                    params.get("endTime"),
                    params.get("limit"),
                )
                .await
            }
            "get_all_orders" => {
                self.get_all_orders(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("startTime"),
                    params.get("endTime"),
                    params.get("limit"),
                )
                .await
            }
            "get_account_trades" => {
                self.get_account_trades(
                    params.required("product_symbol")?,
                    params.get("orderId"),
                    params.get("startTime"),
                    params.get("endTime"),
                    params.get("fromId"),
                    params.get("limit"),
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
