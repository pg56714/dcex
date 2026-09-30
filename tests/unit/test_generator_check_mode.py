"""Generator check mode detects drift without touching output files."""

import sys
from pathlib import Path

import pytest

from scripts import generation


@pytest.mark.parametrize("stale", [False, True])
def test_check_mode_never_writes_even_when_stale(tmp_path, monkeypatch, stale):
    destination = tmp_path / "output.json"
    destination.write_text("old\n" if stale else "new\n", encoding="utf-8")
    before = destination.read_bytes(), destination.stat().st_mtime_ns
    monkeypatch.setattr(sys, "argv", ["generator", "--check"])
    monkeypatch.setattr(generation, "ROOT", tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("check mode attempted filesystem mutation")

    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "mkdir", forbidden)
    assert generation.run(lambda: generation.emit(destination, "new\n")) == int(stale)
    assert (destination.read_bytes(), destination.stat().st_mtime_ns) == before


def test_generators_require_an_explicit_mode(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["generator"])
    with pytest.raises(SystemExit) as error:
        generation.run(lambda: pytest.fail("render should not run without a mode"))
    assert error.value.code == 2


def test_schema_table_formatting_uses_stdin_and_stdout():
    source = "fn example(){let _x=1;}\n"
    result = generation.formatted(Path("example.rs"), source)
    assert result == "fn example() {\n    let _x = 1;\n}\n"


@pytest.mark.parametrize("emits_current", [False, True])
def test_removed_domain_leaves_a_read_only_orphan_failure(tmp_path, monkeypatch, emits_current):
    orphan = tmp_path / "removed_domain.py"
    orphan.write_text('"""Old generated domain."""\n', encoding="utf-8")
    before = orphan.read_bytes(), orphan.stat().st_mtime_ns
    monkeypatch.setattr(generation, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["generator", "--check"])

    def render():
        generation.own_directory(tmp_path, "*.py")
        if emits_current:
            generation.emit(tmp_path / "current.json", "{}\n")

    def forbidden(*args, **kwargs):
        raise AssertionError("check mode attempted a write or deletion")

    monkeypatch.setattr(Path, "write_text", forbidden)
    monkeypatch.setattr(Path, "unlink", forbidden)
    monkeypatch.setattr(Path, "mkdir", forbidden)
    assert generation.run(render) == 1
    assert (orphan.read_bytes(), orphan.stat().st_mtime_ns) == before


@pytest.mark.parametrize("exchange", ["kraken", "okx"])
def test_sole_schema_owner_rejects_unmarked_rust_orphans(tmp_path, monkeypatch, exchange):
    from scripts.generated_ownership import register_schema_directories
    folder = tmp_path / exchange / "generated"
    folder.mkdir(parents=True)
    orphan = folder / "unmarked.rs"
    orphan.write_text("fn unexpected() {}\n", encoding="utf8")
    before = orphan.read_bytes(), orphan.stat().st_mtime_ns
    monkeypatch.setattr(generation, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["generator", "--check"])
    assert generation.run(lambda: register_schema_directories(tmp_path)) == 1
    assert before == (orphan.read_bytes(), orphan.stat().st_mtime_ns)


def test_new_schema_output_is_shared_without_hardcoded_exclusion(monkeypatch):
    from scripts import generated_ownership
    monkeypatch.setattr(generated_ownership, "SCHEMA_JOBS", [
        *generated_ownership.SCHEMA_JOBS, ("binance", "new", "table_new", "new_schema")
    ])
    assert "new_schema.rs" in generated_ownership.schema_output_names("binance")
    assert "new_schema.rs" not in generated_ownership.schema_output_names("okx")
