# 08 — MLflow: Experiment Tracking & Registry

**Files:** `src/mlops_project/components/model_evaluation.py`,
`params.yaml` (`mlflow.tracking_uri`), `docker-compose.yaml` (local server)

## Purpose

Every training run's parameters, metrics, and model artifact get logged to
MLflow — this is the `MLflow Experiment + Registry` box in your diagram,
sitting right after `Evaluate` and right before the `Quality Gate` decision.

## Why this matters

Without MLflow, "did the last retrain actually improve things?" is a
question you can only answer by reading `metrics.json` from a single run,
with no history. With MLflow you get:
- a searchable history of every run (params + metrics side by side)
- the actual model artifact attached to each run, so you can always go back
  to exactly the model that produced a given metric
- (via the Model Registry) named model versions with **stages** —
  `None → Staging → Production → Archived` — which is a very natural fit
  for the diagram's `Staging` box after the Quality Gate passes

## What the code does

```python
mlflow.set_tracking_uri(self.config.mlflow_uri)          # params.yaml
mlflow.set_experiment("autogluon-air-quality")
with mlflow.start_run():
    mlflow.log_metric("r2_score", metrics["r2_score"])
    mlflow.log_metric("mae", metrics["mae"])
    mlflow.log_metric("rmse", metrics["rmse"])
    mlflow.log_param("quality_gate_passed", passed_gate)
    mlflow.log_artifact(str(self.config.model_pkl_file))
```

## Tracking URI: local file vs. a real server

`params.yaml` defaults to `mlflow.tracking_uri: "file:./mlruns"` — a local
folder, zero setup, good for the bootcamp/local dev.

For a team/production setup, point it at a real tracking server instead:

```yaml
mlflow:
  tracking_uri: "http://mlflow-server:5000"
```

`docker-compose.yaml` includes a minimal `mlflow` service you can start
locally with `docker compose up mlflow` to try this without any cloud infra.

## Promoting a model via the Registry (manual step, or scripted in CI)

```python
import mlflow
client = mlflow.tracking.MlflowClient()
result = mlflow.register_model(
    f"runs:/{run_id}/model", "autogluon-air-quality"
)
client.transition_model_version_stage(
    name="autogluon-air-quality", version=result.version, stage="Staging"
)
```

In `.github/workflows/ci-cd.yaml`, the Quality Gate check plays this role
today by gating whether the `build-and-push-image` job runs at all — you
can extend that job to also call the snippet above once you have a shared
MLflow tracking server reachable from CI.

## Viewing the UI

```bash
mlflow ui --backend-store-uri file:./mlruns --port 5000
# open http://localhost:5000
```
