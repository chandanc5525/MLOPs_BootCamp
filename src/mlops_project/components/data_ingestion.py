"""
Stage 1 - Data Ingestion

PURPOSE:
  Get raw data from its source (local file, S3, an API, a database export...)
  into a single, predictable location: artifacts/data_ingestion/raw_data.csv.

LOGIC:
  In this bootcamp the "source" is a local CSV (data/raw/air_quality.csv) to
  keep the project runnable without external credentials. In a real company
  setup you would swap `_load_source()` for a call to S3 / a warehouse query
  / an API client - nothing downstream needs to change because every other
  stage only ever talks to `raw_data_file`, never to the original source.
"""

import shutil
import pandas as pd

from src.mlops_project.entity.config_entity import DataIngestionConfig
from src.mlops_project.logger import get_logger
from src.mlops_project.exception import CustomException

logger = get_logger(__name__)


class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def _load_source(self) -> pd.DataFrame:
        """Read the raw dataset from its source path."""
        return pd.read_csv(self.config.source_path)

    def ingest(self) -> str:
        try:
            logger.info("Starting data ingestion")
            df = self._load_source()
            df.to_csv(self.config.raw_data_file, index=False)
            logger.info(
                f"Ingested {df.shape[0]} rows / {df.shape[1]} columns "
                f"into {self.config.raw_data_file}"
            )
            return self.config.raw_data_file
        except Exception as e:
            raise CustomException(e)
