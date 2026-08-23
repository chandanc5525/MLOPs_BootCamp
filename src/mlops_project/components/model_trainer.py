"""
Stage 4 - Model Training (AutoGluon)

PURPOSE:
  Train an AutoGluon TabularPredictor on the training split and persist it
  as the pipeline's model ARTIFACT - a .pkl file - which is what the FastAPI
  service and model_evaluation.py load later.

WHY AutoGluon:
  AutoGluon's TabularPredictor automatically tries multiple model families
  (LightGBM, CatBoost, XGBoost, Random Forest, neural nets) and ensembles
  them, so we get strong baseline performance without hand-tuning individual
  algorithms - ideal for an MLOps bootcamp where the *pipeline* is the
  teaching focus, not manual model selection.

ARTIFACT STRATEGY (important):
  AutoGluon predictors already persist themselves as a directory
  (model_dir/) via `predictor.save()` - that directory contains its own
  internal state and is the format AutoGluon itself recommends for
  `TabularPredictor.load()`. On top of that, per this project's requirement
  that "artifact is a file where a pickle file must get stored", we ALSO
  pickle.dump() the fitted predictor object into a single `model.pkl` file.
  DVC tracks model.pkl as the canonical training-stage output, and the
  FastAPI app loads *that* file directly with pickle.load(), so serving
  never needs to know AutoGluon's internal directory layout.
"""

import pandas as pd
from autogluon.tabular import TabularPredictor

from src.mlops_project.entity.config_entity import ModelTrainerConfig
from src.mlops_project.utils.common import save_pickle
from src.mlops_project.logger import get_logger
from src.mlops_project.exception import CustomException

logger = get_logger(__name__)


class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def train(self):
        try:
            train_df = pd.read_csv(self.config.train_data_file)

            logger.info(
                f"Starting AutoGluon training | target={self.config.target_column} "
                f"presets={self.config.presets} time_limit={self.config.time_limit}s"
            )

            predictor = TabularPredictor(
                label=self.config.target_column,
                path=self.config.model_dir,
                eval_metric=self.config.eval_metric,
            ).fit(
                train_data=train_df,
                presets=self.config.presets,
                time_limit=self.config.time_limit,
            )

            leaderboard = predictor.leaderboard(silent=True)
            logger.info(f"AutoGluon leaderboard (top 5):\n{leaderboard.head()}")

            # Canonical pickle artifact consumed by evaluation + FastAPI.
            save_pickle(self.config.model_pkl_file, predictor)

            logger.info(f"Model artifact saved to {self.config.model_pkl_file}")
            return self.config.model_pkl_file
        except Exception as e:
            raise CustomException(e)
