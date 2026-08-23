from src.mlops_project.config.configuration import ConfigurationManager
from src.mlops_project.components.data_validation import DataValidation
from src.mlops_project.logger import get_logger

logger = get_logger(__name__)
STAGE_NAME = "Data Validation"


def main():
    config = ConfigurationManager().get_data_validation_config()
    status = DataValidation(config).validate()
    if not status:
        raise ValueError(
            "Data validation failed - schema mismatch. See status file for details."
        )


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        main()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
