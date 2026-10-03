//! Market scoping for native symbols: category narrowing, unscoped uniqueness and aliases.
use super::*;

fn table(rows: &[(&str, &str, &str, &str, &str)]) -> ProductTable {
    ProductTable::new(
        rows.iter()
            .map(|(exchange, product, native, kind, category)| {
                row(exchange, product, native, kind, category)
            })
            .collect(),
    )
}

fn refused_url() -> (TcpListener, String) {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    listener.set_nonblocking(true).unwrap();
    let url = format!("http://{}", listener.local_addr().unwrap());
    (listener, url)
}

fn assert_nothing_sent(listener: &TcpListener) {
    assert_eq!(
        listener.accept().unwrap_err().kind(),
        std::io::ErrorKind::WouldBlock,
        "a request was sent before the symbol resolved"
    );
}

fn pairs(values: &[(&str, &str)]) -> Vec<(String, String)> {
    values
        .iter()
        .map(|(key, value)| (key.to_string(), value.to_string()))
        .collect()
}

const TIMEOUT: Duration = Duration::from_secs(2);

fn bitget_table() -> ProductTable {
    table(&[
        ("bitget", "BTC-USDT-SPOT", "BTCUSDT", "spot", "spot"),
        ("bitget", "BTC-USDT-SWAP", "BTCUSDT", "swap", "USDT-FUTURES"),
    ])
}

async fn bitget_history(url: String, symbol: &str, category: &str) -> crate::Result<()> {
    bitget::BitgetClient::with_base_url(
        Some("key".into()),
        Some("secret".into()),
        Some("pass".into()),
        TIMEOUT,
        url,
    )?
    .with_product_table(bitget_table())
    .private_request(
        "get_uta_history_orders",
        pairs(&[("category", category), ("product_symbol", symbol)]),
    )
    .await
    .map(drop)
}

#[tokio::test]
async fn bitget_margin_category_narrows_to_spot_rows() {
    for symbol in ["BTCUSDT", "BTC-USDT-SPOT"] {
        let (url, capture) = server("bitget");
        bitget_history(url, symbol, "MARGIN").await.unwrap();
        let wire = capture.join().unwrap();
        assert!(wire.contains("category=MARGIN") && wire.contains("symbol=BTCUSDT"));
    }
    let (listener, url) = refused_url();
    let error = bitget_history(url, "BTC-USDT-SWAP", "MARGIN")
        .await
        .unwrap_err();
    assert!(error.to_string().contains("BTC-USDT-SWAP"));
    assert_nothing_sent(&listener);
}

fn bingx_table() -> ProductTable {
    table(&[
        ("bingx", "BTC-USDT-SPOT", "BTC-USDT", "spot", "spot"),
        ("bingx", "BTC-USDT-SWAP", "BTC-USDT", "swap", "perpetual"),
    ])
}

#[tokio::test]
async fn bingx_coin_margined_routes_skip_the_usdt_margined_table() {
    for loaded in [false, true] {
        let (url, capture) = server("bingx");
        let client = bingx::BingxClient::with_base_url(None, None, TIMEOUT, url).unwrap();
        let client = if loaded {
            client.with_product_table(bingx_table())
        } else {
            client
        };
        client
            .public_request(
                "get_coin_swap_orderbook",
                pairs(&[("product_symbol", "BTC-USD")]),
            )
            .await
            .unwrap();
        let wire = capture.join().unwrap();
        assert!(wire.contains("/openApi/cswap/v1/market/depth"));
        assert!(wire.contains("symbol=BTC-USD&") || wire.contains("symbol=BTC-USD "));
    }
    // Coin-M keeps its own native rule even with a table loaded.
    let (listener, url) = refused_url();
    let error = bingx::BingxClient::with_base_url(None, None, TIMEOUT, url)
        .unwrap()
        .with_product_table(bingx_table())
        .public_request(
            "get_coin_swap_orderbook",
            pairs(&[("product_symbol", "BTC-USDT")]),
        )
        .await
        .unwrap_err();
    assert!(error.to_string().contains("BASE-USD"));
    assert_nothing_sent(&listener);
}

fn kraken_table() -> ProductTable {
    let mut spot = row("kraken", "BTC-USD-SPOT", "XXBTZUSD", "spot", "spot");
    spot.base_currency = "BTC".into();
    spot.quote_currency = "USD".into();
    spot.exchange_symbol_alias = "XBTUSD".into();
    ProductTable::new(vec![spot])
}

async fn kraken_depth(url: String, table: Option<ProductTable>, symbol: &str) -> crate::Result<()> {
    let client =
        kraken::KrakenClient::with_base_urls(None, None, None, None, TIMEOUT, url.clone(), url)?;
    let client = match table {
        Some(table) => client.with_product_table(table),
        None => client,
    };
    client
        .public_request("get_spot_orderbook", pairs(&[("product_symbol", symbol)]))
        .await
        .map(drop)
}

#[tokio::test]
async fn kraken_accepts_the_official_altname_exactly() {
    for (input, wire_pair) in [
        ("BTC-USD-SPOT", "pair=XXBTZUSD"),
        ("XXBTZUSD", "pair=XXBTZUSD"),
        ("BTC/USD", "pair=XXBTZUSD"),
        ("XBTUSD", "pair=XBTUSD"),
    ] {
        let (url, capture) = server("kraken");
        kraken_depth(url, Some(kraken_table()), input)
            .await
            .unwrap();
        assert!(capture.join().unwrap().contains(wire_pair), "{input}");
    }
    // The altname is sent unchanged, exactly as without a table.
    let (url, capture) = server("kraken");
    kraken_depth(url, None, "XBTUSD").await.unwrap();
    assert!(capture.join().unwrap().contains("pair=XBTUSD"));
    let (listener, url) = refused_url();
    for input in ["xbtusd", "XBTUSDT", "XBT"] {
        assert!(
            kraken_depth(url.clone(), Some(kraken_table()), input)
                .await
                .is_err()
        );
    }
    assert_nothing_sent(&listener);
}

async fn bybit_order(url: String, table: ProductTable, symbol: &str) -> crate::Result<()> {
    bybit::BybitClient::with_base_url(
        Some("key".into()),
        Some("secret".into()),
        5000,
        false,
        TIMEOUT,
        url,
    )?
    .with_product_table(table)
    .private_request(
        "place_order",
        pairs(&[
            ("product_symbol", symbol),
            ("side", "buy"),
            ("orderType", "Limit"),
            ("qty", "1"),
            ("price", "1"),
        ]),
    )
    .await
    .map(drop)
}

#[tokio::test]
async fn bybit_unscoped_native_symbols_take_the_category_of_their_unique_row() {
    let rows = [
        ("bybit", "BTC-USDT-SPOT", "BTCUSDT", "spot", "spot"),
        ("bybit", "BTC-USDT-SWAP", "BTCUSDT", "swap", "linear"),
        ("bybit", "SOL-USDT-SPOT", "SOLUSDT", "spot", "spot"),
        ("bybit", "BTC-USD-SWAP", "BTCUSD", "swap", "inverse"),
    ];
    for (input, category, native) in [
        ("SOLUSDT", "spot", "SOLUSDT"),
        ("BTCUSD", "inverse", "BTCUSD"),
        ("BTC-USDT-SPOT", "spot", "BTCUSDT"),
        ("BTC-USDT-SWAP", "linear", "BTCUSDT"),
    ] {
        let (url, capture) = server("bybit");
        bybit_order(url, table(&rows), input).await.unwrap();
        let wire = capture.join().unwrap();
        assert!(
            wire.contains(&format!("\"category\":\"{category}\""))
                && wire.contains(&format!("\"symbol\":\"{native}\"")),
            "{input}: {wire}"
        );
    }
    let (listener, url) = refused_url();
    let error = bybit_order(url, table(&rows), "BTCUSDT")
        .await
        .unwrap_err()
        .to_string();
    assert!(error.contains("BTC-USDT-SPOT") && error.contains("BTC-USDT-SWAP"));
    assert_nothing_sent(&listener);
}

fn binance_table() -> ProductTable {
    table(&[
        ("binance", "BTC-USDT-SPOT", "BTCUSDT", "spot", "spot"),
        ("binance", "BTC-USDT-SWAP", "BTCUSDT", "swap", "PERPETUAL"),
        ("binance", "SOL-USDT-SPOT", "SOLUSDT", "spot", "spot"),
        ("binance", "XRP-USDT-SWAP", "XRPUSDT", "swap", "PERPETUAL"),
        (
            "binance_coinm",
            "BTC-USD-SWAP",
            "BTCUSD_PERP",
            "swap",
            "PERPETUAL",
        ),
    ])
}

async fn binance_klines(url: String, symbol: &str) -> crate::Result<()> {
    binance::BinanceClient::with_all_base_urls(None, None, TIMEOUT, url.clone(), url.clone(), url)?
        .with_product_table(binance_table())
        .public_request(
            "get_klines",
            pairs(&[("product_symbol", symbol), ("interval", "1m")]),
        )
        .await
        .map(drop)
}

#[tokio::test]
async fn binance_unscoped_native_symbols_route_to_their_unique_market() {
    for (input, path, native) in [
        ("SOLUSDT", "/api/v3/klines", "SOLUSDT"),
        ("XRPUSDT", "/fapi/v1/klines", "XRPUSDT"),
        ("BTC-USDT-SPOT", "/api/v3/klines", "BTCUSDT"),
        ("BTC-USDT-SWAP", "/fapi/v1/klines", "BTCUSDT"),
    ] {
        let (url, capture) = server("binance");
        binance_klines(url, input).await.unwrap();
        let wire = capture.join().unwrap();
        assert!(
            wire.contains(path) && wire.contains(&format!("symbol={native}")),
            "{input}"
        );
    }
    let (listener, url) = refused_url();
    let ambiguous = binance_klines(url.clone(), "BTCUSDT")
        .await
        .unwrap_err()
        .to_string();
    assert!(ambiguous.contains("BTC-USDT-SPOT") && ambiguous.contains("BTC-USDT-SWAP"));
    // COIN-M rows resolve, but the generic helpers do not serve COIN-M.
    for input in ["BTCUSD_PERP", "BTC-USD-SWAP"] {
        let error = binance_klines(url.clone(), input).await.unwrap_err();
        assert!(error.to_string().contains("coin-futures"), "{input}");
    }
    assert_nothing_sent(&listener);
}

#[test]
fn lighter_websocket_uses_the_network_product_namespace() {
    use crate::exchanges::lighter::chains::LighterNetwork;
    use crate::ws::lighter::LighterPublicWebSocket;
    let rows = table(&[
        ("lighter", "BTC-USDC-SWAP", "1", "swap", "perp"),
        ("lighter_robinhood", "BTC-USDC-SWAP", "7", "swap", "perp"),
    ]);
    for (network, id) in [
        (LighterNetwork::Mainnet, 1),
        (LighterNetwork::Testnet, 1),
        (LighterNetwork::Robinhood, 7),
        (LighterNetwork::RobinhoodTestnet, 7),
    ] {
        let by_network = LighterPublicWebSocket::with_network(network, TIMEOUT)
            .unwrap()
            .with_product_table(rows.clone());
        assert_eq!(
            by_network.resolve_market_symbol("BTC-USDC-SWAP").unwrap(),
            id
        );
        let by_url = LighterPublicWebSocket::with_url(network.profile().ws_url, TIMEOUT)
            .unwrap()
            .with_product_table(rows.clone());
        assert_eq!(by_url.resolve_market_symbol("BTC-USDC-SWAP").unwrap(), id);
        let custom =
            LighterPublicWebSocket::with_network_and_url(network, "ws://127.0.0.1:9", TIMEOUT)
                .unwrap()
                .with_product_table(rows.clone());
        assert_eq!(custom.resolve_market_symbol("BTC-USDC-SWAP").unwrap(), id);
    }
}

#[tokio::test]
async fn hyperliquid_native_pairs_compare_parsed_values() {
    let rows = table(&[(
        "hyperliquid",
        "BTC-USDC-SWAP",
        "[\"BTC\",0]",
        "swap",
        "perpetual",
    )]);
    for input in ["[\"BTC\",0]", "[\"BTC\", 0]", "[ \"BTC\" , 0 ]", "BTC"] {
        let (url, capture) = server("hyperliquid");
        hyperliquid::HyperliquidClient::with_endpoint(false, None, None, TIMEOUT, url)
            .unwrap()
            .with_product_table(rows.clone())
            .public_request("get_l2book", pairs(&[("product_symbol", input)]))
            .await
            .unwrap();
        assert!(
            capture.join().unwrap().contains("\"coin\":\"BTC\""),
            "{input}"
        );
    }
    for input in ["[\"BTC\", 1]", "[\"btc\", 0]"] {
        assert!(
            rows.resolve_symbol("hyperliquid", input, None, None)
                .is_err(),
            "{input}"
        );
    }
}
