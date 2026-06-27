mod live_http_parity {
    macro_rules! request_case {
        ($client:expr, $case:expr, [$($method:ident => $method_with:ident),+ $(,)?]) => {{
            let case = $case;
            match case.method {
                $(
                    stringify!($method) => $client.$method_with(case.params).await,
                )+
                method => Err(dcex::DcexError::InvalidInput(format!(
                    "unsupported live parity method: {method}",
                ))),
            }
        }};
    }

    mod common;

    mod aster;
    mod backpack;
    mod binance;
    mod bingx;
    mod bitget;
    mod bitmart;
    mod bitmex;
    mod bybit;
    mod gateio;
    mod hyperliquid;
    mod kraken;
    mod kucoin;
    mod lighter;
    mod mexc;
    mod okx;
}
