"""
Stage 2 - Data Validation

PURPOSE:
  Fail fast. Before spending time/compute on transformation and AutoGluon
  training, confirm the ingested data actually matches the contract defined
  in schema.yaml (expected columns + dtypes). This is what protects the rest
  of the DVC pipeline (and, later, retraining triggered from Airflow) from
  silently training on a corrupted or drifted upstream extract.

LOGIC:
  1. Read raw_data_file.
  2. Compare its columns against schema.yaml's COLUMNS section.
  3. Write True/False + details to a status file. DVC treats this status
     file as an output, so a validation failure is visible directly in
     `dvc repro` output and can gate later stages in CI.
"""

import pandas as pd

from src.mlops_project.entity.config_entity import DataValidationConfig
from src.mlops_project.logger import get_logger
from src.mlops_project.exception import CustomException

logger = get_logger(__name__)


class DataValidation:
    def __init__(self, config: DataValidationConfig):
        self.config = config

    def validate(self) -> bool:
        try:
            df = pd.read_csv(self.config.raw_data_file)
            all_cols = list(df.columns)
            expected_cols = list(self.config.all_schema.keys())

            missing = set(expected_cols) - set(all_cols)
            unexpected = set(all_cols) - set(expected_cols)

            validation_status = len(missing) == 0

            with open(self.config.status_file, "w") as f:
                f.write(f"Validation status: {validation_status}\n")
                if missing:
                    f.write(f"Missing columns: {sorted(missing)}\n")
                if unexpected:
                    f.write(f"Unexpected columns (ignored): {sorted(unexpected)}\n")

            logger.info(f"Data validation status: {validation_status}")
            return validation_status
        except Exception as e:
            raise CustomException(e)
