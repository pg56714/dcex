mod live_http_parity {
    macro_rules! request_case {
        ($client:expr, $case:expr, [$($method:ident),+ $(,)?]) => {{
            let case = $case;
            match case.method {
                $(
                    stringify!($method) => $client.$method(case.params).await,
                )+
                method => Err(dcex::DcexError::InvalidInput(format!(
                    "unsupported live parity method: {method}",
                ))),
            }
        }};
    }

    mod common;

    mod binance;
    mod bitget;
    mod bitmart;
    mod bitmex;
    mod bybit;
    mod gateio;
    mod kraken;
    mod mexc;
    mod okx;
}
