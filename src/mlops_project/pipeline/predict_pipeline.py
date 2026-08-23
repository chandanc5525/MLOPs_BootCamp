"""
Inference pipeline used by the FastAPI app (app/main.py).

PURPOSE:
  Keep "how do I load the model + turn a request into a prediction" in one
  place, independent of FastAPI, so it can also be unit-tested or reused
  from a CLI / batch-scoring script.
"""

import pandas as pd

from src.mlops_project.utils.common import load_pickle
from src.mlops_project.logger import get_logger
from src.mlops_project.exception import CustomException

logger = get_logger(__name__)


class PredictionPipeline:
    def __init__(self, model_pkl_path: str):
        self.model = load_pickle(model_pkl_path)

    def predict(self, input_dict: dict) -> float:
        try:
            input_df = pd.DataFrame([input_dict])
            prediction = self.model.predict(input_df)
            return float(prediction.iloc[0])
        except Exception as e:
            raise CustomException(e)
