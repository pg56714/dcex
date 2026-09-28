"""Guard the reviewed BingX documentation and financial type contracts."""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("prefix", ["dcex", "dcex/async_support"])
def test_bingx_public_docstrings_start_with_a_summary(prefix):
    for path in (ROOT / prefix / "bingx").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name.startswith("_"):
                continue
            doc = ast.get_docstring(node, clean=False)
            assert doc and doc.splitlines()[0].strip(), (path, node.name)
            assert not doc.lstrip().startswith(("Args:", "Returns:", "Raises:")), (path, node.name)


@pytest.mark.parametrize("prefix", ["dcex", "dcex/async_support"])
def test_bingx_financial_parameters_do_not_advertise_float(prefix):
    tree = ast.parse((ROOT / prefix / "bingx/_trade_http.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.arg) and node.annotation:
            assert "float" not in ast.unparse(node.annotation), node.arg


@pytest.mark.parametrize("prefix", ["dcex", "dcex/async_support"])
@pytest.mark.parametrize("file", ["bingx/_withdrawals_http.py", "mexc/_transfers_http.py"])
def test_transfer_warning_has_one_blank_line(prefix, file):
    source = (ROOT / prefix / file).read_text(encoding="utf-8")
    assert "\n\n\n        The recipient" not in source
