"""Same-prefix native input errors have one constructor per exchange."""

import re
from collections import defaultdict

import pytest

from tests.unit.rust_dispatch import mask
from tests.unit.test_exchange_structure import EXCHANGES, NATIVE


def invalid_prefixes(source):
    clean = mask(source)
    for match in re.finditer(r"\bfn\s+invalid\s*\(", clean):
        start = clean.index("{", match.end())
        depth = 1
        end = start + 1
        while depth:
            depth += (clean[end] == "{") - (clean[end] == "}")
            end += 1
        body = source[start:end]
        prefix = re.search(r'format!\("([^"{]*)', body)
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
    source = """fn invalid(message: &str) -> Error { Error(format!("KuCoin: {message}")) }
fn invalid(message: impl Into<String>) -> Error { Error(format!("KuCoin: {}", message.into())) }"""
    assert list(invalid_prefixes(source)) == ["KuCoin: ", "KuCoin: "]
