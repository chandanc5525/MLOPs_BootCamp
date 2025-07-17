import os
from pathlib import Path

project_name = input("Enter your project name: ")

list_of_files = [
    f"{project_name}/.github/workflows/.gitkeep",
    f"{project_name}/src/__init__.py",
    f"{project_name}/src/components/__init__.py",
    f"{project_name}/src/components/data_ingestion.py",
    f"{project_name}/src/components/data_transformation.py",
    f"{project_name}/src/components/model_trainer.py",
    f"{project_name}/src/components/model_evaluation.py",
    f"{project_name}/src/pipeline/__init__.py",
    f"{project_name}/src/pipeline/training_pipeline.py",
    f"{project_name}/src/pipeline/prediction_pipeline.py",
    f"{project_name}/src/utils/__init__.py",
    f"{project_name}/src/utils/utils.py",
    f"{project_name}/src/logger/logging.py",
    f"{project_name}/src/exception/exception.py",
    f"{project_name}/tests/unit/__init__.py",
    f"{project_name}/tests/integration/__init__.py",
    f"{project_name}/init_setup.sh",
    f"{project_name}/requirements.txt",
    f"{project_name}/requirements_dev.txt",
    f"{project_name}/setup.py",
    f"{project_name}/setup.cfg",
    f"{project_name}/pyproject.toml",
    f"{project_name}/tox.ini",
    f"{project_name}/experiment/experiments.ipynb"
]


for file in list_of_files:
    path = Path(file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

print(f"Project '{project_name}' structure created successfully!")
