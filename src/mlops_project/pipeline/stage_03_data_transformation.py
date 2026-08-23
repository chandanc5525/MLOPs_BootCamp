from src.mlops_project.config.configuration import ConfigurationManager
from src.mlops_project.components.data_transformation import DataTransformation
from src.mlops_project.logger import get_logger

logger = get_logger(__name__)
STAGE_NAME = "Data Transformation"


def main():
    config = ConfigurationManager().get_data_transformation_config()
    DataTransformation(config).transform()


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        main()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
