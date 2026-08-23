"""
Stage 5 - Model Evaluation

PURPOSE:
  1. Load the pickled model artifact + held-out test set.
  2. Compute metrics (R2, MAE, RMSE for this regression use case).
  3. Log the run (params + metrics + the model itself) to MLflow, so every
     training run is comparable in the MLflow UI / Model Registry.
  4. Apply the "Quality Gate" from the architecture diagram: if the new
     model's R2 doesn't beat `min_r2_threshold` (params.yaml), evaluation
     reports FAIL, and the CI/CD workflow stops the model from being
     promoted to the Staging/FastAPI stage - it lands back on "Retrain"
     instead of silently entering production.
"""

import json
import pandas as pd
import mlflow
import mlflow.pyfunc
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np

from src.mlops_project.entity.config_entity import ModelEvaluationConfig
from src.mlops_project.utils.common import load_pickle, save_json
from src.mlops_project.logger import get_logger
from src.mlops_project.exception import CustomException

logger = get_logger(__name__)


class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config

    def evaluate(self) -> dict:
        try:
            test_df = pd.read_csv(self.config.test_data_file)
            y_true = test_df[self.config.target_column]
            X_test = test_df.drop(columns=[self.config.target_column])

            predictor = load_pickle(self.config.model_pkl_file)
            y_pred = predictor.predict(X_test)

            metrics = {
                "r2_score": float(r2_score(y_true, y_pred)),
                "mae": float(mean_absolute_error(y_true, y_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            }

            passed_gate = metrics["r2_score"] >= self.config.min_r2_threshold
            metrics["quality_gate_passed"] = passed_gate
            metrics["min_r2_threshold"] = self.config.min_r2_threshold

            save_json(self.config.metric_file, metrics)
            logger.info(f"Evaluation metrics: {metrics}")

            # --- MLflow experiment tracking + registry ---
            mlflow.set_tracking_uri(self.config.mlflow_uri)
            mlflow.set_experiment("autogluon-air-quality")
            with mlflow.start_run():
                mlflow.log_metric("r2_score", metrics["r2_score"])
                mlflow.log_metric("mae", metrics["mae"])
                mlflow.log_metric("rmse", metrics["rmse"])
                mlflow.log_param("quality_gate_passed", passed_gate)
                mlflow.log_artifact(str(self.config.model_pkl_file))
                if passed_gate:
                    logger.info("Quality gate PASSED -> eligible for Staging")
                else:
                    logger.warning("Quality gate FAILED -> flagged for Retrain")

            return metrics
        except Exception as e:
            raise CustomException(e)
