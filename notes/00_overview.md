# 00 — Project Overview

## What this project is

An end-to-end **MLOps bootcamp project**: predicting Air Quality Index (AQI)
from pollutant + weather readings, using **AutoGluon** as the modeling
engine, wired into a full production-style MLOps loop:

```
GitHub → GitHub Actions (CI/CD) → Airflow (orchestration) → DVC (data + ML pipeline)
      → [Data Validation → Preprocess → Train → Evaluate] → MLflow (tracking + registry)
      → Quality Gate → (PASS) Staging → FastAPI → Docker → Production
                     → (FAIL) Retrain
      → Production → Logging / Data Drift / Performance → Alerting → Airflow → Retrain
```

This matches, stage for stage, the architecture diagram you provided. Each
box in that diagram maps to a concrete file in this repo — see the table in
`01_project_structure.md`.

## Why each tool is there

| Tool | Role | Why not skip it |
|---|---|---|
| **GitHub** | source of truth for code | version control, PR review, audit trail |
| **GitHub Actions** | CI/CD | runs tests + pipeline + builds/pushes Docker image automatically on every push |
| **Airflow** | orchestration / scheduling | runs the DVC pipeline on a schedule and reacts to drift/alerts, independent of a person clicking "run" |
| **DVC** | data + pipeline versioning | makes each stage cacheable/reproducible and data itself version-controlled (large files never go into git) |
| **AutoGluon** | model training | strong baseline model with automatic model selection/ensembling — the bootcamp's ML engine |
| **MLflow** | experiment tracking + model registry | every run's params/metrics/artifacts are logged and comparable; enables the "Quality Gate" decision |
| **FastAPI** | model serving | typed, auto-documented REST API for real-time inference |
| **Docker** | packaging | the exact same environment runs the same way locally, in CI, and in production |

## How to read the rest of this Notes/ folder

Read the files in numeric order — each one is a step in the pipeline, and
later files assume you understand the concepts introduced earlier:

1. `01_project_structure.md` — full folder/file map + what each piece does
2. `02_data_ingestion.md`
3. `03_data_validation.md`
4. `04_data_transformation.md`
5. `05_model_training_autogluon.md`
6. `06_model_evaluation.md`
7. `07_dvc_pipeline.md`
8. `08_mlflow_tracking.md`
9. `09_fastapi_serving.md`
10. `10_docker.md`
11. `11_cicd_github_actions.md`
12. `12_airflow_orchestration.md`
13. `13_monitoring_and_retraining.md`

## Quickstart

```bash
# 1. Create env + install deps (you said AutoGluon is already installed)
pip install -r requirements.txt
pip install -e .

# 2. (Optional) regenerate the synthetic demo dataset
python scripts_generate_sample_data.py

# 3. Run the whole pipeline with plain Python
python main.py

# --- OR, the DVC way (recommended, gives caching + a reproducible DAG) ---
dvc init                 # once, first time
dvc repro                # runs every stage in dvc.yaml, skipping unchanged ones
dvc dag                  # visualize the pipeline graph
dvc metrics show         # see the latest R2/MAE/RMSE

# 4. Serve the trained model
uvicorn app.main:app --reload --port 8000
# open http://localhost:8000/docs

# 5. Or run it all in Docker
docker compose up --build
```
