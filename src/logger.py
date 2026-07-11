"""Logging configuration for Agnes Mini."""

from __future__ import annotations

import logging
import sys

from src.config import get_settings


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: The logger name, typically ``__name__``.

    Returns:
        A logger configured with the application-wide log level and format.
    """
    settings = get_settings()
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
        logger.propagate = False

    return logger
