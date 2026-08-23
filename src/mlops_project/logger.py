"""
Centralized logging setup for the project.

WHY: Every component (data ingestion, validation, training, FastAPI app,
Airflow tasks) imports this single logger so that:
  1. Log format/behavior is consistent everywhere.
  2. Logs are written both to console (for local/dev/CI visibility) and to a
     timestamped file under logs/ (for later debugging / audit trail).
  3. We avoid re-configuring logging.basicConfig() in multiple places, which
     can silently break logging if done more than once in a process.
"""

import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d')}.log"
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
)
console_handler.setFormatter(console_formatter)

logging.getLogger().addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger, e.g. get_logger(__name__)."""
    return logging.getLogger(name)
