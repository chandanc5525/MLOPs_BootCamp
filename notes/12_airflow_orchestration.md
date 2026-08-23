# 12 — Orchestration with Airflow

**File:** `dags/air_quality_training_dag.py`

## Purpose

GitHub Actions answers "when code changes, retrain and redeploy." Airflow
answers the *other* trigger in your diagram: **scheduled** retraining
(`@weekly` here) and retraining **triggered by production monitoring**
(drift/performance alerts — see `13_monitoring_and_retraining.md`),
independent of anyone pushing code.

## Why you need both CI/CD *and* Airflow

- **GitHub Actions** reacts to *code* changes.
- **Airflow** reacts to *time* (schedule) and *data/production signals*
  (drift, degraded performance) — situations where the code hasn't changed
  at all, but the model still needs to be refreshed on new data.

Both ultimately call the same underlying command — `dvc repro` — so
training logic is defined exactly once (in `dvc.yaml`) and orchestrated
from two different triggers.

## DAG structure

```python
data_ingestion >> data_validation >> data_transformation >> model_trainer >> model_evaluation
                                                                            >> quality_gate
quality_gate >> [promote_to_staging, flag_for_retrain]   # BranchPythonOperator
```

Each task is a `BashOperator` running `dvc repro <stage_name>` inside the
project directory mounted into the Airflow worker (`/opt/airflow/project`
in the example — adjust to your Airflow deployment's volume mounts).

`quality_gate` is a `BranchPythonOperator` that reads the same
`metrics.json` used by CI (`13_monitoring_and_retraining.md` covers what
happens on the FAIL path in production):

```python
def _check_quality_gate(**context):
    metrics = json.load(open(".../artifacts/model_evaluation/metrics.json"))
    return "promote_to_staging" if metrics["quality_gate_passed"] else "flag_for_retrain"
```

## Installing this DAG

1. Copy `dags/air_quality_training_dag.py` into your Airflow instance's
   `dags/` folder (or mount this repo's `dags/` directory as Airflow's DAGs
   folder).
2. Make sure the project itself (code + a `dvc`-initialized repo, with
   remote credentials configured if you use `dvc pull`) is available at the
   path referenced by `params={"project_dir": ...}` inside the worker
   container/environment.
3. Airflow needs its own Python environment with `dvc`, `pandas`,
   `autogluon.tabular`, etc. installed (or the `BashOperator` calls could
   instead run inside a dedicated Docker/K8s pod via
   `DockerOperator`/`KubernetesPodOperator` for stronger isolation from
   Airflow's own dependencies — recommended for a real deployment, since
   Airflow and AutoGluon can have conflicting pinned dependencies).

## Triggering a retrain outside the schedule

From monitoring/alerting (see next note) or manually:

```bash
airflow dags trigger air_quality_autogluon_training_pipeline
```

`promote_to_staging`'s current body is a placeholder that documents the
next real step — calling GitHub's `repository_dispatch` API (or another
CI trigger) so the `build-and-push-image` job in `ci-cd.yaml` picks up the
freshly-approved model.
