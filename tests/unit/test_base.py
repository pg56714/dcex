"""Unit tests for the shared HTTP manager base helpers."""

from dcex.base.http_manager import BaseHTTPManager, drop_none
from dcex.utils.common import Common


def test_drop_none_removes_only_none() -> None:
    """None values are removed; every other key is kept."""
    result = drop_none({"a": 1, "b": None, "c": "x"})
    assert result == {"a": 1, "c": "x"}


def test_drop_none_keeps_falsy_non_none() -> None:
    """Valid falsy API values (0, '', False) must survive."""
    result = drop_none({"zero": 0, "empty": "", "flag": False, "none": None})
    assert result == {"zero": 0, "empty": "", "flag": False}


def test_drop_none_returns_new_dict() -> None:
    """The input dict is not mutated."""
    original = {"a": 1, "b": None}
    result = drop_none(original)
    assert original == {"a": 1, "b": None}
    assert result is not original


def test_drop_none_empty() -> None:
    """An empty payload stays empty."""
    assert drop_none({}) == {}


def test_setup_logger_defaults_to_module_name() -> None:
    """Without a supplied logger, the logger is named after the class module."""

    class Dummy(BaseHTTPManager):
        EXCHANGE = Common.BINANCE

    logger = Dummy()._setup_logger(None)
    assert logger.name == Dummy.__module__


def test_setup_logger_uses_supplied_logger() -> None:
    """A supplied logger is returned unchanged."""
    import logging

    class Dummy(BaseHTTPManager):
        pass

    custom = logging.getLogger("custom-test-logger")
    assert Dummy()._setup_logger(custom) is custom
