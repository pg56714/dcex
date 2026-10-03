"""Tests for live-test safety controls."""
# ruff: noqa: D103

import ast
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_test_conftest() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "conftest.py"
    spec = importlib.util.spec_from_file_location("dcex_test_conftest", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load tests/conftest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _stateful_item(module: ModuleType) -> object:
    class StatefulItem:
        stash = {module._relative_path_key: Path("sync_support/bybit/test_trade.py")}

        def get_closest_marker(self, name: str) -> object | None:
            return object() if name == "stateful" else None

    return StatefulItem()


def test_stateful_live_test_requires_explicit_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_test_conftest()
    monkeypatch.delenv("RUN_LIVE_TRADING_TESTS", raising=False)
    monkeypatch.setattr("tests.live_gate.LIVE_TRADING_ENABLED", False)

    with pytest.raises(pytest.skip.Exception, match="RUN_LIVE_TRADING_TESTS=1"):
        module.pytest_runtest_setup(_stateful_item(module))


def test_stateful_live_test_runs_after_explicit_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_test_conftest()
    monkeypatch.setenv("RUN_LIVE_TRADING_TESTS", "1")
    monkeypatch.setattr("tests.live_gate.LIVE_TRADING_ENABLED", True)

    module.pytest_runtest_setup(_stateful_item(module))


def test_dotenv_cannot_enable_stateful_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tests.live_gate.LIVE_TRADING_ENABLED", False)
    monkeypatch.delenv("RUN_LIVE_TRADING_TESTS", raising=False)

    def fake_load_dotenv(**kwargs):
        monkeypatch.setenv("RUN_LIVE_TRADING_TESTS", "1")

    monkeypatch.setattr("dotenv.load_dotenv", fake_load_dotenv)
    module = _load_test_conftest()
    assert not module._stateful_tests_enabled()
    with pytest.raises(pytest.skip.Exception):
        module.pytest_runtest_setup(_stateful_item(module))


@pytest.mark.parametrize(
    "path",
    [
        Path("sync_support/backpack/test_stateful_trade.py"),
        Path("async_support/aster/test_stateful_trade.py"),
    ],
)
def test_stateful_test_files_are_classified_by_path(path: Path) -> None:
    module = _load_test_conftest()

    assert module._is_stateful_path(path)


def test_regular_live_test_files_are_not_classified_by_path() -> None:
    module = _load_test_conftest()

    assert not module._is_stateful_path(Path("sync_support/bybit/test_account.py"))


def test_collection_marks_stateful_file_without_matching_method_prefix(tmp_path: Path) -> None:
    module = _load_test_conftest()

    def read_only_test_body() -> None:
        pass

    class Config:
        rootpath = tmp_path

    class Item:
        fspath = tmp_path / "tests/sync_support/backpack/test_stateful_trade.py"
        stash: dict[object, object] = {}
        obj = read_only_test_body
        markers: list[object] = []

        def add_marker(self, marker: object) -> None:
            self.markers.append(marker)

    item = Item()
    module.pytest_collection_modifyitems(Config(), [item])

    assert any(getattr(marker, "name", None) == "stateful" for marker in item.markers)


def test_account_mutation_calls_cannot_select_stateful_tests(tmp_path: Path) -> None:
    module = _load_test_conftest()

    class Config:
        rootpath = tmp_path

    class Item:
        fspath = tmp_path / "tests/sync_support/okx/test_account.py"
        stash = {}
        markers = []

        def add_marker(self, marker):
            self.markers.append(marker)

        def obj(self, client):
            client.set_position_mode(posMode="net_mode")

    item = Item()
    module.pytest_collection_modifyitems(Config(), [item])
    assert not any(marker.name == "stateful" for marker in item.markers)
    assert not module._is_stateful_path(Path("sync_support/aster/test_stateful_account.py"))


def test_old_live_account_settings_have_no_mutating_calls() -> None:
    root = Path(__file__).resolve().parents[1]
    for mode in ("sync_support", "async_support"):
        for exchange in ("okx", "mexc"):
            tree = ast.parse(
                (root / mode / exchange / "test_account.py").read_text(encoding="utf-8")
            )
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    assert not node.func.attr.startswith(("set_", "change_")), node.func.attr
