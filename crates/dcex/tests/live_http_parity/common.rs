use std::collections::HashMap;
use std::sync::OnceLock;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use dcex::exchange::ValidatedResponse;
use tokio::time::sleep;

pub(crate) const BTC_USDT_SPOT: &str = "BTC-USDT-SPOT";
pub(crate) const BTC_USDT_SWAP: &str = "BTC-USDT-SWAP";
pub(crate) const BTC_USD_SWAP: &str = "BTC-USD-SWAP";

type Params = Vec<(String, String)>;

#[derive(Clone)]
pub(crate) struct Case {
    pub(crate) method: &'static str,
    pub(crate) params: Params,
}

impl Case {
    pub(crate) fn new(method: &'static str, params: &[(&str, &str)]) -> Self {
        Self {
            method,
            params: params
                .iter()
                .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
                .collect(),
        }
    }
}

pub(crate) fn live_http_enabled() -> bool {
    env_value("RUN_LIVE_HTTP_TESTS").as_deref() == Some("1")
}

fn env_value(name: &str) -> Option<String> {
    std::env::var(name)
        .ok()
        .filter(|value| !value.is_empty())
        .or_else(|| dotenv_values().get(name).cloned())
}

pub(crate) fn require_env(names: &[&str]) -> Option<Vec<String>> {
    let mut values = Vec::with_capacity(names.len());
    let mut missing = Vec::new();
    for name in names {
        match env_value(name) {
            Some(value) => values.push(value),
            None => missing.push(*name),
        }
    }
    if missing.is_empty() {
        Some(values)
    } else {
        let message = format!(
            "missing required live private environment variables: {}",
            missing.join(", ")
        );
        if live_http_enabled() {
            panic!("{message}");
        }
        eprintln!("skipping live private test; {message}");
        None
    }
}

fn dotenv_values() -> &'static HashMap<String, String> {
    static VALUES: OnceLock<HashMap<String, String>> = OnceLock::new();
    VALUES.get_or_init(|| {
        let contents = std::env::current_dir()
            .ok()
            .and_then(|directory| {
                directory
                    .ancestors()
                    .map(|ancestor| ancestor.join(".env"))
                    .find_map(|path| std::fs::read_to_string(path).ok())
            })
            .unwrap_or_default();
        contents
            .lines()
            .filter_map(|line| {
                let line = line.trim();
                if line.is_empty() || line.starts_with('#') {
                    return None;
                }
                let (key, value) = line.split_once('=')?;
                let value = value.trim().trim_matches('"').trim_matches('\'');
                Some((key.trim().to_string(), value.to_string()))
            })
            .collect()
    })
}

pub(crate) fn now_ms() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("system clock should be after unix epoch")
        .as_millis()
}

fn assert_success(response: &ValidatedResponse) {
    assert!((200..300).contains(&response.status), "{response:?}");
    assert!(!response.data.is_null(), "{response:?}");
}

pub(crate) async fn run_cases<F, Fut>(cases: Vec<Case>, request: F) -> dcex::Result<()>
where
    F: FnMut(Case) -> Fut,
    Fut: std::future::Future<Output = dcex::Result<ValidatedResponse>>,
{
    run_cases_with_delay(cases, Duration::ZERO, request).await
}

pub(crate) async fn run_cases_with_delay<F, Fut>(
    cases: Vec<Case>,
    delay: Duration,
    mut request: F,
) -> dcex::Result<()>
where
    F: FnMut(Case) -> Fut,
    Fut: std::future::Future<Output = dcex::Result<ValidatedResponse>>,
{
    if !live_http_enabled() {
        eprintln!("skipping live HTTP parity test; set RUN_LIVE_HTTP_TESTS=1");
        return Ok(());
    }

    for case in cases {
        let method = case.method;
        let response = request(case).await?;
        assert_success(&response);
        eprintln!("ok {method}");
        if !delay.is_zero() {
            sleep(delay).await;
        }
    }
    Ok(())
}

pub(crate) async fn run_private_cases<F, Fut>(
    env_names: &[&str],
    cases: Vec<Case>,
    request: F,
) -> dcex::Result<()>
where
    F: FnMut(Case) -> Fut,
    Fut: std::future::Future<Output = dcex::Result<ValidatedResponse>>,
{
    if !live_http_enabled() {
        eprintln!("skipping live private parity test; set RUN_LIVE_HTTP_TESTS=1");
        return Ok(());
    }
    if require_env(env_names).is_none() {
        return Ok(());
    }
    run_cases(cases, request).await
}

pub(crate) fn is_bitget_unified_account_error(error: &dcex::DcexError) -> bool {
    error.to_string().contains("40085") || error.to_string().contains("Unified Account mode")
}
