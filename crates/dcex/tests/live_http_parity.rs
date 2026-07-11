mod live_http_parity {
    macro_rules! request_case {
        ($client:expr, $case:expr, [$($method:ident),+ $(,)?]) => {{
            let case = $case;
            match case.method {
                $(
                    stringify!($method) => {
                        let params = case.params;
                        match $client.public_request(stringify!($method), params.clone()).await {
                            Ok(response) => Ok(response),
                            Err(dcex::DcexError::InvalidInput(message))
                                if message.contains("unsupported") =>
                            {
                                $client.private_request(stringify!($method), params).await
                            }
                            Err(error) => Err(error),
                        }
                    },
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
    mod hyperliquid;
    mod kraken;
    mod kucoin;
    mod lighter;
    mod mexc;
    mod okx;
}
