"""Same-prefix native input errors have one constructor per exchange."""

import re
from collections import defaultdict

import pytest

from tests.unit.rust_dispatch import mask
from tests.unit.test_exchange_structure import EXCHANGES, NATIVE


def invalid_prefixes(source):
    clean = mask(source)
    for match in re.finditer(r"\bfn\s+\w+\s*(?:<[^{}]*>)?\(", clean):
        start = clean.index("{", match.end())
        depth = 1
        end = start + 1
        while depth:
            depth += (clean[end] == "{") - (clean[end] == "}")
            end += 1
        body = source[start:end]
        if not re.search(r"->\s*(?:crate::)?DcexError", clean[match.start():start]) or not re.search(r"InvalidInput\s*\(\s*format!", mask(body)):
            continue
        prefix = re.search(r'InvalidInput\s*\(\s*format!\s*\(\s*"([^"{]*)', body)
        yield prefix[1] if prefix else ""


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
