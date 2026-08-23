"""
Stage 3 - Data Transformation

PURPOSE:
  Produce the train/test split that model_trainer.py and model_evaluation.py
  consume. Deliberately kept "light" here: AutoGluon does its own internal
  preprocessing (imputation, encoding, scaling) during .fit(), so this stage
  focuses only on what AutoGluon does NOT do for you - cleaning obviously
  broken rows and creating a held-out test set DVC can track and hash.

  Doing the split as its own DVC-tracked stage (instead of inside training)
  means the exact same test set is reused across retraining runs, so model
  evaluation metrics stay comparable over time.
"""

import pandas as pd
from sklearn.model_selection import train_test_split

from src.mlops_project.entity.config_entity import DataTransformationConfig
from src.mlops_project.logger import get_logger
from src.mlops_project.exception import CustomException

logger = get_logger(__name__)


class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config

    def transform(self):
        try:
            df = pd.read_csv(self.config.raw_data_file)

            before = df.shape[0]
            df = df.dropna(how="all")
            df = df.drop_duplicates()
            logger.info(f"Dropped {before - df.shape[0]} empty/duplicate rows")

            train_df, test_df = train_test_split(
                df, test_size=self.config.test_size, random_state=42
            )

            train_df.to_csv(self.config.train_data_file, index=False)
            test_df.to_csv(self.config.test_data_file, index=False)

            logger.info(
                f"Split data -> train: {train_df.shape}, test: {test_df.shape}"
            )
            return self.config.train_data_file, self.config.test_data_file
        except Exception as e:
            raise CustomException(e)
