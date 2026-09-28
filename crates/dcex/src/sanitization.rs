//! Sanitization utilities.
use regex::{Captures, Regex};
use std::sync::LazyLock;
static URL_PATTERN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"(?i)(?:https?:/{1,2}|//)[^\s<>'"]+"#).expect("valid URL sanitization regex")
});
static BEARER_TOKEN_PATTERN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+").expect("valid bearer token regex")
});
static AUTHORIZATION_PATTERN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r#"(?ix)
        ["']?\bauthorization\b["']?
        \s*[:=]\s*
        (?:
            '[^']*'
            |
            "[^"]*"
            |
            (?:basic|bearer|digest)\s+[^,\s;}\]]+
            |
            [^,\s;}\]]+
        )
        "#,
    )
    .expect("valid authorization regex")
});
static SENSITIVE_ASSIGNMENT_PATTERN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r#"(?ix)
        ["']?
        \b(?:
            api[_-]?(?:key|secret)
            |
            access[_-]?key
            |
            secret[_-]?key
            |
            signature
            |
            secret
            |
            passphrase
            |
            password
            |
            authorization
            |
            token
        )\b
        ["']?
        \s*[:=]\s*
        (?:
            '[^']*'
            |
            "[^"]*"
            |
            [^,\s&}\]]+
        )
        "#,
    )
    .expect("valid sensitive assignment regex")
});

pub fn sanitize_url(url: &str) -> String {
    let value = url.split_whitespace().next().unwrap_or_default();
    if value.is_empty() {
        return String::new();
    }

    if value.starts_with("//") {
        return sanitize_absolute_url(&format!("https:{value}"))
            .map(|safe| safe.trim_start_matches("https:").to_string())
            .unwrap_or_else(|| "<redacted-url>".to_string());
    }

    if value
        .get(..5)
        .is_some_and(|prefix| prefix.eq_ignore_ascii_case("http:"))
        || value
            .get(..6)
            .is_some_and(|prefix| prefix.eq_ignore_ascii_case("https:"))
    {
        return sanitize_absolute_url(value).unwrap_or_else(|| "<redacted-url>".to_string());
    }

    value
        .split_once('?')
        .map_or(value, |(path, _)| path)
        .split_once('#')
        .map_or_else(
            || value.split_once('?').map_or(value, |(path, _)| path),
            |(path, _)| path,
        )
        .to_string()
}

pub fn sanitize_request(request: &str) -> String {
    let request_line = request
        .split_once(" | ")
        .map_or(request, |(summary, _)| summary)
        .trim();
    let mut parts = request_line.split_whitespace();
    let Some(method) = parts.next() else {
        return "<redacted>".to_string();
    };
    let method = method.to_ascii_uppercase();
    if !matches!(
        method.as_str(),
        "DELETE" | "GET" | "HEAD" | "OPTIONS" | "PATCH" | "POST" | "PUT"
    ) {
        return "<redacted>".to_string();
    }
    let Some(url) = parts.next() else {
        return "<redacted>".to_string();
    };
    let safe_url = sanitize_url(url);
    if safe_url.is_empty() {
        "<redacted>".to_string()
    } else {
        format!("{method} {safe_url}")
    }
}

pub fn sanitize_message(message: &str) -> String {
    let sanitized = URL_PATTERN.replace_all(message, |captures: &Captures<'_>| {
        let matched_url = captures.get(0).expect("whole URL match").as_str();
        let trimmed = matched_url.trim_end_matches(['.', ',', ';', ':', '!', '?', ')', ']', '}']);
        let trailing = &matched_url[trimmed.len()..];
        format!("{}{trailing}", sanitize_url(trimmed))
    });
    let sanitized = AUTHORIZATION_PATTERN.replace_all(&sanitized, "<redacted>");
    let sanitized = BEARER_TOKEN_PATTERN.replace_all(&sanitized, "<redacted>");
    SENSITIVE_ASSIGNMENT_PATTERN
        .replace_all(&sanitized, "<redacted>")
        .into_owned()
}

fn sanitize_absolute_url(value: &str) -> Option<String> {
    let parsed = url::Url::parse(value).ok()?;
    if !matches!(parsed.scheme(), "http" | "https") {
        return None;
    }
    let host = parsed.host_str()?;
    let mut safe = format!("{}://{}", parsed.scheme(), host);
    if let Some(port) = parsed.port() {
        safe.push(':');
        safe.push_str(&port.to_string());
    }
    safe.push_str(parsed.path());
    Some(safe)
}
