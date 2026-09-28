"""Guard the reviewed BingX documentation and financial type contracts."""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_all_public_docstrings_start_with_a_summary():
    for path in (ROOT / "dcex").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        containers = [tree, *(node for node in ast.walk(tree) if isinstance(node, ast.ClassDef))]
        for node in (node for container in containers for node in container.body):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name.startswith("_"):
                continue
            doc = ast.get_docstring(node, clean=False)
            if doc is None and "bingx" not in path.parts:
                continue  # Check existing docstrings; missing-doc policy is separate.
            assert doc and doc.strip(), (path, node.name)
            assert not doc.lstrip().startswith(("Args:", "Returns:", "Raises:")), (path, node.name)


@pytest.mark.parametrize("prefix", ["dcex", "dcex/async_support"])
def test_bingx_financial_parameters_do_not_advertise_float(prefix):
    tree = ast.parse((ROOT / prefix / "bingx/_trade_http.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.arg) and node.annotation:
            assert "float" not in ast.unparse(node.annotation), node.arg


def test_all_docstrings_have_at_most_one_consecutive_blank_line():
    for path in (ROOT / "dcex").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node, clean=False)
                assert not doc or not re.search(r"\n[ \t]*\n[ \t]*\n", doc), (path, getattr(node, "name", "module"))
