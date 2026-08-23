"""
ConfigurationManager: the single bridge between YAML files
(config.yaml / params.yaml / schema.yaml) and the typed entity dataclasses
each pipeline stage consumes.

WHY this indirection exists:
  config.yaml   -> WHERE things live (paths, directories)
  params.yaml   -> HOW training behaves (AutoGluon presets, time_limit, etc.)
  schema.yaml   -> WHAT the data must look like (column names/dtypes)

Keeping these three concerns in three files (instead of one big config)
means a data scientist can tune params.yaml for a new experiment without
touching paths, and DVC can track params.yaml separately to know when a
pipeline stage needs to re-run because a *parameter* changed.
"""

from src.mlops_project.constants import (
    CONFIG_FILE_PATH,
    PARAMS_FILE_PATH,
    SCHEMA_FILE_PATH,
)
from src.mlops_project.utils.common import read_yaml, create_directories
from src.mlops_project.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    ModelEvaluationConfig,
)


class ConfigurationManager:
    def __init__(
        self,
        config_filepath=CONFIG_FILE_PATH,
        params_filepath=PARAMS_FILE_PATH,
        schema_filepath=SCHEMA_FILE_PATH,
    ):
        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)
        self.schema = read_yaml(schema_filepath)

        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        cfg = self.config.data_ingestion
        create_directories([cfg.root_dir])
        return DataIngestionConfig(
            root_dir=cfg.root_dir,
            source_path=cfg.source_path,
            raw_data_file=cfg.raw_data_file,
        )

    def get_data_validation_config(self) -> DataValidationConfig:
        cfg = self.config.data_validation
        create_directories([cfg.root_dir])
        return DataValidationConfig(
            root_dir=cfg.root_dir,
            raw_data_file=cfg.raw_data_file,
            status_file=cfg.status_file,
            all_schema=self.schema.COLUMNS,
        )

    def get_data_transformation_config(self) -> DataTransformationConfig:
        cfg = self.config.data_transformation
        create_directories([cfg.root_dir])
        return DataTransformationConfig(
            root_dir=cfg.root_dir,
            raw_data_file=cfg.raw_data_file,
            train_data_file=cfg.train_data_file,
            test_data_file=cfg.test_data_file,
            test_size=self.params.data_transformation.test_size,
        )

    def get_model_trainer_config(self) -> ModelTrainerConfig:
        cfg = self.config.model_trainer
        create_directories([cfg.root_dir])
        return ModelTrainerConfig(
            root_dir=cfg.root_dir,
            train_data_file=cfg.train_data_file,
            model_dir=cfg.model_dir,
            model_pkl_file=cfg.model_pkl_file,
            target_column=self.schema.TARGET_COLUMN.name,
            presets=self.params.autogluon.presets,
            time_limit=self.params.autogluon.time_limit,
            eval_metric=self.params.autogluon.eval_metric,
        )

    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        cfg = self.config.model_evaluation
        create_directories([cfg.root_dir])
        return ModelEvaluationConfig(
            root_dir=cfg.root_dir,
            test_data_file=cfg.test_data_file,
            model_pkl_file=cfg.model_pkl_file,
            metric_file=cfg.metric_file,
            target_column=self.schema.TARGET_COLUMN.name,
            mlflow_uri=self.params.mlflow.tracking_uri,
            min_r2_threshold=self.params.quality_gate.min_r2_threshold,
        )
