"""Helper functions for logging configuration and timestamp generation."""

import os
from collections.abc import Callable
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Protocol, overload

from .. import _native


class LoggingModuleProtocol(Protocol):
    """Protocol for logging module with required attributes and methods."""

    Formatter: type
    basicConfig: Callable[..., Any]
    getLogger: Callable[..., Any]


@overload
def generate_timestamp(iso_format: bool = False) -> int: ...


@overload
def generate_timestamp(iso_format: bool = True) -> str: ...


def generate_timestamp(iso_format: bool = False) -> int | str:
    """
    Generate timestamp in milliseconds or ISO format.

    Args:
        iso_format: If True, return ISO format string, otherwise return milliseconds

    Returns:
        int | str: Timestamp in milliseconds or ISO format
    """
    return _native.generate_timestamp_iso() if iso_format else _native.generate_timestamp_ms()


def config_logging(
    logging_module: LoggingModuleProtocol, logging_level: int | str, log_file: str | None = None
) -> None:
    """
    Configures logging with UTC timestamp and optional daily rotating log files.

    Example log format:
        2025-03-07 19:42:04.849 UTC DEBUG my_logger: Log message

    Args:
        logging_module: Python logging module
        logging_level: Log level (e.g., 10 for DEBUG, 20 for INFO)
        log_file: Base filename for logs (e.g., "my_log.log").
                 If provided, logs will rotate daily.
    """

    # Set UTC time format
    import time

    logging_module.Formatter.converter = time.gmtime

    # Define log format
    log_format = "%(asctime)s.%(msecs)03d UTC %(levelname)s %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Create log formatter
    formatter = logging_module.Formatter(fmt=log_format, datefmt=date_format)

    # Configure logging to console
    logging_module.basicConfig(level=logging_level, format=log_format, datefmt=date_format)

    # If a log file is provided, enable daily log rotation
    if log_file:
        log_dir = os.path.dirname(log_file) or "."  # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)

        # Create a rotating file handler (daily rotation)
        file_handler = TimedRotatingFileHandler(
            filename=log_file,  # This will be the base filename
            when="midnight",  # Rotate at midnight
            interval=1,  # Rotate every 1 day
            backupCount=30,  # Keep the last 7 days of logs
            encoding="utf-8",  # Support Unicode logs
            utc=True,  # Use UTC for time-based rotation
        )

        file_handler.setFormatter(formatter)
        file_handler.suffix = "%Y-%m-%d"  # Filename suffix pattern
        logging_module.getLogger().addHandler(file_handler)
