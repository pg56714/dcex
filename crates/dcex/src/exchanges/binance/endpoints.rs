pub(super) const SPOT_BASE_URL: &str = "https://api.binance.com";
pub(super) const FUTURES_BASE_URL: &str = "https://fapi.binance.com";
pub(super) const COIN_FUTURES_BASE_URL: &str = "https://dapi.binance.com";
pub(super) const COIN_FUTURES_SERVER_TIME: &str = "/dapi/v1/time";
pub(super) const OPTIONS_BASE_URL: &str = "https://eapi.binance.com";
pub(super) const SPOT_SERVER_TIME: &str = "/api/v3/time";
pub(super) const SPOT_EXCHANGE_INFO: &str = "/api/v3/exchangeInfo";
pub(super) const SPOT_ORDERBOOK: &str = "/api/v3/depth";
pub(super) const SPOT_TRADES: &str = "/api/v3/trades";
pub(super) const SPOT_KLINES: &str = "/api/v3/klines";
pub(super) const SPOT_PRICE: &str = "/api/v3/ticker/price";
pub(super) const MARGIN_ALL_ASSETS: &str = "/sapi/v1/margin/allAssets";
pub(super) const MARGIN_ALL_PAIRS: &str = "/sapi/v1/margin/allPairs";
pub(super) const MARGIN_ALL_ISOLATED_SYMBOLS: &str = "/sapi/v1/margin/isolated/allPairs";
pub(super) const MARGIN_PRICE_INDEX: &str = "/sapi/v1/margin/priceIndex";
pub(super) const MARGIN_CROSS_ACCOUNT: &str = "/sapi/v1/margin/account";
pub(super) const MARGIN_ISOLATED_ACCOUNT: &str = "/sapi/v1/margin/isolated/account";
pub(super) const MARGIN_BORROW_REPAY: &str = "/sapi/v1/margin/borrow-repay";
pub(super) const MARGIN_INTEREST_HISTORY: &str = "/sapi/v1/margin/interestHistory";
pub(super) const MARGIN_MAX_BORROWABLE: &str = "/sapi/v1/margin/maxBorrowable";
pub(super) const MARGIN_MAX_TRANSFERABLE: &str = "/sapi/v1/margin/maxTransferable";
pub(super) const MARGIN_ORDER: &str = "/sapi/v1/margin/order";
pub(super) const MARGIN_OPEN_ORDERS: &str = "/sapi/v1/margin/openOrders";
pub(super) const MARGIN_ALL_ORDERS: &str = "/sapi/v1/margin/allOrders";
pub(super) const MARGIN_ACCOUNT_TRADES: &str = "/sapi/v1/margin/myTrades";
pub(super) const FUTURES_SERVER_TIME: &str = "/fapi/v1/time";
pub(super) const OPTIONS_SERVER_TIME: &str = "/eapi/v1/time";
pub(super) const OPTIONS_EXCHANGE_INFO: &str = "/eapi/v1/exchangeInfo";
pub(super) const OPTIONS_EXERCISE_HISTORY: &str = "/eapi/v1/exerciseHistory";
pub(super) const OPTIONS_INDEX_PRICE: &str = "/eapi/v1/index";
pub(super) const OPTIONS_KLINES: &str = "/eapi/v1/klines";
pub(super) const OPTIONS_OPEN_INTEREST: &str = "/eapi/v1/openInterest";
pub(super) const OPTIONS_MARK_PRICE: &str = "/eapi/v1/mark";
pub(super) const OPTIONS_ORDERBOOK: &str = "/eapi/v1/depth";
pub(super) const OPTIONS_BLOCK_TRADES: &str = "/eapi/v1/blockTrades";
pub(super) const OPTIONS_TRADES: &str = "/eapi/v1/trades";
pub(super) const OPTIONS_PING: &str = "/eapi/v1/ping";
pub(super) const OPTIONS_TICKER: &str = "/eapi/v1/ticker";
pub(super) const OPTIONS_ACCOUNT_BILL: &str = "/eapi/v1/bill";
pub(super) const OPTIONS_MARGIN_ACCOUNT: &str = "/eapi/v1/marginAccount";
pub(super) const OPTIONS_USER_TRADES: &str = "/eapi/v1/userTrades";
pub(super) const OPTIONS_ALL_OPEN_ORDERS_BY_UNDERLYING: &str = "/eapi/v1/allOpenOrdersByUnderlying";
pub(super) const OPTIONS_ALL_OPEN_ORDERS: &str = "/eapi/v1/allOpenOrders";
pub(super) const OPTIONS_BATCH_ORDERS: &str = "/eapi/v1/batchOrders";
pub(super) const OPTIONS_ORDER: &str = "/eapi/v1/order";
pub(super) const OPTIONS_POSITION: &str = "/eapi/v1/position";
pub(super) const OPTIONS_OPEN_ORDERS: &str = "/eapi/v1/openOrders";
pub(super) const OPTIONS_HISTORY_ORDERS: &str = "/eapi/v1/historyOrders";
pub(super) const OPTIONS_COMMISSION: &str = "/eapi/v1/commission";
pub(super) const OPTIONS_EXERCISE_RECORD: &str = "/eapi/v1/exerciseRecord";
pub(super) const OPTIONS_USER_DATA_STREAM: &str = "/eapi/v1/listenKey";
pub(super) const EQUITY_EXCHANGE_INFO: &str = "/sapi/v1/equity/market/exchangeInfo";
pub(super) const EQUITY_TOKENIZED_ASSETS: &str = "/sapi/v1/equity/market/tokenized-assets";
pub(super) const EQUITY_QUOTE: &str = "/sapi/v1/equity/market/quote";
pub(super) const EQUITY_ORDER_PLACE: &str = "/sapi/v1/equity/order/place";
pub(super) const EQUITY_ORDER_CANCEL: &str = "/sapi/v1/equity/order/cancel";
pub(super) const EQUITY_ORDER_CANCEL_ALL: &str = "/sapi/v1/equity/order/cancel-all";
pub(super) const EQUITY_OPEN_ORDERS: &str = "/sapi/v1/equity/order/open-orders";
pub(super) const EQUITY_ORDER_HISTORY: &str = "/sapi/v1/equity/order/history";
pub(super) const EQUITY_ORDER_DETAIL: &str = "/sapi/v1/equity/order/detail";
pub(super) const EQUITY_TRADE_HISTORY: &str = "/sapi/v1/equity/trade/history";
pub(super) const EQUITY_TOKENIZED_MINT: &str = "/sapi/v1/equity/tokenized/mint";
pub(super) const EQUITY_TOKENIZED_REDEEM: &str = "/sapi/v1/equity/tokenized/redeem";
pub(super) const EQUITY_TOKENIZED_CONVERT_STATUS: &str = "/sapi/v1/equity/tokenized/convert-status";
pub(super) const EQUITY_TOKENIZED_HISTORY: &str = "/sapi/v1/equity/tokenized/history";
pub(super) const EQUITY_DISCLAIMER: &str = "/sapi/v1/equity/account/disclaimer";
pub(super) const EQUITY_LISTEN_KEY: &str = "/sapi/v1/equity/listenKey";
pub(super) const FUTURES_EXCHANGE_INFO: &str = "/fapi/v1/exchangeInfo";
pub(super) const FUTURES_BOOK_TICKER: &str = "/fapi/v1/ticker/bookTicker";
pub(super) const FUTURES_KLINES: &str = "/fapi/v1/klines";
pub(super) const FUTURES_PREMIUM_INDEX: &str = "/fapi/v1/premiumIndex";
pub(super) const FUTURES_FUNDING_RATE_HISTORY: &str = "/fapi/v1/fundingRate";
pub(super) const FUTURES_OPEN_INTEREST: &str = "/fapi/v1/openInterest";
pub(super) const FUTURES_OPEN_INTEREST_HISTORY: &str = "/futures/data/openInterestHist";
pub(super) const FUTURES_GLOBAL_LONG_SHORT_ACCOUNT_RATIO: &str =
    "/futures/data/globalLongShortAccountRatio";
pub(super) const FUTURES_TOP_LONG_SHORT_ACCOUNT_RATIO: &str =
    "/futures/data/topLongShortAccountRatio";
pub(super) const FUTURES_TOP_LONG_SHORT_POSITION_RATIO: &str =
    "/futures/data/topLongShortPositionRatio";
pub(super) const FUTURES_TAKER_LONG_SHORT_RATIO: &str = "/futures/data/takerlongshortRatio";
pub(super) const FUTURES_BASIS: &str = "/futures/data/basis";
pub(super) const SPOT_ACCOUNT_BALANCE: &str = "/api/v3/account";
pub(super) const SPOT_COMMISSION_RATE: &str = "/api/v3/account/commission";
pub(super) const WALLET_BALANCE: &str = "/sapi/v1/asset/wallet/balance";
pub(super) const FUNDING_WALLET: &str = "/sapi/v1/asset/get-funding-asset";
pub(super) const UNIVERSAL_TRANSFER: &str = "/sapi/v1/asset/transfer";
pub(super) const SIMPLE_EARN_ACCOUNT: &str = "/sapi/v1/simple-earn/account";
pub(super) const SIMPLE_EARN_FLEXIBLE_LIST: &str = "/sapi/v1/simple-earn/flexible/list";
pub(super) const SIMPLE_EARN_LOCKED_LIST: &str = "/sapi/v1/simple-earn/locked/list";
pub(super) const SIMPLE_EARN_FLEXIBLE_POSITION: &str = "/sapi/v1/simple-earn/flexible/position";
pub(super) const SIMPLE_EARN_LOCKED_POSITION: &str = "/sapi/v1/simple-earn/locked/position";
pub(super) const SIMPLE_EARN_FLEXIBLE_SUBSCRIBE: &str = "/sapi/v1/simple-earn/flexible/subscribe";
pub(super) const SIMPLE_EARN_LOCKED_SUBSCRIBE: &str = "/sapi/v1/simple-earn/locked/subscribe";
pub(super) const SIMPLE_EARN_FLEXIBLE_REDEEM: &str = "/sapi/v1/simple-earn/flexible/redeem";
pub(super) const SIMPLE_EARN_LOCKED_REDEEM: &str = "/sapi/v1/simple-earn/locked/redeem";
pub(super) const SIMPLE_EARN_FLEXIBLE_SUBSCRIPTIONS: &str =
    "/sapi/v1/simple-earn/flexible/history/subscriptionRecord";
pub(super) const SIMPLE_EARN_LOCKED_SUBSCRIPTIONS: &str =
    "/sapi/v1/simple-earn/locked/history/subscriptionRecord";
pub(super) const SIMPLE_EARN_FLEXIBLE_REDEMPTIONS: &str =
    "/sapi/v1/simple-earn/flexible/history/redemptionRecord";
pub(super) const SIMPLE_EARN_LOCKED_REDEMPTIONS: &str =
    "/sapi/v1/simple-earn/locked/history/redemptionRecord";
pub(super) const SIMPLE_EARN_FLEXIBLE_REWARDS: &str =
    "/sapi/v1/simple-earn/flexible/history/rewardsRecord";
pub(super) const SIMPLE_EARN_LOCKED_REWARDS: &str =
    "/sapi/v1/simple-earn/locked/history/rewardsRecord";
pub(super) const FLEXIBLE_LOAN_COLLATERAL_REPAY_RATE: &str = "/sapi/v2/loan/flexible/repay/rate";
pub(super) const FLEXIBLE_LOAN_ADJUST_LTV: &str = "/sapi/v2/loan/flexible/adjust/ltv";
pub(super) const FLEXIBLE_LOAN_BORROW: &str = "/sapi/v2/loan/flexible/borrow";
pub(super) const FLEXIBLE_LOAN_REPAY: &str = "/sapi/v2/loan/flexible/repay";
pub(super) const FLEXIBLE_LOAN_ASSETS: &str = "/sapi/v2/loan/flexible/loanable/data";
pub(super) const FLEXIBLE_LOAN_BORROW_HISTORY: &str = "/sapi/v2/loan/flexible/borrow/history";
pub(super) const FLEXIBLE_LOAN_COLLATERAL_ASSETS: &str = "/sapi/v2/loan/flexible/collateral/data";
pub(super) const FLEXIBLE_LOAN_INTEREST_RATE_HISTORY: &str = "/sapi/v2/loan/interestRateHistory";
pub(super) const FLEXIBLE_LOAN_LIQUIDATION_HISTORY: &str =
    "/sapi/v2/loan/flexible/liquidation/history";
pub(super) const FLEXIBLE_LOAN_LTV_ADJUSTMENT_HISTORY: &str =
    "/sapi/v2/loan/flexible/ltv/adjustment/history";
pub(super) const FLEXIBLE_LOAN_ONGOING_ORDERS: &str = "/sapi/v2/loan/flexible/ongoing/orders";
pub(super) const FLEXIBLE_LOAN_REPAYMENT_HISTORY: &str = "/sapi/v2/loan/flexible/repay/history";
pub(super) const CRYPTO_LOAN_INCOME_HISTORY: &str = "/sapi/v1/loan/income";
pub(super) const STABLE_LOAN_BORROW_HISTORY: &str = "/sapi/v1/loan/borrow/history";
pub(super) const STABLE_LOAN_LTV_ADJUSTMENT_HISTORY: &str = "/sapi/v1/loan/ltv/adjustment/history";
pub(super) const STABLE_LOAN_REPAYMENT_HISTORY: &str = "/sapi/v1/loan/repay/history";
pub(super) const ETH_STAKING_ACCOUNT: &str = "/sapi/v2/eth-staking/account";
pub(super) const ETH_STAKING_QUOTA: &str = "/sapi/v1/eth-staking/eth/quota";
pub(super) const ETH_REDEMPTION_HISTORY: &str =
    "/sapi/v1/eth-staking/eth/history/redemptionHistory";
pub(super) const ETH_STAKING_HISTORY: &str = "/sapi/v1/eth-staking/eth/history/stakingHistory";
pub(super) const WBETH_RATE_HISTORY: &str = "/sapi/v1/eth-staking/eth/history/rateHistory";
pub(super) const WBETH_REWARDS_HISTORY: &str =
    "/sapi/v1/eth-staking/eth/history/wbethRewardsHistory";
pub(super) const WBETH_UNWRAP_HISTORY: &str = "/sapi/v1/eth-staking/wbeth/history/unwrapHistory";
pub(super) const WBETH_WRAP_HISTORY: &str = "/sapi/v1/eth-staking/wbeth/history/wrapHistory";
pub(super) const ETH_STAKING_REDEEM: &str = "/sapi/v1/eth-staking/eth/redeem";
pub(super) const ETH_STAKING_SUBSCRIBE: &str = "/sapi/v2/eth-staking/eth/stake";
pub(super) const WBETH_WRAP: &str = "/sapi/v1/eth-staking/wbeth/wrap";
pub(super) const ONCHAIN_YIELDS_PERSONAL_QUOTA: &str =
    "/sapi/v1/onchain-yields/locked/personalLeftQuota";
pub(super) const ONCHAIN_YIELDS_PRODUCTS: &str = "/sapi/v1/onchain-yields/locked/list";
pub(super) const ONCHAIN_YIELDS_POSITIONS: &str = "/sapi/v1/onchain-yields/locked/position";
pub(super) const ONCHAIN_YIELDS_REDEMPTION_HISTORY: &str =
    "/sapi/v1/onchain-yields/locked/history/redemptionRecord";
pub(super) const ONCHAIN_YIELDS_REWARDS_HISTORY: &str =
    "/sapi/v1/onchain-yields/locked/history/rewardsRecord";
pub(super) const ONCHAIN_YIELDS_SUBSCRIPTION_PREVIEW: &str =
    "/sapi/v1/onchain-yields/locked/subscriptionPreview";
pub(super) const ONCHAIN_YIELDS_SUBSCRIPTION_HISTORY: &str =
    "/sapi/v1/onchain-yields/locked/history/subscriptionRecord";
pub(super) const ONCHAIN_YIELDS_ACCOUNT: &str = "/sapi/v1/onchain-yields/account";
pub(super) const ONCHAIN_YIELDS_REDEEM: &str = "/sapi/v1/onchain-yields/locked/redeem";
pub(super) const ONCHAIN_YIELDS_SET_AUTO_SUBSCRIBE: &str =
    "/sapi/v1/onchain-yields/locked/setAutoSubscribe";
pub(super) const ONCHAIN_YIELDS_SET_REDEEM_OPTION: &str =
    "/sapi/v1/onchain-yields/locked/setRedeemOption";
pub(super) const ONCHAIN_YIELDS_SUBSCRIBE: &str = "/sapi/v1/onchain-yields/locked/subscribe";
pub(super) const SOFT_STAKING_PRODUCTS: &str = "/sapi/v1/soft-staking/list";
pub(super) const SOFT_STAKING_REWARDS_HISTORY: &str = "/sapi/v1/soft-staking/history/rewardsRecord";
pub(super) const SOFT_STAKING_SET: &str = "/sapi/v1/soft-staking/set";
pub(super) const SOL_STAKING_CLAIM: &str = "/sapi/v1/sol-staking/sol/claim";
pub(super) const BNSOL_RATE_HISTORY: &str = "/sapi/v1/sol-staking/sol/history/rateHistory";
pub(super) const BNSOL_REWARDS_HISTORY: &str =
    "/sapi/v1/sol-staking/sol/history/bnsolRewardsHistory";
pub(super) const SOL_BOOST_REWARDS_HISTORY: &str =
    "/sapi/v1/sol-staking/sol/history/boostRewardsHistory";
pub(super) const SOL_REDEMPTION_HISTORY: &str =
    "/sapi/v1/sol-staking/sol/history/redemptionHistory";
pub(super) const SOL_STAKING_HISTORY: &str = "/sapi/v1/sol-staking/sol/history/stakingHistory";
pub(super) const SOL_STAKING_QUOTA: &str = "/sapi/v1/sol-staking/sol/quota";
pub(super) const SOL_UNCLAIMED_REWARDS: &str = "/sapi/v1/sol-staking/sol/history/unclaimedRewards";
pub(super) const SOL_STAKING_REDEEM: &str = "/sapi/v1/sol-staking/sol/redeem";
pub(super) const SOL_STAKING_ACCOUNT: &str = "/sapi/v1/sol-staking/account";
pub(super) const SOL_STAKING_SUBSCRIBE: &str = "/sapi/v1/sol-staking/sol/stake";
pub(super) const SUBACCOUNT_LIST: &str = "/sapi/v1/sub-account/list";
pub(super) const SUBACCOUNT_STATUS: &str = "/sapi/v1/sub-account/status";
pub(super) const SUBACCOUNT_TRANSACTION_STATISTICS: &str =
    "/sapi/v1/sub-account/transaction-statistics";
pub(super) const SUBACCOUNT_FUTURES_POSITION_RISK: &str =
    "/sapi/v2/sub-account/futures/positionRisk";
pub(super) const SUBACCOUNT_FUTURES_ACCOUNT: &str = "/sapi/v2/sub-account/futures/account";
pub(super) const SUBACCOUNT_MARGIN_ACCOUNT: &str = "/sapi/v1/sub-account/margin/account";
pub(super) const SUBACCOUNT_FUTURES_SUMMARY: &str = "/sapi/v2/sub-account/futures/accountSummary";
pub(super) const SUBACCOUNT_MARGIN_SUMMARY: &str = "/sapi/v1/sub-account/margin/accountSummary";
pub(super) const SUBACCOUNT_ASSETS: &str = "/sapi/v4/sub-account/assets";
pub(super) const SUBACCOUNT_SPOT_SUMMARY: &str = "/sapi/v1/sub-account/spotSummary";
pub(super) const SUBACCOUNT_FUTURES_TRANSFER: &str = "/sapi/v1/sub-account/futures/transfer";
pub(super) const SUBACCOUNT_MARGIN_TRANSFER: &str = "/sapi/v1/sub-account/margin/transfer";
pub(super) const SUBACCOUNT_FUTURES_TRANSFER_HISTORY: &str =
    "/sapi/v1/sub-account/futures/internalTransfer";
pub(super) const SUBACCOUNT_FUTURES_INTERNAL_TRANSFER: &str =
    "/sapi/v1/sub-account/futures/internalTransfer";
pub(super) const SUBACCOUNT_SPOT_TRANSFER_HISTORY: &str =
    "/sapi/v1/sub-account/sub/transfer/history";
pub(super) const SUBACCOUNT_UNIVERSAL_TRANSFER: &str = "/sapi/v1/sub-account/universalTransfer";
pub(super) const SUBACCOUNT_TRANSFER_HISTORY: &str = "/sapi/v1/sub-account/transfer/subUserHistory";
pub(super) const SUBACCOUNT_TO_MASTER_TRANSFER: &str = "/sapi/v1/sub-account/transfer/subToMaster";
pub(super) const SUBACCOUNT_TO_SUBACCOUNT_TRANSFER: &str = "/sapi/v1/sub-account/transfer/subToSub";
pub(super) const FUTURES_ACCOUNT_BALANCE: &str = "/fapi/v3/balance";
pub(super) const FUTURES_ACCOUNT_INFO: &str = "/fapi/v3/account";
pub(super) const FUTURES_COMMISSION_RATE: &str = "/fapi/v1/commissionRate";
pub(super) const FUTURES_INCOME_HISTORY: &str = "/fapi/v1/income";
pub(super) const FUTURES_USER_DATA_STREAM: &str = "/fapi/v1/listenKey";
pub(super) const SPOT_ORDER: &str = "/api/v3/order";
pub(super) const SPOT_TEST_ORDER: &str = "/api/v3/order/test";
pub(super) const SPOT_OPEN_ORDERS: &str = "/api/v3/openOrders";
pub(super) const SPOT_ALL_ORDERS: &str = "/api/v3/allOrders";
pub(super) const SPOT_ACCOUNT_TRADES: &str = "/api/v3/myTrades";
pub(super) const SPOT_ORDER_LIST_OCO: &str = "/api/v3/orderList/oco";
pub(super) const SPOT_ORDER_LIST_OTO: &str = "/api/v3/orderList/oto";
pub(super) const SPOT_ORDER_LIST_OTOCO: &str = "/api/v3/orderList/otoco";
pub(super) const SPOT_PREVENTED_MATCHES: &str = "/api/v3/myPreventedMatches";
pub(super) const SPOT_ALLOCATIONS: &str = "/api/v3/myAllocations";
pub(super) const SPOT_ORDER_RATE_LIMIT: &str = "/api/v3/rateLimit/order";
pub(super) const FUTURES_LEVERAGE: &str = "/fapi/v1/leverage";
pub(super) const FUTURES_ORDER: &str = "/fapi/v1/order";
pub(super) const FUTURES_TEST_ORDER: &str = "/fapi/v1/order/test";
pub(super) const FUTURES_CANCEL_ALL_OPEN_ORDERS: &str = "/fapi/v1/allOpenOrders";
pub(super) const FUTURES_ALL_ORDERS: &str = "/fapi/v1/allOrders";
pub(super) const FUTURES_OPEN_ORDER: &str = "/fapi/v1/openOrder";
pub(super) const FUTURES_OPEN_ORDERS: &str = "/fapi/v1/openOrders";
pub(super) const FUTURES_ALGO_ORDER: &str = "/fapi/v1/algoOrder";
pub(super) const FUTURES_CANCEL_ALL_OPEN_ALGO_ORDERS: &str = "/fapi/v1/algoOpenOrders";
pub(super) const FUTURES_OPEN_ALGO_ORDERS: &str = "/fapi/v1/openAlgoOrders";
pub(super) const FUTURES_ALL_ALGO_ORDERS: &str = "/fapi/v1/allAlgoOrders";
pub(super) const FUTURES_ACCOUNT_TRADES: &str = "/fapi/v1/userTrades";
pub(super) const FUTURES_POSITION_INFO: &str = "/fapi/v3/positionRisk";
