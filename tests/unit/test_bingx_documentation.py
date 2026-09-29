"""Guard the reviewed BingX documentation and financial type contracts."""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def assert_docstring_summaries(source, require_functions=False):
    for node in ast.walk(ast.parse(source)):
        function = isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        if not isinstance(node, (ast.Module, ast.ClassDef)) and not (function and not node.name.startswith("_")):
            continue
        doc = ast.get_docstring(node, clean=False)
        if doc is None and not (function and require_functions):
            continue  # Missing-doc policy is separate from existing summaries.
        name = getattr(node, "name", "module")
        assert doc and doc.strip(), name
        assert not doc.lstrip().startswith(("Args:", "Returns:", "Raises:", "Yields:", "Attributes:", "Example:", "Examples:", "Note:")), name


def test_all_public_docstrings_start_with_a_summary():
    for path in [*(ROOT / "dcex").rglob("*.py"), *(ROOT / "dcex").rglob("*.pyi")]:
        assert_docstring_summaries(path.read_text(encoding="utf-8"), "bingx" in path.parts)


@pytest.mark.parametrize("source", [
    '"""Returns: missing module summary."""',
    'class Client:\n """Args: missing class summary."""',
    'if TYPE_CHECKING:\n def public():\n  """Raises: missing conditional function summary."""',
])
def test_summary_guard_covers_modules_classes_and_conditional_functions(source):
    with pytest.raises(AssertionError):
        assert_docstring_summaries(source)


@pytest.mark.parametrize("prefix", ["dcex", "dcex/async_support"])
def test_bingx_financial_parameters_do_not_advertise_float(prefix):
    tree = ast.parse((ROOT / prefix / "bingx/_trade_http.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.arg) and node.annotation:
            assert "float" not in ast.unparse(node.annotation), node.arg


def test_all_docstrings_have_at_most_one_consecutive_blank_line():
    for path in [*(ROOT / "dcex").rglob("*.py"), *(ROOT / "dcex").rglob("*.pyi")]:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node, clean=False)
                assert not doc or not re.search(r"\n[ \t]*\n[ \t]*\n", doc), (path, getattr(node, "name", "module"))


@pytest.mark.parametrize("prefix", ["Yields", "Attributes", "Example", "Examples", "Note"])
def test_additional_section_prefixes_are_not_summaries(prefix):
    with pytest.raises(AssertionError):
        assert_docstring_summaries(f'def public():\n """{prefix}: missing summary."""\n ...')
