from src.mlops_project.config.configuration import ConfigurationManager
from src.mlops_project.components.model_trainer import ModelTrainer
from src.mlops_project.logger import get_logger

logger = get_logger(__name__)
STAGE_NAME = "Model Trainer (AutoGluon)"


def main():
    config = ConfigurationManager().get_model_trainer_config()
    ModelTrainer(config).train()


if __name__ == "__main__":
    try:
        logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        main()
        logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logger.exception(e)
        raise e
