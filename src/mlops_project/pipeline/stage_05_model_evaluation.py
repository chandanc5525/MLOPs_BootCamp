from src.mlops_project.config.configuration import ConfigurationManager
from src.mlops_project.components.model_evaluation import ModelEvaluation
from src.mlops_project.logger import get_logger

logger = get_logger(__name__)
STAGE_NAME = "Model Evaluation"


def main():
    config = ConfigurationManager().get_model_evaluation_config()
    ModelEvaluation(config).evaluate()


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        main()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
