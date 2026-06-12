"""Tests for live-test safety controls."""
# ruff: noqa: D103

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

    with pytest.raises(pytest.skip.Exception, match="RUN_LIVE_TRADING_TESTS=1"):
        module.pytest_runtest_setup(_stateful_item(module))


def test_stateful_live_test_runs_after_explicit_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_test_conftest()
    monkeypatch.setenv("RUN_LIVE_TRADING_TESTS", "1")

    module.pytest_runtest_setup(_stateful_item(module))


def test_change_contract_methods_are_classified_as_stateful(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_test_conftest()

    def test_contract_account(client: object) -> None:
        client.change_contract_leverage()

    source = """
def test_contract_account(client):
    client.change_contract_leverage()
"""
    monkeypatch.setattr(module.inspect, "getsource", lambda _: source)

    class TestItem:
        obj = test_contract_account

    assert module._calls_stateful_client_method(TestItem())


@pytest.mark.parametrize(
    "path",
    [
        Path("sync_support/backpack/test_stateful_trade.py"),
        Path("async_support/aster/test_stateful_account.py"),
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
