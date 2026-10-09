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
mod official_fields;
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

mod order_lists;
mod schema_requests;

mod wrappers;

mod transfers;

mod withdrawals;
