"""Capture explicit process opt-in before any test configuration loads dotenv."""

import os

LIVE_TRADING_ENABLED = os.environ.get("RUN_LIVE_TRADING_TESTS") == "1"


def stateful_tests_enabled() -> bool:
    """Return the process opt-in captured before credential files are loaded."""
    return LIVE_TRADING_ENABLED
