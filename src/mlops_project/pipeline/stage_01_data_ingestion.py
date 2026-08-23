"""
DVC calls this file for the 'data_ingestion' stage (see dvc.yaml).
Kept as a thin script: all real logic lives in components/data_ingestion.py
so it's unit-testable without invoking DVC or reading yaml files.
"""

from src.mlops_project.config.configuration import ConfigurationManager
from src.mlops_project.components.data_ingestion import DataIngestion
from src.mlops_project.logger import get_logger

logger = get_logger(__name__)
STAGE_NAME = "Data Ingestion"


def main():
    config = ConfigurationManager().get_data_ingestion_config()
    DataIngestion(config).ingest()


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        main()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
