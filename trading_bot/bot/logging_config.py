"""Logging configuration for console diagnostics and rotating log files."""

from logging.handlers import RotatingFileHandler
from pathlib import Path
import logging

from bot.config import LOG_DIR


LOGGER_NAME = "trading_bot"


def configure_logging(log_dir: Path = LOG_DIR) -> logging.Logger:
    """Configure and return the application logger."""

    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_dir / "trading_bot.log",
        maxBytes=1_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    """Return the configured application logger."""

    return configure_logging()
