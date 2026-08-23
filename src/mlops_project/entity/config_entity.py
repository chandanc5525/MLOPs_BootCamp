"""
Entity classes = typed, immutable "contracts" for what configuration each
pipeline stage needs.

WHY: Instead of passing around raw dictionaries (config["data_ingestion"]["x"])
which give no autocomplete and fail silently on typos, every stage receives a
frozen dataclass with named, typed fields. If a field is missing/misnamed,
you get an error immediately at object-construction time, not deep inside
training after 10 minutes of AutoGluon fitting.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataIngestionConfig:
    root_dir: Path
    source_path: Path
    raw_data_file: Path


@dataclass(frozen=True)
class DataValidationConfig:
    root_dir: Path
    raw_data_file: Path
    status_file: Path
    all_schema: dict


@dataclass(frozen=True)
class DataTransformationConfig:
    root_dir: Path
    raw_data_file: Path
    train_data_file: Path
    test_data_file: Path
    test_size: float


@dataclass(frozen=True)
class ModelTrainerConfig:
    root_dir: Path
    train_data_file: Path
    model_dir: Path
    model_pkl_file: Path
    target_column: str
    presets: str
    time_limit: int
    eval_metric: str


@dataclass(frozen=True)
class ModelEvaluationConfig:
    root_dir: Path
    test_data_file: Path
    model_pkl_file: Path
    metric_file: Path
    target_column: str
    mlflow_uri: str
    min_r2_threshold: float
