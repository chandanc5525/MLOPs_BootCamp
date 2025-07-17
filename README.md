# MLOPs_BootCamp

## Folder Structure for Efficient Pipeline of our Project:

The .github/workflows/ folder holds CI/CD pipeline configurations, with a .gitkeep file to ensure the folder is tracked even if empty. The src/ directory contains the main source code and is marked as a Python package by the __init__.py file. Inside src/components/ are the key ML pipeline building blocks: data_ingestion.py for loading and preparing raw data, data_transformation.py for cleaning and transforming data, model_trainer.py for training machine learning models, and model_evaluation.py for evaluating those models. The src/pipeline/ folder contains orchestration scripts, including training_pipeline.py for running the full training workflow and prediction_pipeline.py for making predictions. The src/utils/ folder provides reusable helper functions defined in utils.py. Logging is centrally configured in src/logger/logging.py, and custom exceptions are defined in src/exception/exception.py.

The tests/ folder contains unit and integration tests, with separate subfolders for each type. The init_setup.sh script initializes a virtual environment and installs dependencies. The requirements.txt and requirements_dev.txt files specify production and development dependencies respectively. Packaging and installation metadata and configuration are handled by setup.py, setup.cfg, and pyproject.toml, while tox.ini automates testing across environments. Finally, experiment/experiments.ipynb is a Jupyter notebook for running experiments and prototyping research ideas.

