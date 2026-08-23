"""
Generic, reusable helper functions.

WHY a separate utils module: components (data_ingestion.py, model_trainer.py,
etc.) should focus on *pipeline logic*, not on boilerplate like "how do I
safely read a YAML file" or "how do I make sure a directory exists". Pulling
these into one place means every component behaves identically and bugs only
need to be fixed once.
"""

import os
import pickle
import json
from pathlib import Path
from typing import Any

import yaml
from box import ConfigBox  # python-box: lets us do config.key instead of config["key"]

from src.mlops_project.exception import CustomException
from src.mlops_project.logger import get_logger

logger = get_logger(__name__)


def read_yaml(path_to_yaml: Path) -> ConfigBox:
    """Read a yaml file and return a ConfigBox (dot-accessible dict)."""
    try:
        with open(path_to_yaml, "r") as f:
            content = yaml.safe_load(f)
            logger.info(f"yaml file: {path_to_yaml} loaded successfully")
            return ConfigBox(content)
    except Exception as e:
        raise CustomException(e)


def create_directories(path_list: list, verbose: bool = True) -> None:
    """Create a list of directories if they don't already exist."""
    for path in path_list:
        os.makedirs(path, exist_ok=True)
        if verbose:
            logger.info(f"created directory at: {path}")


def save_json(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    logger.info(f"json file saved at: {path}")


def load_json(path: Path) -> ConfigBox:
    with open(path, "r") as f:
        content = json.load(f)
    logger.info(f"json file loaded succesfully from: {path}")
    return ConfigBox(content)


def save_pickle(path: Path, obj: Any) -> None:
    """
    Persist any Python object (here: the trained AutoGluon predictor wrapper)
    as a .pkl artifact. This is the file the FastAPI app later loads for
    inference, and the file DVC tracks as the pipeline's model artifact.
    """
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    logger.info(f"pickle artifact saved at: {path}")


def load_pickle(path: Path) -> Any:
    with open(path, "rb") as f:
        obj = pickle.load(f)
    logger.info(f"pickle artifact loaded from: {path}")
    return obj


def get_size(path: Path) -> str:
    """Return file size in KB as a readable string."""
    size_in_kb = round(os.path.getsize(path) / 1024)
    return f"~ {size_in_kb} KB"
