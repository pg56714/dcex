use super::endpoint_coverage::{client, server};
use crate::product_table::{MarketInfo, ProductTable};

fn table() -> ProductTable {
    ProductTable::new(
        [
            ("BTC-USDT-SPOT", "BTC-USDT", "spot"),
            ("BTC-USDT-SWAP", "BTC-USDT-SWAP", "swap"),
            ("BTC-USD-260327-FUTURES", "BTC-USD-260327", "futures"),
            ("BTC-USD-260626-FUTURES", "BTC-USD-260626", "futures"),
            (
                "BTC-USD-260327-80000-C-OPTION",
                "BTC-USD-260327-80000-C",
                "option",
            ),
        ]
        .into_iter()
        .map(|(product, native, kind)| MarketInfo {
            exchange: "okx".into(),
            product_symbol: product.into(),
            exchange_symbol: native.into(),
            product_type: kind.into(),
            exchange_type: kind.to_ascii_uppercase(),
            ..MarketInfo::default()
        })
        .collect(),
    )
}

#[tokio::test]
async fn loaded_canonical_and_native_symbols_reach_the_same_wire_instrument() {
    let table = table();
    for row in table.rows() {
        for symbol in [&row.product_symbol, &row.exchange_symbol] {
            for private in [false, true] {
                let (url, capture) = server();
                let client = client(url).with_product_table(table.clone());
                let params = vec![
                    ("product_symbol".into(), symbol.clone()),
                    ("ordId".into(), "order-fixture".into()),
                ];
                if private {
                    client
                        .private_request("get_order", params)
                        .await
                        .expect("mock order query");
                } else {
                    client
                        .public_request("get_orderbook", params)
                        .await
                        .expect("mock book");
                }
                let request = capture.join().expect("server");
                let line = request.lines().next().expect("request line");
                assert!(
                    line.contains(&format!("instId={}", row.exchange_symbol)),
                    "wrong instrument on wire"
                );
            }
        }
    }
}

#[tokio::test]
async fn unknown_dates_strikes_and_partial_names_send_nothing() {
    let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    listener.set_nonblocking(true).unwrap();
    let client =
        client(format!("http://{}", listener.local_addr().unwrap())).with_product_table(table());
    for symbol in [
        "BTC",
        "btc-usdt",
        "BTC-USD-260328",
        "BTC-USD-260327-81000-C",
    ] {
        assert!(
            client
                .public_request(
                    "get_orderbook",
                    vec![("product_symbol".into(), symbol.into())]
                )
                .await
                .is_err()
        );
        assert_eq!(
            listener.accept().unwrap_err().kind(),
            std::io::ErrorKind::WouldBlock
        );
    }
}
