//! Exact symbol resolution exercised through local HTTP transports only.
use crate::exchange::ValidatedResponse;
use crate::exchanges::*;
use crate::product_table::{MarketInfo, ProductTable};
use std::io::{Read, Write};
use std::net::TcpListener;
use std::time::{Duration, Instant};

#[path = "symbol_resolution_tests/market_scope.rs"]
mod market_scope;
#[path = "symbol_resolution_tests/websocket.rs"]
mod websocket;

struct Case {
    exchange: &'static str,
    method: &'static str,
    key: &'static str,
    category: Option<&'static str>,
    rows: Vec<MarketInfo>,
}

fn row(exchange: &str, product: &str, native: &str, kind: &str, category: &str) -> MarketInfo {
    MarketInfo {
        exchange: exchange.into(),
        product_symbol: product.into(),
        exchange_symbol: native.into(),
        product_type: kind.into(),
        exchange_type: category.into(),
        ..MarketInfo::default()
    }
}

async fn request(
    case: &Case,
    url: String,
    table: Option<ProductTable>,
    symbol: &str,
) -> crate::Result<ValidatedResponse> {
    let timeout = Duration::from_secs(2);
    let mut params = vec![(case.key.into(), symbol.into())];
    if let Some(category) = case.category {
        params.push(("category".into(), category.into()));
    }
    macro_rules! call {
        ($client:expr) => {{
            let client = $client?;
            let client = match table {
                Some(table) => client.with_product_table(table),
                None => client,
            };
            client.public_request(case.method, params).await
        }};
    }
    match case.exchange {
        "arcus" => call!(arcus::ArcusClient::public(timeout)?.with_base_url(url)),
        "aster" => call!(aster::AsterClient::with_base_urls(
            None,
            None,
            None,
            timeout,
            url.clone(),
            url
        )),
        "backpack" => call!(backpack::BackpackClient::with_base_url(
            None, None, 5000, timeout, url
        )),
        "binance" => call!(binance::BinanceClient::with_all_base_urls(
            None,
            None,
            timeout,
            url.clone(),
            url.clone(),
            url
        )),
        "bingx" => call!(bingx::BingxClient::with_base_url(None, None, timeout, url)),
        "bitget" => call!(bitget::BitgetClient::with_base_url(
            None, None, None, timeout, url
        )),
        "bybit" => call!(bybit::BybitClient::with_base_url(
            None, None, 5000, false, timeout, url
        )),
        "extended" => call!(extended::ExtendedClient::with_base_url(
            None,
            timeout,
            url,
            "offline-test".into()
        )),
        "hyperliquid" => call!(hyperliquid::HyperliquidClient::with_endpoint(
            false, None, None, timeout, url
        )),
        "kraken" => call!(kraken::KrakenClient::with_base_urls(
            None,
            None,
            None,
            None,
            timeout,
            url.clone(),
            url
        )),
        "kucoin" => call!(kucoin::KucoinClient::with_base_urls(
            None,
            None,
            None,
            timeout,
            url.clone(),
            url
        )),
        "lighter" => call!(lighter::LighterClient::with_base_url(timeout, url)),
        "mexc" => call!(mexc::MexcClient::with_base_urls(
            None,
            None,
            timeout,
            url.clone(),
            url
        )),
        "okx" => call!(okx::OkxClient::with_base_url(
            None,
            None,
            None,
            "0".into(),
            timeout,
            url
        )),
        "ondo" => call!(ondo::OndoClient::with_base_url(None, None, timeout, url)),
        _ => unreachable!(),
    }
}

fn server(exchange: &str) -> (String, std::thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    listener.set_nonblocking(true).unwrap();
    let url = format!("http://{}", listener.local_addr().unwrap());
    let body = match exchange {
        "binance" => r#"{}"#,
        "okx" => r#"{"code":"0","data":[]}"#,
        "bitget" => r#"{"code":"00000","data":{}}"#,
        "kucoin" => r#"{"code":"200000","data":{}}"#,
        _ => r#"{"code":0,"retCode":0,"success":true,"status":"OK","error":[],"data":{}}"#,
    };
    let handle = std::thread::spawn(move || {
        let deadline = Instant::now() + Duration::from_secs(3);
        let (mut stream, _) = loop {
            if let Ok(connection) = listener.accept() {
                break connection;
            }
            if Instant::now() >= deadline {
                return String::new();
            }
            std::thread::sleep(Duration::from_millis(2));
        };
        stream.set_nonblocking(false).unwrap();
        stream
            .set_read_timeout(Some(Duration::from_secs(2)))
            .unwrap();
        let mut bytes = Vec::new();
        loop {
            let mut buffer = [0; 4096];
            let count = stream.read(&mut buffer).unwrap();
            if count == 0 {
                break;
            }
            bytes.extend_from_slice(&buffer[..count]);
            let text = String::from_utf8_lossy(&bytes);
            if let Some(end) = text.find("\r\n\r\n") {
                let length = text[..end]
                    .lines()
                    .find_map(|line| {
                        line.to_ascii_lowercase()
                            .strip_prefix("content-length:")
                            .and_then(|v| v.trim().parse::<usize>().ok())
                    })
                    .unwrap_or(0);
                if bytes.len() >= end + 4 + length {
                    break;
                }
            }
        }
        write!(stream,"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",body.len()).unwrap();
        String::from_utf8(bytes).unwrap()
    });
    (url, handle)
}

fn cases() -> Vec<Case> {
    let mut cases = Vec::new();
    for (exchange, method, key, category, native, kind, exchange_type) in [
        (
            "arcus",
            "get_bbo",
            "market",
            None,
            "BTC-USD",
            "swap",
            "PERPETUAL",
        ),
        (
            "aster",
            "get_spot_orderbook",
            "product_symbol",
            None,
            "BTCUSDT",
            "spot",
            "spot",
        ),
        (
            "aster",
            "get_futures_orderbook",
            "product_symbol",
            None,
            "BTCUSDT",
            "swap",
            "PERPETUAL",
        ),
        (
            "backpack",
            "get_order_book_depth",
            "product_symbol",
            None,
            "BTC_USDC",
            "spot",
            "SPOT",
        ),
        (
            "backpack",
            "get_order_book_depth",
            "product_symbol",
            None,
            "BTC_USDC_PERP",
            "swap",
            "PERP",
        ),
        (
            "binance",
            "get_spot_orderbook",
            "product_symbol",
            None,
            "BTCUSDT",
            "spot",
            "spot",
        ),
        (
            "binance",
            "get_futures_orderbook",
            "product_symbol",
            None,
            "BTCUSDT",
            "swap",
            "PERPETUAL",
        ),
        (
            "bingx",
            "get_spot_orderbook",
            "product_symbol",
            None,
            "BTC-USDT",
            "spot",
            "spot",
        ),
        (
            "bingx",
            "get_orderbook",
            "product_symbol",
            None,
            "BTC-USDT",
            "swap",
            "perpetual",
        ),
        (
            "bitget",
            "get_uta_orderbook",
            "product_symbol",
            Some("spot"),
            "BTCUSDT",
            "spot",
            "spot",
        ),
        (
            "bitget",
            "get_uta_orderbook",
            "product_symbol",
            Some("USDT-FUTURES"),
            "BTCUSDT",
            "swap",
            "USDT-FUTURES",
        ),
        (
            "bybit",
            "get_orderbook",
            "product_symbol",
            Some("spot"),
            "BTCUSDT",
            "spot",
            "spot",
        ),
        (
            "bybit",
            "get_orderbook",
            "product_symbol",
            Some("linear"),
            "BTCUSDT",
            "swap",
            "linear",
        ),
        (
            "extended",
            "get_orderbook",
            "product_symbol",
            None,
            "BTC-USD",
            "swap",
            "PERPETUAL",
        ),
        (
            "hyperliquid",
            "get_l2book",
            "product_symbol",
            None,
            "[\"BTC\",0]",
            "swap",
            "perpetual",
        ),
        (
            "hyperliquid",
            "get_l2book",
            "product_symbol",
            None,
            "[\"@1\",10001]",
            "spot",
            "spot",
        ),
        (
            "kraken",
            "get_spot_orderbook",
            "product_symbol",
            None,
            "XXBTZUSD",
            "spot",
            "spot",
        ),
        (
            "kraken",
            "get_futures_orderbook",
            "product_symbol",
            None,
            "PF_XBTUSD",
            "swap",
            "flexible_futures",
        ),
        (
            "kucoin",
            "get_spot_orderbook",
            "product_symbol",
            None,
            "BTC-USDT",
            "spot",
            "spot",
        ),
        (
            "kucoin",
            "get_futures_orderbook",
            "product_symbol",
            None,
            "XBTUSDTM",
            "swap",
            "FFWCSX",
        ),
        (
            "lighter",
            "get_order_book_details",
            "product_symbol",
            None,
            "0",
            "swap",
            "perp",
        ),
        (
            "lighter",
            "get_order_book_details",
            "product_symbol",
            None,
            "2048",
            "spot",
            "spot",
        ),
        (
            "mexc",
            "get_spot_orderbook",
            "product_symbol",
            None,
            "BTCUSDT",
            "spot",
            "spot",
        ),
        (
            "mexc",
            "get_contract_depth",
            "product_symbol",
            None,
            "BTC_USDT",
            "swap",
            "perpetual",
        ),
        (
            "okx",
            "get_orderbook",
            "product_symbol",
            None,
            "BTC-USDT",
            "spot",
            "SPOT",
        ),
        (
            "ondo",
            "get_depth",
            "product_symbol",
            None,
            "BTC-USDC.P",
            "swap",
            "perpetual",
        ),
        (
            "ondo",
            "get_spot_depth",
            "product_symbol",
            None,
            "BTC-USDC",
            "spot",
            "spot",
        ),
    ] {
        let quote = if ["arcus", "extended", "kraken"].contains(&exchange) {
            "USD"
        } else if ["backpack", "hyperliquid", "ondo", "lighter"].contains(&exchange) {
            "USDC"
        } else {
            "USDT"
        };
        cases.push(Case {
            exchange,
            method,
            key,
            category,
            rows: vec![row(
                exchange,
                &format!("BTC-{quote}-{}", kind.to_ascii_uppercase()),
                native,
                kind,
                exchange_type,
            )],
        });
    }
    // Real dated/option formats; adjacent expiry and strike rows must never be substituted.
    for (exchange, method, category, native, kind, exchange_type) in [
        (
            "binance",
            "get_options_orderbook",
            None,
            "BTC-261225-80000-C",
            "option",
            "OPTION",
        ),
        (
            "binance",
            "get_futures_orderbook",
            None,
            "BTCUSDT_261225",
            "futures",
            "CURRENT_QUARTER",
        ),
        (
            "bybit",
            "get_orderbook",
            Some("linear"),
            "BTCUSDT-25DEC26",
            "futures",
            "linear",
        ),
        (
            "bybit",
            "get_orderbook",
            Some("option"),
            "BTC-25DEC26-80000-C",
            "option",
            "option",
        ),
        (
            "kucoin",
            "get_futures_orderbook",
            None,
            "XBTMM26",
            "futures",
            "FFCCSX",
        ),
        (
            "kraken",
            "get_futures_orderbook",
            None,
            "FI_XBTUSD_261225",
            "futures",
            "futures_inverse",
        ),
        (
            "okx",
            "get_orderbook",
            None,
            "BTC-USD-261225",
            "futures",
            "FUTURES",
        ),
        (
            "okx",
            "get_orderbook",
            None,
            "BTC-USD-261225-80000-C",
            "option",
            "OPTION",
        ),
    ] {
        cases.push(Case {
            exchange,
            method,
            key: "product_symbol",
            category,
            rows: vec![row(
                exchange,
                &if kind == "option" {
                    "BTC-USD-261225-80000-C-OPTION".to_string()
                } else {
                    format!("BTC-USD-261225-{}", kind.to_ascii_uppercase())
                },
                native,
                kind,
                exchange_type,
            )],
        });
    }
    cases.push(Case {
        exchange: "bitget",
        method: "get_uta_orderbook",
        key: "product_symbol",
        category: Some("spot"),
        rows: vec![row(
            "bitget",
            "rCVCO-USDT-SPOT",
            "rCVCOUSDT",
            "spot",
            "spot",
        )],
    });
    // Each request sees the complete small table for its exchange, including duplicate native names.
    let all: Vec<_> = cases.iter().flat_map(|case| case.rows.clone()).collect();
    for case in &mut cases {
        let target = case.rows[0].clone();
        case.rows.extend(
            all.iter()
                .filter(|row| row.exchange == case.exchange && **row != target)
                .cloned(),
        );
    }
    cases
}

#[tokio::test]
async fn every_exchange_resolves_exact_canonical_and_native_symbols_on_wire() {
    let mut failures = Vec::new();
    for case in cases() {
        let row = &case.rows[0];
        let native = if case.exchange == "hyperliquid" {
            serde_json::from_str::<(String, u64)>(&row.exchange_symbol)
                .unwrap()
                .0
        } else {
            row.exchange_symbol.clone()
        };
        for input in [&row.product_symbol, &native] {
            let (url, capture) = server(case.exchange);
            let result = request(
                &case,
                url,
                Some(ProductTable::new(case.rows.clone())),
                input,
            )
            .await;
            if let Err(error) = result {
                failures.push(format!(
                    "{} {} {input}: {error}",
                    case.exchange, case.method
                ));
                continue;
            }
            let wire = capture.join().unwrap();
            assert!(
                wire.contains(&native),
                "{} {} used the wrong native instrument",
                case.exchange,
                case.method
            );
            assert!(
                !wire.contains(&row.product_symbol),
                "canonical leaked to wire"
            );
        }
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        listener.set_nonblocking(true).unwrap();
        for bad in [
            "NOT-LISTED",
            "btc",
            "BTC-USD-261226",
            "BTC-USD-261225-81000-C",
        ] {
            let result = request(
                &case,
                format!("http://{}", listener.local_addr().unwrap()),
                Some(ProductTable::new(case.rows.clone())),
                bad,
            )
            .await;
            assert!(
                result.is_err(),
                "{} accepted an unknown instrument",
                case.exchange
            );
            assert_eq!(
                listener.accept().unwrap_err().kind(),
                std::io::ErrorKind::WouldBlock,
                "{} sent a request before resolving",
                case.exchange
            );
        }
        // Duplicate rows in the same market must fail rather than selecting the first one.
        let mut ambiguous = case.rows.clone();
        let mut duplicate = row.clone();
        duplicate.product_symbol = format!("ALTERNATE-{}", row.product_symbol);
        ambiguous.push(duplicate);
        let error = request(
            &case,
            format!("http://{}", listener.local_addr().unwrap()),
            Some(ProductTable::new(ambiguous)),
            &native,
        )
        .await
        .unwrap_err();
        assert!(error.to_string().contains(&row.product_symbol));
        assert_eq!(
            listener.accept().unwrap_err().kind(),
            std::io::ErrorKind::WouldBlock
        );
    }
    assert!(failures.is_empty(), "{}", failures.join("\n"));
}

#[tokio::test]
async fn loaded_native_symbols_preserve_unloaded_wire_requests() {
    for case in cases() {
        let native = if case.exchange == "hyperliquid" {
            serde_json::from_str::<(String, u64)>(&case.rows[0].exchange_symbol)
                .unwrap()
                .0
        } else {
            case.rows[0].exchange_symbol.clone()
        };
        let (url, capture) = server(case.exchange);
        let result = request(&case, url, None, &native).await;
        // Existing no-table fallbacks may reject dated symbols: never relax them here.
        if let Err(error) = result {
            assert!(
                matches!(error, crate::DcexError::InvalidInput(_)),
                "unexpected fallback failure for {}",
                case.exchange
            );
            continue;
        }
        let without = capture.join().unwrap();
        let (url, capture) = server(case.exchange);
        request(
            &case,
            url,
            Some(ProductTable::new(case.rows.clone())),
            &native,
        )
        .await
        .unwrap();
        let loaded = capture.join().unwrap();
        // Compare request target and JSON body; the ephemeral Host port differs.
        let target = |request: &str| {
            let target = request
                .lines()
                .next()
                .unwrap()
                .split_whitespace()
                .nth(1)
                .unwrap();
            let url = url::Url::parse(&format!("http://localhost{target}")).unwrap();
            (
                url.path().to_string(),
                url.query_pairs()
                    .filter(|(key, _)| key != "timestamp")
                    .map(|(k, v)| (k.into_owned(), v.into_owned()))
                    .collect::<Vec<_>>(),
            )
        };
        assert_eq!(target(&without), target(&loaded), "{}", case.exchange);
        assert_eq!(
            without.split("\r\n\r\n").nth(1),
            loaded.split("\r\n\r\n").nth(1),
            "{}",
            case.exchange
        );
    }
}
