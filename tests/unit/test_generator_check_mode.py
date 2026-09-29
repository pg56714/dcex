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
