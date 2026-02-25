from __future__ import annotations

import logging
import sys
from typing import Any


def configure_logging(level: str = "INFO") -> None:
    """
    Configure structured JSON logging for the application.

    Sets up the root logger to emit JSON-formatted log records to stdout.
    Call once at application startup (e.g., in app/main.py lifespan).

    Args:
        level: Logging level string — "DEBUG", "INFO", "WARNING", "ERROR".
    """
    # TODO: Implement structured JSON logging.
    # Recommended approach: use `python-json-logger` (pythonjsonlogger.jsonlogger.JsonFormatter)
    # or a manual Formatter that emits {"timestamp": ..., "level": ..., "name": ..., "message": ...}.
    #
    # Example (requires pip install python-json-logger):
    #   from pythonjsonlogger import jsonlogger
    #   handler = logging.StreamHandler(sys.stdout)
    #   handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    #   logging.root.handlers = [handler]
    #   logging.root.setLevel(level)

    # Fallback: basic human-readable logging (replace with JSON formatter above)
    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Use in place of `logging.getLogger(__name__)`."""
    return logging.getLogger(name)
