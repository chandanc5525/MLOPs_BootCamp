"""
Local training-pipeline entrypoint.

Runs all 5 stages sequentially, exactly like `dvc repro` would, but without
needing DVC installed - handy for a quick local smoke test:

    python main.py
"""

from src.mlops_project.logger import get_logger
from src.mlops_project.pipeline import (
    stage_01_data_ingestion,
    stage_02_data_validation,
    stage_03_data_transformation,
    stage_04_model_trainer,
    stage_05_model_evaluation,
)

logger = get_logger(__name__)

STAGES = [
    ("Data Ingestion", stage_01_data_ingestion.main),
    ("Data Validation", stage_02_data_validation.main),
    ("Data Transformation", stage_03_data_transformation.main),
    ("Model Trainer (AutoGluon)", stage_04_model_trainer.main),
    ("Model Evaluation", stage_05_model_evaluation.main),
]

if __name__ == "__main__":
    for name, stage_fn in STAGES:
        logger.info(f">>>>>> stage {name} started <<<<<<")
        stage_fn()
        logger.info(f">>>>>> stage {name} completed <<<<<<\n\nx==========x")
