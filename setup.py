"""
Makes `src.mlops_project` pip-installable (`pip install -e .`) so that
`import src.mlops_project...` works the same way locally, in CI, and inside
the Docker image, without fragile sys.path hacks.
"""

from setuptools import setup, find_packages

setup(
    name="mlops_autogluon_bootcamp",
    version="1.0.0",
    description="End-to-end MLOps bootcamp project: AutoGluon + DVC + MLflow + FastAPI + Docker",
    author="MLOps Bootcamp",
    packages=find_packages(include=["src", "src.*"]),
    python_requires=">=3.10",
)
