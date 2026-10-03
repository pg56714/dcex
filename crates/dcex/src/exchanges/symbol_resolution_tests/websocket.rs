use super::*;
use futures_util::StreamExt;

#[tokio::test]
async fn extended_resolves_symbols_in_the_handshake_path() {
    let case = cases()
        .into_iter()
        .find(|case| case.exchange == "extended")
        .unwrap();
    let row = &case.rows[0];
    for input in [&row.product_symbol, &row.exchange_symbol, "NOT-LISTED"] {
        let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
        let mut client = crate::ws::extended::ExtendedPublicWebSocket::with_url(
            format!("ws://{}", listener.local_addr().unwrap()),
            Duration::from_secs(2),
        )
        .unwrap()
        .with_product_table(ProductTable::new(case.rows.clone()));
        if input == "NOT-LISTED" {
            assert!(
                client
                    .subscribe_orderbook(Some(input), None)
                    .await
                    .unwrap_err()
                    .to_string()
                    .contains("Cannot resolve")
            );
            assert!(
                tokio::time::timeout(Duration::from_millis(2), listener.accept())
                    .await
                    .is_err()
            );
            continue;
        }
        let capture = tokio::spawn(async move {
            let (stream, _) = listener.accept().await.unwrap();
            tokio_tungstenite::accept_hdr_async(
                stream,
                |request: &tokio_tungstenite::tungstenite::handshake::server::Request, response| {
                    assert!(request.uri().path().ends_with("/orderbooks/BTC-USD"));
                    Ok(response)
                },
            )
            .await
            .unwrap()
        });
        client.subscribe_orderbook(Some(input), None).await.unwrap();
        capture.await.unwrap();
    }
}

#[tokio::test]
async fn kucoin_resolves_symbols_before_the_bullet_handshake() {
    use tokio::io::{AsyncReadExt, AsyncWriteExt};
    for case in cases().into_iter().filter(|case| case.exchange == "kucoin") {
        let row = &case.rows[0];
        for input in [&row.product_symbol, &row.exchange_symbol, "NOT-LISTED"] {
            let http = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
            let url = format!("http://{}", http.local_addr().unwrap());
            let mut client = crate::ws::kucoin::KucoinPublicWebSocket::with_market_base_urls(
                Duration::from_secs(2),
                url.clone(),
                url,
                if row.product_type == "spot" {
                    kucoin::KucoinMarket::Spot
                } else {
                    kucoin::KucoinMarket::Futures
                },
            )
            .unwrap();
            client.set_product_table(ProductTable::new(case.rows.clone()));
            if input == "NOT-LISTED" {
                assert!(
                    client
                        .subscribe_orderbook(input)
                        .await
                        .unwrap_err()
                        .to_string()
                        .contains("Cannot resolve")
                );
                assert!(
                    tokio::time::timeout(Duration::from_millis(2), http.accept())
                        .await
                        .is_err()
                );
                continue;
            }
            let ws = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
            let endpoint = format!("ws://{}", ws.local_addr().unwrap());
            let bullet = tokio::spawn(async move {
                let (mut stream, _) = http.accept().await.unwrap();
                let mut bytes = [0; 4096];
                assert!(stream.read(&mut bytes).await.unwrap() > 0);
                let body = serde_json::json!({"code":"200000","data":{"token":"local-fixture","instanceServers":[{"endpoint":endpoint}]}}).to_string();
                stream.write_all(format!("HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}", body.len()).as_bytes()).await.unwrap();
            });
            let capture = tokio::spawn(async move {
                let (stream, _) = ws.accept().await.unwrap();
                let mut socket = tokio_tungstenite::accept_async(stream).await.unwrap();
                socket
                    .next()
                    .await
                    .unwrap()
                    .unwrap()
                    .into_text()
                    .unwrap()
                    .to_string()
            });
            client.connect().await.unwrap();
            client.subscribe_orderbook(input).await.unwrap();
            assert!(capture.await.unwrap().contains(&row.exchange_symbol));
            bullet.await.unwrap();
        }
    }
}

async fn subscribe(case: &Case, url: String, symbol: &str, connect: bool) -> crate::Result<()> {
    let timeout = Duration::from_secs(2);
    let table = ProductTable::new(case.rows.clone());
    let spot = case.rows[0].product_type == "spot";
    macro_rules! send {
        ($client:expr, $method:ident($($arg:expr),*)) => {{
            let mut client = $client?;
            client.set_product_table(table);
            if connect { client.connect().await?; }
            client.$method($($arg),*).await.map(|_| ())
        }};
    }
    match case.exchange {
        "arcus" => send!(
            crate::ws::arcus::ArcusWebSocket::with_url(url, timeout),
            subscribe("l2Orderbook", Some(symbol))
        ),
        "aster" => send!(
            crate::ws::aster::AsterPublicWebSocket::with_url(
                if spot {
                    aster::AsterMarket::Spot
                } else {
                    aster::AsterMarket::Futures
                },
                url,
                timeout
            ),
            subscribe_orderbook(symbol)
        ),
        "backpack" => send!(
            crate::ws::backpack::BackpackPublicWebSocket::with_url(url, timeout),
            subscribe_orderbook(symbol)
        ),
        "binance" => send!(
            crate::ws::binance::BinancePublicWebSocket::with_profile_url(
                if spot {
                    "spot"
                } else if case.rows[0].product_type == "option" {
                    "options_public"
                } else {
                    "futures_public"
                },
                Some(url),
                timeout
            ),
            subscribe_orderbook(symbol)
        ),
        "bingx" => send!(
            if spot {
                crate::ws::bingx::BingxPublicWebSocket::with_spot_url(url, timeout)
            } else {
                crate::ws::bingx::BingxPublicWebSocket::with_swap_url(url, timeout)
            },
            subscribe_orderbook(symbol, 5, "500ms")
        ),
        "bitget" => send!(
            crate::ws::bitget::BitgetPublicWebSocket::with_url(
                case.category.unwrap(),
                format!("{url}/v3/ws/public"),
                timeout
            ),
            subscribe_orderbook(symbol, 50)
        ),
        "bybit" => send!(
            crate::ws::bybit::BybitPublicWebSocket::with_url(case.category.unwrap(), url, timeout),
            subscribe_orderbook(
                symbol,
                if case.category == Some("option") {
                    25
                } else {
                    50
                }
            )
        ),
        "hyperliquid" => send!(
            crate::ws::hyperliquid::HyperliquidPublicWebSocket::with_url(url, timeout),
            subscribe_orderbook(symbol)
        ),
        "kraken" if spot => send!(
            crate::ws::kraken::KrakenPublicWebSocket::with_url(url, timeout),
            subscribe_orderbook(symbol, 10)
        ),
        "kraken" => send!(
            crate::ws::kraken::KrakenFuturesWebSocket::with_url(url, timeout),
            subscribe("book", Some(vec![symbol.into()]))
        ),
        "lighter" => send!(
            crate::ws::lighter::LighterPublicWebSocket::with_url(url, timeout),
            subscribe_orderbook(symbol)
        ),
        "mexc" if spot => send!(
            crate::ws::mexc::MexcPublicWebSocket::with_url(url, timeout),
            subscribe_orderbook(symbol, "100ms")
        ),
        "mexc" => send!(
            crate::ws::mexc::MexcFuturesWebSocket::with_url(url, timeout),
            subscribe("depth", Some(symbol), None, None)
        ),
        "okx" => send!(
            crate::ws::okx::OkxPublicWebSocket::with_url(url, timeout),
            subscribe_orderbook(symbol)
        ),
        "ondo" if spot => send!(
            crate::ws::ondo::OndoPublicWebSocket::with_url(url, timeout),
            subscribe_spot_depth(vec![symbol.into()])
        ),
        "ondo" => send!(
            crate::ws::ondo::OndoPublicWebSocket::with_url(url, timeout),
            subscribe_depth(vec![symbol.into()])
        ),
        _ => unreachable!(),
    }
}

#[tokio::test]
async fn loaded_websocket_symbols_reach_exact_market_frames() {
    let mut failures = Vec::new();
    for mut case in cases()
        .into_iter()
        .filter(|case| !["extended", "kucoin"].contains(&case.exchange))
    {
        for row in &mut case.rows {
            row.base_currency = "BTC".into();
            row.quote_currency = if case.exchange == "kraken" {
                "USD"
            } else {
                "USDT"
            }
            .into();
        }
        let row = &case.rows[0];
        let native = if case.exchange == "hyperliquid" {
            serde_json::from_str::<(String, u64)>(&row.exchange_symbol)
                .unwrap()
                .0
        } else {
            row.exchange_symbol.clone()
        };
        let expected = if case.exchange == "kraken" && row.product_type == "spot" {
            "BTC/USD".to_string()
        } else if ["binance", "aster"].contains(&case.exchange) {
            native.to_ascii_lowercase()
        } else {
            native.clone()
        };
        let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
        let url = format!("ws://{}", listener.local_addr().unwrap());
        let error = subscribe(&case, url, "NOT-LISTED", false)
            .await
            .unwrap_err();
        assert!(
            error.to_string().contains("Cannot resolve"),
            "{} did not resolve before transport: {error}",
            case.exchange
        );
        assert!(
            tokio::time::timeout(Duration::from_millis(2), listener.accept())
                .await
                .is_err()
        );
        for input in [&row.product_symbol, &native] {
            let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
            let url = format!("ws://{}", listener.local_addr().unwrap());
            let capture = tokio::spawn(async move {
                let (stream, _) = listener.accept().await.unwrap();
                let mut websocket = tokio_tungstenite::accept_async(stream).await.unwrap();
                websocket
                    .next()
                    .await
                    .unwrap()
                    .unwrap()
                    .into_text()
                    .unwrap()
                    .to_string()
            });
            if let Err(error) = subscribe(&case, url, input, true).await {
                capture.abort();
                failures.push(format!("{} {}: {error}", case.exchange, case.method));
                continue;
            }
            let wire = tokio::time::timeout(Duration::from_secs(2), capture)
                .await
                .unwrap()
                .unwrap();
            assert!(
                wire.contains(&expected),
                "{} used the wrong WS instrument",
                case.exchange
            );
        }
    }
    assert!(failures.is_empty(), "{}", failures.join("\n"));
}
