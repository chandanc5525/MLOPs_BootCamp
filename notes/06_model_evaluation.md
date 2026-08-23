# 06 — Model Evaluation & the Quality Gate

**Files:** `src/mlops_project/components/model_evaluation.py`,
`src/mlops_project/pipeline/stage_05_model_evaluation.py`

## Purpose

Score the trained model on the held-out test set, log the run to MLflow, and
decide — programmatically — whether this model is good enough to be
promoted toward Staging/FastAPI/Docker/Production, matching the diagram's
`MLflow → Quality Gate → PASS/FAIL` branch.

## What the code does

```python
predictor = load_pickle(self.config.model_pkl_file)     # the .pkl from stage 05
y_pred = predictor.predict(X_test)

metrics = {
    "r2_score": r2_score(y_true, y_pred),
    "mae": mean_absolute_error(y_true, y_pred),
    "rmse": sqrt(mean_squared_error(y_true, y_pred)),
}
metrics["quality_gate_passed"] = metrics["r2_score"] >= self.config.min_r2_threshold
save_json(self.config.metric_file, metrics)   # artifacts/model_evaluation/metrics.json
```

Then it logs to MLflow:

```python
mlflow.set_tracking_uri(self.config.mlflow_uri)   # params.yaml: mlflow.tracking_uri
mlflow.set_experiment("autogluon-air-quality")
with mlflow.start_run():
    mlflow.log_metric("r2_score", ...)
    mlflow.log_param("quality_gate_passed", ...)
    mlflow.log_artifact(str(self.config.model_pkl_file))
```

## Why a Quality Gate, and why here

Without an automated gate, "is this new model good enough to deploy?"
becomes a manual judgment call someone has to remember to make on every
retrain — which doesn't scale, especially once Airflow is retraining weekly
or on drift-triggers with no human in the loop by default.

`min_r2_threshold` in `params.yaml` (`quality_gate.min_r2_threshold`,
default `0.5`) encodes that judgment call as data. Both:
- **CI/CD** (`.github/workflows/ci-cd.yaml`, `dvc-pipeline` job) reads
  `metrics.json` and fails the workflow (blocking the Docker build/push job)
  if `quality_gate_passed` is `false`.
- **Airflow** (`dags/air_quality_training_dag.py`) branches on the same
  field to route to `promote_to_staging` vs. `flag_for_retrain`.

Both consumers read the exact same `metrics.json` — there's only one source
of truth for "did this model pass."

## Why R² specifically (and how to change it)

R² is a natural fit for a regression target like AQI: it's scale-free and
easy to reason about ("model explains X% of the variance"). If you switch to
a different target/metric, update:
- `params.yaml` → `autogluon.eval_metric` (what AutoGluon optimizes for)
- `params.yaml` → `quality_gate.min_r2_threshold` → rename/rescale as needed
- `model_evaluation.py` → the gate condition and the metrics dict

## How to run just this stage

```bash
python -m src.mlops_project.pipeline.stage_05_model_evaluation
# or:
dvc repro model_evaluation
dvc metrics show   # pretty-print artifacts/model_evaluation/metrics.json
```
