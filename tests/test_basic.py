"""
Minimal smoke tests - run in CI before the (slow) DVC/AutoGluon pipeline.
These deliberately don't train a model; they check that config loading and
schema/entity wiring work, which catches most "I renamed a yaml key"
mistakes in seconds instead of after a 2-minute AutoGluon run.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mlops_project.config.configuration import ConfigurationManager


def test_config_loads():
    cm = ConfigurationManager()
    assert cm.config.artifacts_root == "artifacts"


def test_data_ingestion_config():
    cm = ConfigurationManager()
    cfg = cm.get_data_ingestion_config()
    assert str(cfg.source_path).endswith("air_quality.csv")


def test_schema_has_target_column():
    cm = ConfigurationManager()
    assert cm.schema.TARGET_COLUMN.name == "AQI"


def test_model_trainer_config_reads_autogluon_params():
    cm = ConfigurationManager()
    cfg = cm.get_model_trainer_config()
    assert cfg.presets in ("medium_quality", "good_quality", "best_quality", "high_quality")
    assert cfg.time_limit > 0
