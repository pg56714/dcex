use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::{
    market_from_type, normalize_order_side, push_optional, BinanceAccountTradesParams,
    BinanceAlgoOrderLookupParams, BinanceAllFuturesAlgoOrdersParams, BinanceAllOpenOrdersParams,
    BinanceAllOrdersParams, BinanceLimitOrderParams, BinanceMarketOrderParams,
    BinanceOpenFuturesAlgoOrdersParams, BinanceOrderLookupParams, BinancePostOnlyOrderParams,
};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl BinanceClient {
    pub async fn set_leverage(
        &self,
        product_symbol: &str,
        leverage: &str,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Post,
            BinanceMarket::Futures,
            FUTURES_LEVERAGE,
            vec![
                ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
                ("leverage".to_string(), leverage.to_string()),
            ],
            true,
        )
        .await
    }

    pub async fn place_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
    ) -> Result<ValidatedResponse> {
        self.place_order_with(product_symbol, side, order_type, Vec::new())
            .await
    }

    pub async fn place_order_with(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
        extra_params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.order_request(
            HttpMethod::Post,
            product_symbol,
            false,
            side,
            order_type,
            extra_params,
        )
        .await
    }

    pub async fn test_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
    ) -> Result<ValidatedResponse> {
        self.test_order_with(product_symbol, side, order_type, Vec::new())
            .await
    }

    pub async fn test_order_with(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
        extra_params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.order_request(
            HttpMethod::Post,
            product_symbol,
            true,
            side,
            order_type,
            extra_params,
        )
        .await
    }

    pub async fn place_futures_algo_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
        algo_type: &str,
    ) -> Result<ValidatedResponse> {
        self.place_futures_algo_order_with(product_symbol, side, order_type, algo_type, Vec::new())
            .await
    }

    pub async fn place_futures_algo_order_with(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
        algo_type: &str,
        extra_params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("algoType".to_string(), algo_type.to_string()),
            ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
            ("side".to_string(), normalize_order_side(side)?),
            ("type".to_string(), order_type.to_string()),
        ];
        params.extend(extra_params);
        self.request(
            HttpMethod::Post,
            BinanceMarket::Futures,
            FUTURES_ALGO_ORDER,
            params,
            true,
        )
        .await
    }

    pub async fn cancel_futures_algo_order(
        &self,
        request: BinanceAlgoOrderLookupParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.futures_algo_order_request(HttpMethod::Delete, request)
            .await
    }

    pub async fn get_futures_algo_order(
        &self,
        request: BinanceAlgoOrderLookupParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.futures_algo_order_request(HttpMethod::Get, request)
            .await
    }

    pub async fn get_all_open_futures_algo_orders(&self) -> Result<ValidatedResponse> {
        self.get_all_open_futures_algo_orders_with(BinanceOpenFuturesAlgoOrdersParams::default())
            .await
    }

    pub async fn get_all_open_futures_algo_orders_with(
        &self,
        request: BinanceOpenFuturesAlgoOrdersParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        push_optional(&mut params, "algoType", request.algo_type);
        push_optional(&mut params, "algoId", request.algo_id);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_OPEN_ALGO_ORDERS,
            params,
            true,
        )
        .await
    }

    pub async fn get_all_futures_algo_orders(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.get_all_futures_algo_orders_with(
            product_symbol,
            BinanceAllFuturesAlgoOrdersParams::default(),
        )
        .await
    }

    pub async fn get_all_futures_algo_orders_with(
        &self,
        product_symbol: &str,
        request: BinanceAllFuturesAlgoOrdersParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional(&mut params, "algoId", request.algo_id);
        push_optional(&mut params, "startTime", request.start_time);
        push_optional(&mut params, "endTime", request.end_time);
        push_optional(&mut params, "limit", request.limit);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_ALL_ALGO_ORDERS,
            params,
            true,
        )
        .await
    }

    pub async fn cancel_all_open_futures_algo_orders(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Delete,
            BinanceMarket::Futures,
            FUTURES_CANCEL_ALL_OPEN_ALGO_ORDERS,
            vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)],
            true,
        )
        .await
    }

    pub async fn place_market_order(
        &self,
        product_symbol: &str,
        side: &str,
        quantity: &str,
    ) -> Result<ValidatedResponse> {
        self.place_market_order_with(
            product_symbol,
            side,
            quantity,
            BinanceMarketOrderParams::default(),
        )
        .await
    }

    pub async fn place_market_order_with(
        &self,
        product_symbol: &str,
        side: &str,
        quantity: &str,
        request: BinanceMarketOrderParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("quantity".to_string(), quantity.to_string())];
        push_optional(&mut params, "positionSide", request.position_side);
        push_optional(&mut params, "reduceOnly", request.reduce_only);
        push_optional(&mut params, "newOrderRespType", request.new_order_resp_type);
        self.place_order_with(product_symbol, side, "MARKET", params)
            .await
    }

    pub async fn place_market_buy_order(
        &self,
        product_symbol: &str,
        quantity: &str,
    ) -> Result<ValidatedResponse> {
        self.place_market_buy_order_with(
            product_symbol,
            quantity,
            BinanceMarketOrderParams::default(),
        )
        .await
    }

    pub async fn place_market_buy_order_with(
        &self,
        product_symbol: &str,
        quantity: &str,
        request: BinanceMarketOrderParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.place_market_order_with(product_symbol, "BUY", quantity, request)
            .await
    }

    pub async fn place_market_sell_order(
        &self,
        product_symbol: &str,
        quantity: &str,
    ) -> Result<ValidatedResponse> {
        self.place_market_sell_order_with(
            product_symbol,
            quantity,
            BinanceMarketOrderParams::default(),
        )
        .await
    }

    pub async fn place_market_sell_order_with(
        &self,
        product_symbol: &str,
        quantity: &str,
        request: BinanceMarketOrderParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.place_market_order_with(product_symbol, "SELL", quantity, request)
            .await
    }

    pub async fn place_limit_order(
        &self,
        product_symbol: &str,
        side: &str,
        quantity: &str,
        price: &str,
        time_in_force: &str,
    ) -> Result<ValidatedResponse> {
        self.place_limit_order_with(
            product_symbol,
            side,
            quantity,
            price,
            time_in_force,
            BinanceLimitOrderParams::default(),
        )
        .await
    }

    pub async fn place_limit_order_with(
        &self,
        product_symbol: &str,
        side: &str,
        quantity: &str,
        price: &str,
        time_in_force: &str,
        request: BinanceLimitOrderParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("quantity".to_string(), quantity.to_string()),
            ("price".to_string(), price.to_string()),
            ("timeInForce".to_string(), time_in_force.to_string()),
        ];
        push_optional(&mut params, "positionSide", request.position_side);
        push_optional(&mut params, "reduceOnly", request.reduce_only);
        self.place_order_with(product_symbol, side, "LIMIT", params)
            .await
    }

    pub async fn place_limit_buy_order(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
        time_in_force: &str,
    ) -> Result<ValidatedResponse> {
        self.place_limit_buy_order_with(
            product_symbol,
            quantity,
            price,
            time_in_force,
            BinanceLimitOrderParams::default(),
        )
        .await
    }

    pub async fn place_limit_buy_order_with(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
        time_in_force: &str,
        request: BinanceLimitOrderParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.place_limit_order_with(
            product_symbol,
            "BUY",
            quantity,
            price,
            time_in_force,
            request,
        )
        .await
    }

    pub async fn place_limit_sell_order(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
        time_in_force: &str,
    ) -> Result<ValidatedResponse> {
        self.place_limit_sell_order_with(
            product_symbol,
            quantity,
            price,
            time_in_force,
            BinanceLimitOrderParams::default(),
        )
        .await
    }

    pub async fn place_limit_sell_order_with(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
        time_in_force: &str,
        request: BinanceLimitOrderParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.place_limit_order_with(
            product_symbol,
            "SELL",
            quantity,
            price,
            time_in_force,
            request,
        )
        .await
    }

    pub async fn place_post_only_limit_order(
        &self,
        product_symbol: &str,
        side: &str,
        quantity: &str,
        price: &str,
    ) -> Result<ValidatedResponse> {
        self.place_post_only_limit_order_with(
            product_symbol,
            side,
            quantity,
            price,
            BinancePostOnlyOrderParams::default(),
        )
        .await
    }

    pub async fn place_post_only_limit_order_with(
        &self,
        product_symbol: &str,
        side: &str,
        quantity: &str,
        price: &str,
        request: BinancePostOnlyOrderParams<'_>,
    ) -> Result<ValidatedResponse> {
        if self.market_for_product_symbol(product_symbol)? == BinanceMarket::Spot {
            self.place_order_with(
                product_symbol,
                side,
                "LIMIT_MAKER",
                vec![
                    ("quantity".to_string(), quantity.to_string()),
                    ("price".to_string(), price.to_string()),
                ],
            )
            .await
        } else {
            self.place_limit_order_with(
                product_symbol,
                side,
                quantity,
                price,
                "GTX",
                BinanceLimitOrderParams {
                    position_side: request.position_side,
                    reduce_only: request.reduce_only,
                },
            )
            .await
        }
    }

    pub async fn place_post_only_limit_buy_order(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
    ) -> Result<ValidatedResponse> {
        self.place_post_only_limit_buy_order_with(
            product_symbol,
            quantity,
            price,
            BinancePostOnlyOrderParams::default(),
        )
        .await
    }

    pub async fn place_post_only_limit_buy_order_with(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
        request: BinancePostOnlyOrderParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.place_post_only_limit_order_with(product_symbol, "BUY", quantity, price, request)
            .await
    }

    pub async fn place_post_only_limit_sell_order(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
    ) -> Result<ValidatedResponse> {
        self.place_post_only_limit_sell_order_with(
            product_symbol,
            quantity,
            price,
            BinancePostOnlyOrderParams::default(),
        )
        .await
    }

    pub async fn place_post_only_limit_sell_order_with(
        &self,
        product_symbol: &str,
        quantity: &str,
        price: &str,
        request: BinancePostOnlyOrderParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.place_post_only_limit_order_with(product_symbol, "SELL", quantity, price, request)
            .await
    }

    pub async fn cancel_order(
        &self,
        product_symbol: &str,
        request: BinanceOrderLookupParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.order_lookup_request(HttpMethod::Delete, product_symbol, request)
            .await
    }

    pub async fn get_order(
        &self,
        product_symbol: &str,
        request: BinanceOrderLookupParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.order_lookup_request(HttpMethod::Get, product_symbol, request)
            .await
    }

    pub async fn get_open_orders(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_open_orders_with(product_symbol, BinanceOrderLookupParams::default())
            .await
    }

    pub async fn get_open_orders_with(
        &self,
        product_symbol: &str,
        request: BinanceOrderLookupParams<'_>,
    ) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        let path = if market == BinanceMarket::Spot {
            SPOT_OPEN_ORDERS
        } else if request.order_id.is_some() || request.orig_client_order_id.is_some() {
            push_optional(&mut params, "orderId", request.order_id);
            push_optional(
                &mut params,
                "origClientOrderId",
                request.orig_client_order_id,
            );
            FUTURES_OPEN_ORDER
        } else {
            FUTURES_OPEN_ORDERS
        };
        self.request(HttpMethod::Get, market, path, params, true)
            .await
    }

    pub async fn get_all_open_orders(&self) -> Result<ValidatedResponse> {
        self.get_all_open_orders_with(BinanceAllOpenOrdersParams::default())
            .await
    }

    pub async fn get_all_open_orders_with(
        &self,
        request: BinanceAllOpenOrdersParams<'_>,
    ) -> Result<ValidatedResponse> {
        let market = if let Some(product_symbol) = request.product_symbol {
            self.market_for_product_symbol(product_symbol)?
        } else {
            market_from_type(request.market_type.unwrap_or("spot"))
        };
        let path = if market == BinanceMarket::Spot {
            SPOT_OPEN_ORDERS
        } else {
            FUTURES_OPEN_ORDERS
        };
        let params = if let Some(product_symbol) = request.product_symbol {
            vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)]
        } else {
            Vec::new()
        };
        self.request(HttpMethod::Get, market, path, params, true)
            .await
    }

    pub async fn cancel_all_open_orders(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let path = if market == BinanceMarket::Spot {
            SPOT_OPEN_ORDERS
        } else {
            FUTURES_CANCEL_ALL_OPEN_ORDERS
        };
        self.request(
            HttpMethod::Delete,
            market,
            path,
            vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)],
            true,
        )
        .await
    }

    pub async fn get_future_all_order(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_future_all_order_with(product_symbol, BinanceAllOrdersParams::default())
            .await
    }

    pub async fn get_future_all_order_with(
        &self,
        product_symbol: &str,
        request: BinanceAllOrdersParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.get_all_orders_with(product_symbol, request).await
    }

    pub async fn get_all_orders(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_all_orders_with(product_symbol, BinanceAllOrdersParams::default())
            .await
    }

    pub async fn get_all_orders_with(
        &self,
        product_symbol: &str,
        request: BinanceAllOrdersParams<'_>,
    ) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let path = if market == BinanceMarket::Spot {
            SPOT_ALL_ORDERS
        } else {
            FUTURES_ALL_ORDERS
        };
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional(&mut params, "orderId", request.order_id);
        push_optional(&mut params, "startTime", request.start_time);
        push_optional(&mut params, "endTime", request.end_time);
        push_optional(&mut params, "limit", request.limit);
        self.request(HttpMethod::Get, market, path, params, true)
            .await
    }

    pub async fn get_account_trades(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_account_trades_with(product_symbol, BinanceAccountTradesParams::default())
            .await
    }

    pub async fn get_account_trades_with(
        &self,
        product_symbol: &str,
        request: BinanceAccountTradesParams<'_>,
    ) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let path = if market == BinanceMarket::Spot {
            SPOT_ACCOUNT_TRADES
        } else {
            FUTURES_ACCOUNT_TRADES
        };
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        if market == BinanceMarket::Spot {
            push_optional(&mut params, "orderId", request.order_id);
        }
        push_optional(&mut params, "startTime", request.start_time);
        push_optional(&mut params, "endTime", request.end_time);
        push_optional(&mut params, "fromId", request.from_id);
        push_optional(&mut params, "limit", request.limit);
        self.request(HttpMethod::Get, market, path, params, true)
            .await
    }

    pub async fn get_future_position(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_POSITION_INFO,
            vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)],
            true,
        )
        .await
    }

    pub(super) async fn order_request(
        &self,
        method: HttpMethod,
        product_symbol: &str,
        test: bool,
        side: &str,
        order_type: &str,
        extra_params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let path = match (market, test) {
            (BinanceMarket::Spot, false) => SPOT_ORDER,
            (BinanceMarket::Spot, true) => SPOT_TEST_ORDER,
            (BinanceMarket::Futures, false) => FUTURES_ORDER,
            (BinanceMarket::Futures, true) => FUTURES_TEST_ORDER,
        };
        let mut params = vec![
            ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
            ("side".to_string(), normalize_order_side(side)?),
            ("type".to_string(), order_type.to_string()),
        ];
        params.extend(extra_params);
        self.request(method, market, path, params, true).await
    }

    pub(super) async fn futures_algo_order_request(
        &self,
        method: HttpMethod,
        request: BinanceAlgoOrderLookupParams<'_>,
    ) -> Result<ValidatedResponse> {
        if request.algo_id.is_none() && request.client_algo_id.is_none() {
            return Err(DcexError::InvalidInput(
                "Either algoId or clientAlgoId is required.".to_string(),
            ));
        }
        let mut params = Vec::new();
        push_optional(&mut params, "algoId", request.algo_id);
        push_optional(&mut params, "clientAlgoId", request.client_algo_id);
        self.request(
            method,
            BinanceMarket::Futures,
            FUTURES_ALGO_ORDER,
            params,
            true,
        )
        .await
    }

    pub(super) async fn order_lookup_request(
        &self,
        method: HttpMethod,
        product_symbol: &str,
        request: BinanceOrderLookupParams<'_>,
    ) -> Result<ValidatedResponse> {
        let market = self.market_for_product_symbol(product_symbol)?;
        let path = if market == BinanceMarket::Spot {
            SPOT_ORDER
        } else {
            FUTURES_ORDER
        };
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional(&mut params, "orderId", request.order_id);
        push_optional(
            &mut params,
            "origClientOrderId",
            request.orig_client_order_id,
        );
        self.request(method, market, path, params, true).await
    }
}
