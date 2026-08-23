# MLOps Bootcamp 
## MLModel  : Air Quality Index Prediction Model 

An end-to-end MLOps project: **AutoGluon** for modeling, **DVC** for the
data/ML pipeline, **MLflow** for experiment tracking + a quality gate,
**FastAPI** for serving, **Docker** for packaging, **GitHub Actions** for
CI/CD, and **Airflow** for orchestration + retraining — implementing this
architecture end to end:

```
GitHub → GitHub Actions CI/CD → Airflow Orchestration → DVC Pipeline
      → [Data Validate → Preprocess → Train] → Evaluate → MLflow (tracking + registry)
      → Quality Gate → PASS → Staging → FastAPI → Docker → Production
                      → FAIL → Retrain
      → Production → Logging / Data Drift / Performance → Alerting → Airflow → Retrain
```

** Start with [`notes/00_overview.md`](notes/00_overview.md)** — the
`notes/` folder is a full, numbered, step-by-step guide explaining not just
*what* each file does but *why* it's structured that way.

## Quickstart

```bash
# 1. Install dependencies (AutoGluon assumed already installed per your setup)
pip install -r requirements.txt
pip install -e .

# 2. Run the training pipeline
python main.py                 # plain python, or:
dvc init && dvc repro          # the DVC way (recommended - caching + reproducibility)

# 3. Serve the trained model
uvicorn app.main:app --reload --port 8000
# -> http://localhost:8000/docs

# 4. Or run everything containerized
docker compose up --build
```

## Project layout

```
config/config.yaml     WHERE things live (paths)
params.yaml             HOW training behaves (AutoGluon presets, quality gate threshold)
schema.yaml              WHAT the data must look like (columns + target)

src/mlops_project/
  components/            the real logic: ingestion, validation, transformation, AutoGluon training, evaluation
  pipeline/               thin DVC/CLI entrypoints + the FastAPI prediction pipeline
  config/ entity/          yaml -> typed config objects
  utils/ logger.py exception.py

app/                     FastAPI service (loads artifacts/model_trainer/model.pkl)
dvc.yaml                 the 5-stage DVC pipeline DAG
dags/                    Airflow DAG (scheduled + drift/alert-triggered retraining)
.github/workflows/       CI/CD: test -> dvc repro -> quality gate -> docker build & push
Dockerfile / docker-compose.yaml
notes/                   step-by-step guide, one file per pipeline stage
```

See [`notes/01_project_structure.md`](notes/01_project_structure.md) for the
full annotated file tree.

## Notes index

| # | File | Covers |
|---|---|---|
| 00 | [overview](notes/00_overview.md) | architecture, tool choices, quickstart |
| 01 | [project structure](notes/01_project_structure.md) | full file map + the config/entity/component/pipeline pattern |
| 02 | [data ingestion](notes/02_data_ingestion.md) | pulling raw data into `artifacts/` |
| 03 | [data validation](notes/03_data_validation.md) | schema checks, fail-fast |
| 04 | [data transformation](notes/04_data_transformation.md) | train/test split |
| 05 | [AutoGluon training](notes/05_model_training_autogluon.md) | `TabularPredictor`, presets, the pickle artifact |
| 06 | [model evaluation](notes/06_model_evaluation.md) | metrics + the Quality Gate |
| 07 | [DVC pipeline](notes/07_dvc_pipeline.md) | `dvc.yaml`, caching, `dvc repro` |
| 08 | [MLflow tracking](notes/08_mlflow_tracking.md) | experiment tracking + registry |
| 09 | [FastAPI serving](notes/09_fastapi_serving.md) | `/predict`, `/health`, request/response schemas |
| 10 | [Docker](notes/10_docker.md) | Dockerfile design, docker-compose |
| 11 | [CI/CD](notes/11_cicd_github_actions.md) | GitHub Actions workflow, 3-job pipeline |
| 12 | [Airflow](notes/12_airflow_orchestration.md) | scheduled retraining DAG |
| 13 | [Monitoring & retraining](notes/13_monitoring_and_retraining.md) | drift, alerting, closing the loop |

---
