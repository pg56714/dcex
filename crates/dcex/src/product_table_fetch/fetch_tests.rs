//! Product-table fetchers against trimmed, real exchange responses served locally: the
//! requests each fetcher makes and the rows it builds from them.

use std::io::{Read, Write};
use std::net::TcpListener;
use std::sync::{Arc, Mutex};
use std::time::Duration;

use crate::exchanges::{
    arcus::ArcusClient, aster::AsterClient, backpack::BackpackClient, binance::BinanceClient,
    bingx::BingxClient, bitget::BitgetClient, bybit::BybitClient, extended::ExtendedClient,
    hyperliquid::HyperliquidClient, kraken::KrakenClient, kucoin::KucoinClient,
    lighter::LighterClient, mexc::MexcClient, okx::OkxClient, ondo::OndoClient,
};

const TIMEOUT: Duration = Duration::from_secs(10);

/// Serve each request with the body of the first route whose needle appears in
/// `"METHOD target\nbody"`; unmatched requests get `{}`. Every request is recorded.
pub(super) fn serve(routes: Vec<(&'static str, String)>) -> (String, Arc<Mutex<Vec<String>>>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let url = format!("http://{}", listener.local_addr().expect("address"));
    let seen = Arc::new(Mutex::new(Vec::new()));
    let log = seen.clone();
    std::thread::spawn(move || {
        for stream in listener.incoming() {
            let Ok(mut stream) = stream else { break };
            let _ = stream.set_read_timeout(Some(Duration::from_secs(5)));
            let mut raw = Vec::new();
            let mut buffer = [0u8; 8192];
            let (head, length) = loop {
                let Ok(size) = stream.read(&mut buffer) else {
                    break (0, 0);
                };
                if size == 0 {
                    break (0, 0);
                }
                raw.extend_from_slice(&buffer[..size]);
                let text = String::from_utf8_lossy(&raw).into_owned();
                if let Some(end) = text.find("\r\n\r\n") {
                    let length = text[..end]
                        .lines()
                        .find_map(|line| {
                            line.to_ascii_lowercase()
                                .strip_prefix("content-length:")
                                .and_then(|value| value.trim().parse::<usize>().ok())
                        })
                        .unwrap_or(0);
                    break (end + 4, length);
                }
            };
            if head == 0 {
                continue;
            }
            while raw.len() < head + length {
                let Ok(size) = stream.read(&mut buffer) else {
                    break;
                };
                if size == 0 {
                    break;
                }
                raw.extend_from_slice(&buffer[..size]);
            }
            let text = String::from_utf8_lossy(&raw).into_owned();
            let request_line = text.lines().next().unwrap_or_default();
            let mut parts = request_line.split(' ');
            let key = format!(
                "{} {}\n{}",
                parts.next().unwrap_or_default(),
                parts.next().unwrap_or_default(),
                &text[head..]
            );
            let matched = routes.iter().find(|(needle, _)| key.contains(needle));
            let body = matched.map_or_else(|| "{}".to_string(), |(_, body)| body.clone());
            let prefix = if matched.is_some() { "" } else { "UNMATCHED " };
            log.lock().expect("log").push(format!("{prefix}{key}"));
            let response = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",
                body.len()
            );
            let _ = stream.write_all(response.as_bytes());
        }
    });
    (url, seen)
}

/// Routes from `tests/fixtures/product_tables/<exchange>.json`, in file order.
pub(super) fn fixture(exchange: &str) -> Vec<(&'static str, String)> {
    let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures/product_tables")
        .join(format!("{exchange}.json"));
    let routes: serde_json::Map<String, serde_json::Value> =
        serde_json::from_str(&std::fs::read_to_string(path).expect("fixture")).expect("json");
    routes
        .into_iter()
        .map(|(needle, body)| (&*Box::leak(needle.into_boxed_str()), body.to_string()))
        .collect()
}

pub(super) fn arcus(url: &str) -> ArcusClient {
    ArcusClient::public(TIMEOUT)
        .unwrap()
        .with_base_url(url.into())
        .unwrap()
}
pub(super) fn aster(url: &str) -> AsterClient {
    AsterClient::with_base_urls(None, None, None, TIMEOUT, url.into(), url.into()).unwrap()
}
pub(super) fn backpack(url: &str) -> BackpackClient {
    BackpackClient::with_base_url(None, None, 5_000, TIMEOUT, url.into()).unwrap()
}
pub(super) fn binance(url: &str) -> BinanceClient {
    BinanceClient::with_all_base_urls(None, None, TIMEOUT, url.into(), url.into(), url.into())
        .unwrap()
        .with_coin_futures_base_url(url)
}
pub(super) fn bingx(url: &str) -> BingxClient {
    BingxClient::with_base_url(None, None, TIMEOUT, url.into()).unwrap()
}
pub(super) fn bitget(url: &str) -> BitgetClient {
    BitgetClient::with_base_url(None, None, None, TIMEOUT, url.into()).unwrap()
}
pub(super) fn bybit(url: &str) -> BybitClient {
    BybitClient::with_base_url(None, None, 5_000, false, TIMEOUT, url.into()).unwrap()
}
pub(super) fn extended(url: &str) -> ExtendedClient {
    ExtendedClient::with_base_url(None, TIMEOUT, url.into(), "dcex-rust/0.1".into()).unwrap()
}
pub(super) fn hyperliquid(url: &str) -> HyperliquidClient {
    HyperliquidClient::with_endpoint(false, None, None, TIMEOUT, url.into()).unwrap()
}
pub(super) fn kraken(url: &str) -> KrakenClient {
    KrakenClient::with_base_urls(None, None, None, None, TIMEOUT, url.into(), url.into()).unwrap()
}
pub(super) fn kucoin(url: &str) -> KucoinClient {
    KucoinClient::with_base_urls(None, None, None, TIMEOUT, url.into(), url.into()).unwrap()
}
pub(super) fn lighter(url: &str) -> LighterClient {
    LighterClient::with_base_url(TIMEOUT, url.into()).unwrap()
}
pub(super) fn mexc(url: &str) -> MexcClient {
    MexcClient::with_base_urls(None, None, TIMEOUT, url.into(), url.into()).unwrap()
}
pub(super) fn okx(url: &str) -> OkxClient {
    OkxClient::with_base_url(None, None, None, "0".into(), TIMEOUT, url.into()).unwrap()
}
pub(super) fn ondo(url: &str) -> OndoClient {
    OndoClient::with_base_url(None, None, TIMEOUT, url.into()).unwrap()
}

/// Rows were built, each looks like a market of its exchange, and every request the
/// fetcher made was answered by a captured response.
#[track_caller]
fn check(exchange: &str, rows: &[MarketInfo], seen: &Arc<Mutex<Vec<String>>>) {
    let seen = seen.lock().expect("log");
    let unmatched: Vec<_> = seen
        .iter()
        .filter(|key| key.starts_with("UNMATCHED"))
        .collect();
    assert!(
        unmatched.is_empty(),
        "{exchange}: requests without a fixture: {unmatched:?}"
    );
    assert!(!rows.is_empty(), "{exchange}: no rows from {seen:?}");
    for row in rows {
        // Separate product-table scopes such as `binance_coinm` keep the exchange prefix.
        assert!(
            row.exchange == exchange || row.exchange.starts_with(&format!("{exchange}_")),
            "{row:?}"
        );
        assert!(!row.exchange_symbol.is_empty(), "{row:?}");
        assert!(
            !row.price_precision.is_empty() && !row.size_precision.is_empty(),
            "{row:?}"
        );
        let suffixes: &[&str] = match row.product_type.as_str() {
            "spot" => &["-SPOT"],
            "swap" => &["-SWAP"],
            "futures" => &["-FUTURES"],
            "option" => &[""],
            "rfq" => &["-RFQ"],
            other => panic!("{exchange}: unexpected product type {other} in {row:?}"),
        };
        assert!(
            suffixes
                .iter()
                .any(|suffix| row.product_symbol.ends_with(suffix)),
            "{row:?}"
        );
        // Dated futures read BASE-QUOTE-YYMMDD[-INVERSE]-FUTURES.
        if row.product_type == "futures" {
            let date = row.product_symbol.split('-').nth(2).unwrap_or_default();
            assert!(
                date.len() == 6 && date.bytes().all(|byte| byte.is_ascii_digit()),
                "{row:?}"
            );
        }
    }
}

macro_rules! fetch_case {
    ($test:ident, $exchange:literal, $build:ident, |$client:ident| $call:expr) => {
        #[tokio::test]
        async fn $test() {
            let (url, seen) = serve(fixture($exchange));
            let $client = $build(&url);
            let rows = tokio::time::timeout(Duration::from_secs(10), $call)
                .await
                .expect("fetch within 10s")
                .expect("rows");
            check($exchange, &rows, &seen);
        }
    };
}

use super::exchanges as fetch;
use crate::exchanges::lighter::LighterNetwork;
use crate::product_table::MarketInfo;

fetch_case!(arcus_rows, "arcus", arcus, |c| fetch::fetch_arcus(&c));
fetch_case!(aster_rows, "aster", aster, |c| fetch::fetch_aster(&c));
fetch_case!(backpack_rows, "backpack", backpack, |c| {
    fetch::fetch_backpack(&c)
});
fetch_case!(binance_rows, "binance", binance, |c| fetch::fetch_binance(
    &c, None
));
fetch_case!(bingx_rows, "bingx", bingx, |c| fetch::fetch_bingx(&c));
fetch_case!(bitget_rows, "bitget", bitget, |c| fetch::fetch_bitget(&c));
fetch_case!(bybit_rows, "bybit", bybit, |c| fetch::fetch_bybit(&c));
fetch_case!(extended_rows, "extended", extended, |c| {
    fetch::fetch_extended(&c)
});
fetch_case!(hyperliquid_rows, "hyperliquid", hyperliquid, |c| {
    fetch::fetch_hyperliquid(&c)
});
fetch_case!(kraken_rows, "kraken", kraken, |c| fetch::fetch_kraken(&c));
fetch_case!(kucoin_rows, "kucoin", kucoin, |c| fetch::fetch_kucoin(&c));
fetch_case!(lighter_rows, "lighter", lighter, |c| {
    fetch::fetch_lighter_network(&c, LighterNetwork::Mainnet)
});
fetch_case!(mexc_rows, "mexc", mexc, |c| fetch::fetch_mexc(&c));
fetch_case!(okx_rows, "okx", okx, |c| fetch::fetch_okx(&c));
fetch_case!(ondo_rows, "ondo", ondo, |c| fetch::fetch_ondo(&c));
