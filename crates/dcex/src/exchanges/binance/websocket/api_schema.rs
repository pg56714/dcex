// Parameters checked against official Binance WebSocket API documents, 2026-09-26.
use super::api::BinanceWebSocketApiMarket;
#[derive(Clone, Copy, PartialEq, Eq)]
pub(super) enum Auth {
    Public,
    Key,
    Signed,
}
#[derive(Clone, Copy)]
pub(super) enum Kind {
    Text,
    Integer,
    Decimal,
    Bool,
    Strings,
}
pub(super) struct Field {
    pub name: &'static str,
    pub kind: Kind,
    pub required: bool,
}
pub(super) fn schema(
    market: BinanceWebSocketApiMarket,
    method: &str,
) -> Option<(Auth, &'static [Field])> {
    match (market, method) {
        (BinanceWebSocketApiMarket::CoinFutures, "account.status") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::CoinFutures, "account.balance") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::CoinFutures, "order.cancel") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "origClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::CoinFutures, "order.modify") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "side",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "quantity",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "price",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "origClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "priceMatch",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "modifyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::CoinFutures, "order.place") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "side",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "type",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "positionSide",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "timeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "quantity",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "reduceOnly",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "price",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "newClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "priceMatch",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::CoinFutures, "account.position") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "marginAsset",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pair",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::CoinFutures, "order.status") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "origClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::CoinFutures, "userDataStream.stop") => Some((Auth::Key, &[])),
        (BinanceWebSocketApiMarket::CoinFutures, "userDataStream.ping") => Some((Auth::Key, &[])),
        (BinanceWebSocketApiMarket::CoinFutures, "userDataStream.start") => Some((Auth::Key, &[])),
        (BinanceWebSocketApiMarket::Spot, "ping") => Some((Auth::Public, &[])),
        (BinanceWebSocketApiMarket::Spot, "time") => Some((Auth::Public, &[])),
        (BinanceWebSocketApiMarket::Spot, "exchangeInfo") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "symbols",
                    kind: Kind::Strings,
                    required: false,
                },
                Field {
                    name: "permissions",
                    kind: Kind::Strings,
                    required: false,
                },
                Field {
                    name: "showPermissionSets",
                    kind: Kind::Bool,
                    required: false,
                },
                Field {
                    name: "symbolStatus",
                    kind: Kind::Text,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "executionRules") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "symbols",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "symbolStatus",
                    kind: Kind::Text,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "depth") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "symbolStatus",
                    kind: Kind::Text,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "trades.recent") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "trades.historical") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "fromId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "blockTrades.historical") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "fromId",
                    kind: Kind::Integer,
                    required: true,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "trades.aggregate") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "fromId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "startTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "endTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "klines") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "interval",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "startTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "endTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "timeZone",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "uiKlines") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "interval",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "startTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "endTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "timeZone",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "avgPrice") => Some((
            Auth::Public,
            &[Field {
                name: "symbol",
                kind: Kind::Text,
                required: true,
            }],
        )),
        (BinanceWebSocketApiMarket::Spot, "ticker.24hr") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "symbols",
                    kind: Kind::Strings,
                    required: false,
                },
                Field {
                    name: "type",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "symbolStatus",
                    kind: Kind::Text,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "ticker.tradingDay") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "symbols",
                    kind: Kind::Strings,
                    required: false,
                },
                Field {
                    name: "timeZone",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "type",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "symbolStatus",
                    kind: Kind::Text,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "ticker") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "symbols",
                    kind: Kind::Strings,
                    required: false,
                },
                Field {
                    name: "type",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "windowSize",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "symbolStatus",
                    kind: Kind::Text,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "ticker.price") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "symbols",
                    kind: Kind::Strings,
                    required: false,
                },
                Field {
                    name: "symbolStatus",
                    kind: Kind::Text,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "ticker.book") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "symbols",
                    kind: Kind::Strings,
                    required: false,
                },
                Field {
                    name: "symbolStatus",
                    kind: Kind::Text,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "referencePrice") => Some((
            Auth::Public,
            &[Field {
                name: "symbol",
                kind: Kind::Text,
                required: true,
            }],
        )),
        (BinanceWebSocketApiMarket::Spot, "referencePrice.calculation") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "symbolStatus",
                    kind: Kind::Text,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "session.logon") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "session.status") => Some((Auth::Public, &[])),
        (BinanceWebSocketApiMarket::Spot, "session.logout") => Some((Auth::Public, &[])),
        (BinanceWebSocketApiMarket::Spot, "order.place") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "side",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "type",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "timeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "price",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "quantity",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "quoteOrderQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "newClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "stopPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "trailingDelta",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "icebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "strategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "strategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "order.test") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "side",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "type",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "timeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "price",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "quantity",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "quoteOrderQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "newClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "stopPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "trailingDelta",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "icebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "strategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "strategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "computeCommissionRates",
                    kind: Kind::Bool,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "order.cancel") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "origClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "cancelRestrictions",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "order.cancelReplace") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "cancelReplaceMode",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "cancelOrderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "cancelOrigClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "cancelNewClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "side",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "type",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "timeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "price",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "quantity",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "quoteOrderQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "newClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "stopPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "trailingDelta",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "icebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "strategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "strategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "cancelRestrictions",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "orderRateLimitExceededMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "order.amend.keepPriority") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "origClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newQty",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "openOrders.cancelAll") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "orderList.place.oco") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "listClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "side",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "quantity",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "aboveType",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "aboveClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "aboveIcebergQty",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "abovePrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "aboveStopPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "aboveTrailingDelta",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "aboveTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "aboveStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "aboveStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "abovePegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "abovePegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "abovePegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "belowType",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "belowClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "belowIcebergQty",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "belowPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "belowStopPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "belowTrailingDelta",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "belowTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "belowStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "belowStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "belowPegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "belowPegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "belowPegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "orderList.place.oto") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "listClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingType",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "workingSide",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "workingClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPrice",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "workingQuantity",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "workingIcebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "workingTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "workingStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "workingPegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingType",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "pendingSide",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "pendingClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingStopPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingTrailingDelta",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingQuantity",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "pendingIcebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingPegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingPegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingPegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "orderList.place.otoco") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "listClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingType",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "workingSide",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "workingClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPrice",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "workingQuantity",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "workingIcebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "workingTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "workingStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "workingPegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingSide",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "pendingQuantity",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "pendingAboveType",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "pendingAboveClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingAbovePrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingAboveStopPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingAboveTrailingDelta",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingAboveIcebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingAboveTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingAboveStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingAboveStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingAbovePegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingAbovePegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingAbovePegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingBelowType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingBelowClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingBelowPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingBelowStopPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingBelowTrailingDelta",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingBelowIcebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingBelowTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingBelowStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingBelowStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingBelowPegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingBelowPegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingBelowPegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "orderList.place.opo") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "listClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingType",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "workingSide",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "workingClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPrice",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "workingQuantity",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "workingIcebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "workingTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "workingStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "workingPegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingType",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "pendingSide",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "pendingClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingStopPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingTrailingDelta",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingIcebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingPegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingPegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingPegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "orderList.place.opoco") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "listClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingType",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "workingSide",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "workingClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPrice",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "workingQuantity",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "workingIcebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "workingTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "workingStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "workingPegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "workingPegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingSide",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "pendingAboveType",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "pendingAboveClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingAbovePrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingAboveStopPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingAboveTrailingDelta",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingAboveIcebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingAboveTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingAboveStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingAboveStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingAbovePegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingAbovePegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingAbovePegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingBelowType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingBelowClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingBelowPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingBelowStopPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingBelowTrailingDelta",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingBelowIcebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "pendingBelowTimeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingBelowStrategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingBelowStrategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "pendingBelowPegPriceType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingBelowPegOffsetType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "pendingBelowPegOffsetValue",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "orderList.cancel") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "orderListId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "listClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "sor.order.place") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "side",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "type",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "timeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "price",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "quantity",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "newClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "icebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "strategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "strategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "sor.order.test") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "side",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "type",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "timeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "price",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "quantity",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "newClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "icebergQty",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "strategyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "strategyType",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "computeCommissionRates",
                    kind: Kind::Bool,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "account.status") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "omitZeroBalances",
                    kind: Kind::Bool,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "order.status") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "origClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "openOrders.status") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "allOrders") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "startTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "endTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "orderList.status") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "origClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "orderListId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "openOrderLists.status") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "allOrderLists") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "fromId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "startTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "endTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "myTrades") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "startTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "endTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "fromId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "account.rateLimits.orders") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "myPreventedMatches") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "preventedMatchId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "fromPreventedMatchId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "myAllocations") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "startTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "endTime",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "fromAllocationId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "account.commission") => Some((
            Auth::Signed,
            &[Field {
                name: "symbol",
                kind: Kind::Text,
                required: true,
            }],
        )),
        (BinanceWebSocketApiMarket::Spot, "order.amendments") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: true,
                },
                Field {
                    name: "fromExecutionId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "myFilters") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Spot, "userDataStream.subscribe") => Some((Auth::Public, &[])),
        (BinanceWebSocketApiMarket::Spot, "userDataStream.unsubscribe") => Some((
            Auth::Public,
            &[Field {
                name: "subscriptionId",
                kind: Kind::Integer,
                required: false,
            }],
        )),
        (BinanceWebSocketApiMarket::Spot, "session.subscriptions") => Some((Auth::Public, &[])),
        (BinanceWebSocketApiMarket::Spot, "userDataStream.subscribe.signature") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Decimal,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "order.place") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "side",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "type",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "positionSide",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "timeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "reduceOnly",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "quantity",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "price",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "newClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "priceMatch",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "goodTillDate",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "order.modify") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "side",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "quantity",
                    kind: Kind::Decimal,
                    required: true,
                },
                Field {
                    name: "price",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "origClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "priceMatch",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "modifyId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "reduceOnly",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "order.cancel") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "origClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "order.status") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "orderId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "origClientOrderId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "algoOrder.place") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "algoType",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "side",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "type",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "positionSide",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "timeInForce",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "quantity",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "price",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "triggerPrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "workingType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "priceMatch",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "closePosition",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "priceProtect",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "reduceOnly",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "activatePrice",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "callbackRate",
                    kind: Kind::Decimal,
                    required: false,
                },
                Field {
                    name: "clientAlgoId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "newOrderRespType",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "selfTradePreventionMode",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "goodTillDate",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "algoOrder.cancel") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "algoId",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "clientAlgoId",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "v2/account.status") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "v2/account.balance") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "v2/account.position") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: false,
                },
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "depth") => Some((
            Auth::Public,
            &[
                Field {
                    name: "symbol",
                    kind: Kind::Text,
                    required: true,
                },
                Field {
                    name: "limit",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "ticker.price") => Some((
            Auth::Public,
            &[Field {
                name: "symbol",
                kind: Kind::Text,
                required: false,
            }],
        )),
        (BinanceWebSocketApiMarket::Futures, "ticker.book") => Some((
            Auth::Public,
            &[Field {
                name: "symbol",
                kind: Kind::Text,
                required: false,
            }],
        )),
        (BinanceWebSocketApiMarket::Futures, "userDataStream.start") => Some((Auth::Key, &[])),
        (BinanceWebSocketApiMarket::Futures, "userDataStream.ping") => Some((Auth::Key, &[])),
        (BinanceWebSocketApiMarket::Futures, "userDataStream.stop") => Some((Auth::Key, &[])),
        (BinanceWebSocketApiMarket::Futures, "session.logon") => Some((
            Auth::Signed,
            &[
                Field {
                    name: "timestamp",
                    kind: Kind::Integer,
                    required: false,
                },
                Field {
                    name: "recvWindow",
                    kind: Kind::Integer,
                    required: false,
                },
            ],
        )),
        (BinanceWebSocketApiMarket::Futures, "session.status") => Some((Auth::Public, &[])),
        (BinanceWebSocketApiMarket::Futures, "session.logout") => Some((Auth::Public, &[])),
        _ => None,
    }
}
