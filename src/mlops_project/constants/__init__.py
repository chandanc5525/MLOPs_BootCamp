"""
Central place for every file path constant used in the pipeline.

WHY: hard-coding "config/config.yaml" in five different files means a rename
requires five edits and is an easy way to introduce a bug. Every component
imports paths from here instead.
"""

from pathlib import Path

CONFIG_FILE_PATH = Path("config/config.yaml")
PARAMS_FILE_PATH = Path("params.yaml")
SCHEMA_FILE_PATH = Path("schema.yaml")
