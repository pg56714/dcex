"""Adversarial cases for replacement and source-evidence validation."""

import pytest

from tests.unit.ledger_validation import validate_evidence, validate_superseded


def row(number, status, **extra):
    return {"row": number, "status": status, "exchange": "test", "path": "/order", **extra}


@pytest.mark.parametrize("status", ["unavailable", "blocked", "unverified", "pending"])
def test_inactive_replacement_is_rejected_even_when_self_declared(status):
    source = row(1, "superseded", superseded_by=2, replacement_routes=[{"path": "/order"}])
    with pytest.raises(AssertionError, match="inactive target"):
        validate_superseded([source, row(2, status)], [])


def test_replacement_chain_must_end_at_active_row():
    rows = [row(1, "superseded", superseded_by=2), row(2, "superseded", superseded_by=3), row(3, "implemented")]
    validate_superseded(rows, [])
    rows[-1] = row(3, "superseded", superseded_by=1)
    with pytest.raises(AssertionError, match="cycle"):
        validate_superseded(rows, [])


def test_row_cannot_authorize_its_own_different_route():
    source = row(1, "superseded", superseded_by=2, replacement_routes=[{"path": "/unrelated"}])
    with pytest.raises(AssertionError, match="undeclared replacement"):
        validate_superseded([source, row(2, "implemented", path="/unrelated")], [])


def test_superseded_without_target_requires_specific_reason():
    with pytest.raises(AssertionError, match="missing reason"):
        validate_superseded([row(1, "superseded")], [])
    validate_superseded([row(1, "superseded", superseded_reason="Historical grouped inventory without an independently callable endpoint.")], [])
    for reason in ["a" * 20, "same " * 10]:
        with pytest.raises(AssertionError, match="missing reason"):
            validate_superseded([row(1, "superseded", superseded_reason=reason)], [])


def test_evidence_resolves_full_class_and_ignores_rust_comments(tmp_path):
    (tmp_path / "sample.py").write_text("class Correct:\n    def method(self): pass\n", encoding="utf-8")
    validate_evidence(tmp_path, "sample.py::Correct.method")
    with pytest.raises(AssertionError):
        validate_evidence(tmp_path, "sample.py::Wrong.method")
    (tmp_path / "sample.rs").write_text('// fn fake() {}\nconst TEXT: &str = "fn string_fake() {}";\nfn real() {}', encoding="utf-8")
    validate_evidence(tmp_path, "sample.rs::real")
    for evidence in ["sample.rs::fake", "sample.rs::string_fake", "missing.py"]:
        with pytest.raises(AssertionError):
            validate_evidence(tmp_path, evidence)


def test_rust_char_literal_does_not_hide_the_next_symbol(tmp_path):
    (tmp_path / "sample.rs").write_text("const QUOTE: char = '\"';\nfn real() {}\n", encoding="utf-8")
    validate_evidence(tmp_path, "sample.rs::real")
