"""Same-prefix native input errors have one constructor per exchange."""

import re
from collections import defaultdict

import pytest

from tests.unit.rust_dispatch import TOKENS, function_spans, mask
from tests.unit.test_exchange_structure import EXCHANGES, NATIVE


def invalid_prefixes(source):
    clean = mask(source)
    constants = {}
    for match in re.finditer(r"\b(?:const|let)\s+(\w+)(?:\s*:[^=;]+)?\s*=", clean):
        position = match.end()
        while source[position].isspace():
            position += 1
        token = TOKENS.match(source, position)
        if token and token[0].startswith(('"', 'r"', 'r#')):
            constants[match[1]] = token[0][token[0].index('"') + 1:token[0].rindex('"')]
    for _, signature, start, end in function_spans(source):
        body = source[start:end]
        code = mask(body)
        if not re.search(r"->\s*(?:\w+::)*(?:DcexError\b|Result\s*<)", clean[signature:start]) or not re.search(r"\bInvalidInput\s*\(", code):
            continue
        # Error constructors have no conditional control flow; normal request
        # validators can report several unrelated errors from the same method.
        if re.search(r"\b(?:if|match|for|while|loop)\b", code):
            continue
        if "Result" in clean[signature:start] and not re.search(r"(?:^|;)\s*(?:return\s+)?Err\s*\(", code[1:-1]):
            continue
        for call in re.finditer(r"\bformat!\s*\(", code):
            position = call.end()
            while body[position].isspace():
                position += 1
            token = TOKENS.match(body, position)
            if not token or not token[0].startswith(('"', 'r"', 'r#')):
                continue
            text = token[0][token[0].index('"') + 1:token[0].rindex('"')]
            if text.startswith("{}"):
                argument = re.match(r"\s*,\s*(\w+)", body[token.end():])
                if argument and argument[1] in constants:
                    text = constants[argument[1]] + text[2:]
            else:
                text = re.sub(r"\{(\w+)\}", lambda m: constants.get(m[1], m[0]), text)
            prefix = text.split("{", 1)[0]
            if prefix:
                yield prefix


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_invalid_error_prefix_has_one_owner(exchange):
    owners = defaultdict(list)
    for path in (NATIVE / exchange).rglob("*.rs"):
        if "tests" not in path.parts:
            for prefix in invalid_prefixes(path.read_text(encoding="utf-8")):
                owners[prefix].append(path)
    assert all(len(paths) == 1 for paths in owners.values()), dict(owners)


def test_duplicate_helper_with_different_signatures_is_detected():
    source = """fn invalid(message: &str) -> DcexError { DcexError::InvalidInput(format!("KuCoin: {message}")) }
fn other<T: Display>(message: T) -> DcexError { DcexError::InvalidInput(format!("KuCoin: {}", message.into())) }"""
    assert list(invalid_prefixes(source)) == ["KuCoin: ", "KuCoin: "]


def test_named_generic_and_multiline_error_constructors_are_scanned():
    source = '''fn invalid_ws<T: Display>(message: T) -> DcexError {
        DcexError::InvalidInput(format!(
            "Binance WS: {message}"
        ))
    }'''
    assert list(invalid_prefixes(source)) == ["Binance WS: "]


@pytest.mark.parametrize("source", [
    'fn fail<T>(m: &str) -> Result<T> { Err(DcexError::InvalidInput(format!("X: {m}"))) }',
    'fn fail(m: &str) -> super::DcexError { let text = format!("X: {m}"); super::DcexError::InvalidInput(text) }',
    'fn fail(m: &str) -> DcexError { DcexError::InvalidInput(format!(r#"X: {m}"#)) }',
    'const PREFIX: &str = "X: "; fn fail(m: &str) -> Result<()> { Err(DcexError::InvalidInput(format!("{}{m}", PREFIX))) }',
    'const PREFIX: &str = "X: "; fn fail(m: &str) -> Result<()> { Err(DcexError::InvalidInput(format!("{PREFIX}{m}"))) }',
])
def test_error_constructor_forms_keep_the_actual_prefix(source):
    assert list(invalid_prefixes(source)) == ["X: "]


def test_bodiless_trait_signature_does_not_consume_the_next_function():
    source = 'trait E { fn missing(&self) -> DcexError; } fn next() -> Result<()> { Ok(()) }'
    assert list(invalid_prefixes(source)) == []
