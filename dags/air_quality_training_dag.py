"""
Airflow DAG - orchestrates the DVC pipeline on a schedule and reacts to
monitoring signals, matching the diagram's:
    Airflow Orchestration -> DVC Pipeline -> ... -> Airflow -> Retrain loop.

Two ways this DAG gets triggered:
  1. Scheduled (@daily / @weekly) - routine retraining on fresh data.
  2. Externally triggered by the monitoring/alerting stage (see
     notes/13_monitoring_and_retraining.md) when data drift or performance
     degradation is detected in production.

Drop this file into your Airflow `dags/` folder. Each task simply shells out
to `dvc repro <stage>`, so Airflow orchestrates *when* stages run while DVC
still owns *caching + dependency graph* for each stage.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    "owner": "mlops-bootcamp",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="air_quality_autogluon_training_pipeline",
    description="DVC-orchestrated AutoGluon training pipeline with MLflow quality gate",
    default_args=default_args,
    schedule="@weekly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["mlops", "autogluon", "air-quality"],
) as dag:

    data_ingestion = BashOperator(
        task_id="data_ingestion",
        bash_command="cd {{ params.project_dir }} && dvc repro data_ingestion",
        params={"project_dir": "/opt/airflow/project"},
    )

    data_validation = BashOperator(
        task_id="data_validation",
        bash_command="cd {{ params.project_dir }} && dvc repro data_validation",
        params={"project_dir": "/opt/airflow/project"},
    )

    data_transformation = BashOperator(
        task_id="data_transformation",
        bash_command="cd {{ params.project_dir }} && dvc repro data_transformation",
        params={"project_dir": "/opt/airflow/project"},
    )

    model_trainer = BashOperator(
        task_id="model_trainer",
        bash_command="cd {{ params.project_dir }} && dvc repro model_trainer",
        params={"project_dir": "/opt/airflow/project"},
    )

    model_evaluation = BashOperator(
        task_id="model_evaluation",
        bash_command="cd {{ params.project_dir }} && dvc repro model_evaluation",
        params={"project_dir": "/opt/airflow/project"},
    )

    def _check_quality_gate(**context):
        import json

        with open("/opt/airflow/project/artifacts/model_evaluation/metrics.json") as f:
            metrics = json.load(f)
        return "promote_to_staging" if metrics["quality_gate_passed"] else "flag_for_retrain"

    quality_gate = BranchPythonOperator(
        task_id="quality_gate",
        python_callable=_check_quality_gate,
    )

    promote_to_staging = BashOperator(
        task_id="promote_to_staging",
        bash_command=(
            "echo 'Quality gate passed - triggering CI/CD build-and-push-image job "
            "(e.g. via GitHub Actions repository_dispatch API call)'"
        ),
    )

    flag_for_retrain = EmptyOperator(task_id="flag_for_retrain")

    (
        data_ingestion
        >> data_validation
        >> data_transformation
        >> model_trainer
        >> model_evaluation
        >> quality_gate
        >> [promote_to_staging, flag_for_retrain]
    )
