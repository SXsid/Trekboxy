"""
Centralized logging configuration for HimTrek backend.

Usage in any module:
    from logger import get_logger
    logger = get_logger(__name__)

    logger.info("Something happened")
    logger.warning("Something looks off")
    logger.error("Something failed")
    logger.exception("Unexpected error", exc_info=True)  # includes traceback
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Rotate after 5 MB, keep last 5 files
MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 5

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ---------------------------------------------------------------------------
# Setup (called once at app startup)
# ---------------------------------------------------------------------------

def setup_logging(log_level: str = "INFO") -> None:
    """Configure the root logger with a rotating file handler and console handler.

    Call this once inside create_app() before anything else logs.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # --- rotating file handler ------------------------------------------------
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # --- console handler (dev-friendly coloured output) -----------------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # --- root logger ----------------------------------------------------------
    root = logging.getLogger()
    root.setLevel(level)

    # Avoid adding duplicate handlers if setup_logging() is called again
    if not root.handlers:
        root.addHandler(file_handler)
        root.addHandler(console_handler)

    # Silence noisy third-party loggers
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger.  Call at module level:

        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
