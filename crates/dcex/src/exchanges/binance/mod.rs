mod account;
mod batch;
mod client;
mod coin_futures;
mod convert;
mod earn;
mod endpoints;
mod equity;

mod generated;
mod loan;
mod margin;
mod market;
mod options;
mod params;
mod portfolio_margin;
mod private;
mod signing;
mod staking;
mod stream;
mod subaccount;
mod trade;
mod trading_controls;
pub mod websocket;

#[cfg(test)]
mod tests;

pub use client::{BinanceClient, BinanceMarket};
pub use params::{
    BinanceAccountTradesParams, BinanceAlgoOrderLookupParams, BinanceAllFuturesAlgoOrdersParams,
    BinanceAllOpenOrdersParams, BinanceAllOrdersParams, BinanceFundingRateParams,
    BinanceFundingWalletParams, BinanceFuturesBasisParams, BinanceFuturesPeriodParams,
    BinanceIncomeHistoryParams, BinanceKlinesParams, BinanceLimitOrderParams, BinanceLimitParams,
    BinanceMarketOrderParams, BinanceOpenFuturesAlgoOrdersParams, BinanceOptionalSymbolParams,
    BinanceOrderLookupParams, BinancePostOnlyOrderParams, BinanceSymbolListParams,
    BinanceUniversalTransferHistoryParams, BinanceUniversalTransferParams,
    BinanceWalletBalanceParams,
};

impl crate::exchanges::ExchangeMethodRequestClient for BinanceClient {
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

mod order_lists;
mod schema_requests;

mod wrappers;

mod transfers;
