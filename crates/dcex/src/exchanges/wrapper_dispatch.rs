//! Every typed wrapper must reach its exchange dispatch with the visibility and keys it
//! declares. Python reaches the same dispatch by method name, so this is what makes the
//! typed Rust surface equivalent to the Python one.

use std::future::Future;
use std::path::Path;

use crate::{DcexError, Result};

/// One method declared through `impl_exchange_method_wrappers!`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) struct Wrapper {
    pub client: String,
    pub name: String,
    pub public: bool,
    pub keys: Vec<String>,
}

/// Wrappers declared anywhere under `src/exchanges/<exchange>/`.
pub(crate) fn declared(exchange: &str) -> Vec<Wrapper> {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("src/exchanges")
        .join(exchange);
    let mut files = Vec::new();
    collect_rs(&root, &mut files);
    files.sort();
    let mut wrappers = Vec::new();
    for file in files {
        let text = std::fs::read_to_string(&file).expect("read wrapper source");
        wrappers.extend(parse_invocations(&text));
    }
    wrappers
}

fn collect_rs(dir: &Path, out: &mut Vec<std::path::PathBuf>) {
    for entry in std::fs::read_dir(dir).expect("read exchange directory") {
        let path = entry.expect("directory entry").path();
        if path.is_dir() {
            if path.file_name().is_some_and(|name| name != "tests") {
                collect_rs(&path, out);
            }
        } else if path.extension().is_some_and(|ext| ext == "rs") {
            out.push(path);
        }
    }
}

fn parse_invocations(text: &str) -> Vec<Wrapper> {
    const MACRO: &str = "impl_exchange_method_wrappers!";
    let mut wrappers = Vec::new();
    let mut rest = text;
    while let Some(start) = rest.find(MACRO) {
        let after = &rest[start + MACRO.len()..];
        let open = after.find('{').expect("macro body");
        let body = balanced(&after[open..], '{', '}');
        let client = body[1..]
            .trim_start()
            .trim_start_matches("@extend;")
            .trim_start();
        let client = &client[..client.find(';').expect("client type")];
        for (label, public) in [("public", true), ("private", false)] {
            if let Some(list) = section(body, label) {
                wrappers.extend(parse_entries(client, list, public));
            }
        }
        rest = &after[open + body.len()..];
    }
    wrappers
}

/// The text from an opening delimiter through its matching close.
fn balanced(text: &str, open: char, close: char) -> &str {
    let mut depth = 0;
    let mut in_string = false;
    for (index, ch) in text.char_indices() {
        match ch {
            '"' => in_string = !in_string,
            _ if in_string => {}
            c if c == open => depth += 1,
            c if c == close => {
                depth -= 1;
                if depth == 0 {
                    return &text[..=index];
                }
            }
            _ => {}
        }
    }
    panic!("unbalanced wrapper macro")
}

/// The bracketed list after `public` / `private` at the top level of a macro body.
fn section<'a>(body: &'a str, label: &str) -> Option<&'a str> {
    let mut search = 0;
    while let Some(found) = body[search..].find(label) {
        let at = search + found;
        let before = body[..at].chars().next_back();
        let after = body[at + label.len()..].trim_start();
        if before.is_none_or(|c| !c.is_alphanumeric() && c != '_') && after.starts_with('[') {
            let open = body.len() - after.len();
            return Some(balanced(&body[open..], '[', ']'));
        }
        search = at + label.len();
    }
    None
}

fn parse_entries(client: &str, list: &str, public: bool) -> Vec<Wrapper> {
    let inner = &list[1..list.len() - 1];
    let mut wrappers = Vec::new();
    let mut rest = inner;
    loop {
        rest = skip_noise(rest);
        if rest.is_empty() {
            break;
        }
        let name_end = rest
            .find(|c: char| !(c.is_alphanumeric() || c == '_'))
            .expect("wrapper name");
        let name = &rest[..name_end];
        let args = balanced(&rest[name_end..], '(', ')');
        let keys = args
            .split("=>")
            .skip(1)
            .map(|part| {
                let quoted = part.trim_start();
                let end = quoted[1..].find('"').expect("key literal") + 1;
                quoted[1..end].to_string()
            })
            .collect();
        wrappers.push(Wrapper {
            client: client.trim().to_string(),
            name: name.to_string(),
            public,
            keys,
        });
        rest = &rest[name_end + args.len()..];
    }
    wrappers
}

/// Skip whitespace, commas and `#[...]` attributes.
fn skip_noise(mut text: &str) -> &str {
    loop {
        text = text.trim_start_matches(|c: char| c.is_whitespace() || c == ',');
        if text.starts_with("#[") {
            let attr = balanced(&text[1..], '[', ']');
            text = &text[1 + attr.len()..];
        } else if text.starts_with("//") {
            // Doc and line comments (doc comments become attributes on the method).
            text = text.find('\n').map_or("", |end| &text[end..]);
        } else {
            return text;
        }
    }
}

/// Call each declared wrapper the way its typed method does and report dispatch errors:
/// an unknown method for its visibility, or a declared key the dispatch rejects.
/// Every other outcome (validation of the placeholder values, transport) is fine.
pub(crate) async fn assert_dispatch<F, Fut, T>(exchange: &str, client: &str, mut call: F)
where
    F: FnMut(&'static str, bool, Vec<(String, String)>) -> Fut,
    Fut: Future<Output = Result<T>>,
{
    let wrappers: Vec<_> = declared(exchange)
        .into_iter()
        .filter(|wrapper| wrapper.client == client)
        .collect();
    assert!(
        !wrappers.is_empty(),
        "{exchange}: no {client} wrappers found"
    );
    let mut failures = Vec::new();
    for wrapper in &wrappers {
        let name: &'static str = Box::leak(wrapper.name.clone().into_boxed_str());
        let params = wrapper
            .keys
            .iter()
            .map(|key| (key.clone(), placeholder(key)))
            .collect();
        if let Err(DcexError::InvalidInput(message) | DcexError::Runtime(message)) =
            call(name, wrapper.public, params).await
        {
            let lower = message.to_ascii_lowercase();
            let unknown_method = lower.starts_with("unsupported") && lower.contains(" method");
            let rejected_key = wrapper
                .keys
                .iter()
                .any(|key| message.ends_with(&format!("parameter: {key}")));
            if unknown_method || rejected_key {
                let side = if wrapper.public { "public" } else { "private" };
                failures.push(format!("{side} {}: {message}", wrapper.name));
            }
        }
    }
    assert!(
        failures.is_empty(),
        "{exchange} {client}: {} of {} typed wrappers do not reach dispatch:\n{}",
        failures.len(),
        wrappers.len(),
        failures.join("\n")
    );
}

/// A local server that answers every request at once with a generic success body
/// (including a server time), so dispatch errors are never masked by a slow peer.
pub(crate) fn instant_server() -> String {
    use std::io::{Read, Write};
    use std::net::TcpListener;
    use std::time::{Duration, SystemTime, UNIX_EPOCH};

    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let url = format!("http://{}", listener.local_addr().expect("address"));
    std::thread::spawn(move || {
        for stream in listener.incoming() {
            let Ok(mut stream) = stream else { continue };
            std::thread::spawn(move || {
                let _ = stream.set_read_timeout(Some(Duration::from_millis(20)));
                let mut request = Vec::new();
                let mut buffer = [0u8; 8192];
                while let Ok(read) = stream.read(&mut buffer) {
                    if read == 0 {
                        break;
                    }
                    request.extend_from_slice(&buffer[..read]);
                    if request_complete(&request) {
                        break;
                    }
                }
                let now = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .map_or(0, |elapsed| elapsed.as_millis());
                let body = format!(
                    r#"{{"code":0,"retCode":0,"success":true,"serverTime":{now},"data":{{}},"result":{{}},"error":[]}}"#
                );
                let _ = write!(
                    stream,
                    "HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: {}
Connection: close

{body}",
                    body.len()
                );
            });
        }
    });
    url
}

fn request_complete(request: &[u8]) -> bool {
    let text = String::from_utf8_lossy(request);
    let Some((head, body)) = text.split_once(
        "

",
    ) else {
        return false;
    };
    let length = head
        .lines()
        .find_map(|line| {
            let (name, value) = line.split_once(':')?;
            name.eq_ignore_ascii_case("content-length")
                .then(|| value.trim().parse::<usize>().ok())
                .flatten()
        })
        .unwrap_or(0);
    body.len() >= length
}

fn placeholder(key: &str) -> String {
    let lower = key.to_ascii_lowercase();
    if lower.contains("symbol") {
        "BTC-USDT-SWAP".into()
    } else if lower.starts_with("is") || lower.contains("only") || lower == "confirm" {
        "true".into()
    } else {
        "1".into()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_visibility_attributes_and_keys() {
        let text = r#"
            crate::exchanges::impl_exchange_method_wrappers! {
                @extend; DemoClient;
                public [get_ticker(product_symbol => "product_symbol"), get_time()];
                private [
                    #[doc = "x"]
                    /// Doc comments are attributes too.
                    place_order(side => "side", qty => "quantity"),
                ];
            }
        "#;
        assert_eq!(
            parse_invocations(text),
            vec![
                Wrapper {
                    client: "DemoClient".into(),
                    name: "get_ticker".into(),
                    public: true,
                    keys: vec!["product_symbol".into()]
                },
                Wrapper {
                    client: "DemoClient".into(),
                    name: "get_time".into(),
                    public: true,
                    keys: vec![]
                },
                Wrapper {
                    client: "DemoClient".into(),
                    name: "place_order".into(),
                    public: false,
                    keys: vec!["side".into(), "quantity".into()]
                },
            ]
        );
    }

    #[test]
    fn every_exchange_declares_wrappers() {
        for exchange in [
            "arcus",
            "aster",
            "backpack",
            "binance",
            "bingx",
            "bitget",
            "bybit",
            "extended",
            "hyperliquid",
            "kraken",
            "kucoin",
            "lighter",
            "mexc",
            "okx",
            "ondo",
        ] {
            assert!(!declared(exchange).is_empty(), "{exchange}");
        }
    }
}
