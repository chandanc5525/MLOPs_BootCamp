# 13 — Production Monitoring, Alerting & the Retrain Loop

## Purpose

This closes the loop at the bottom of your diagram:

```
Production → Logging / Data Drift / Performance → Alerting → Airflow → Retrain
```

Unlike stages 1–11, this is intentionally left as a **design + integration
guide** rather than a fully wired subsystem — production monitoring choices
(which drift detector, which alerting channel, which metrics store) are
usually organization-specific. Below is exactly what to build and where it
plugs into the existing code.

## 1. Logging

Every component already uses `src/mlops_project/logger.py`, which writes to
both console and a timestamped file under `logs/`. In production:
- Ship container stdout/stderr (FastAPI's Uvicorn logs + our app logger's
  console handler) to a central log store (CloudWatch, ELK/OpenSearch,
  Loki, Datadog, etc.) — no code change needed, just infra config pointing
  at the container's log stream.
- Add structured request logging in `app/main.py`'s `/predict` handler:
  log every request's input + prediction (with appropriate PII handling) so
  you have a ground truth of *what the model actually saw and predicted* in
  production, which both of the next two sections depend on.

## 2. Data Drift Detection

**What**: compare the distribution of features arriving at `/predict` in
production against the distribution `model_trainer.py` was trained on
(`artifacts/data_transformation/train.csv`).

**How to build it** (suggested approach, not yet implemented in this repo):
- A small script/service (or a new Airflow task) that periodically pulls
  logged production requests (from step 1) and runs a statistical test per
  feature — e.g. Kolmogorov–Smirnov for continuous features like `PM2_5`,
  `Temperature` — against the training distribution.
- Tools that do this well out of the box: **Evidently AI** or
  **whylogs/WhyLabs** — both integrate cleanly with a pandas DataFrame,
  which is exactly what this project already works with everywhere else.
- This is conceptually the same check as `data_validation.py`
  (`03_data_validation.md`) — comparing today's data against a fixed
  expectation — just comparing against *yesterday's data* instead of
  against `schema.yaml`.

## 3. Performance Monitoring

**What**: is the deployed model's real-world accuracy holding up?

**How**: this requires *ground truth* to eventually arrive (e.g. the actual
measured AQI becomes available some hours/days after a prediction was
made). Once it does:
- Join logged predictions (step 1) with the ground truth by timestamp/ID.
- Recompute R²/MAE/RMSE on this "production window" using the exact same
  functions already in `model_evaluation.py` (`r2_score`,
  `mean_absolute_error`, `mean_squared_error`) — re-use, don't reinvent.
- Log these to the same MLflow experiment (`08_mlflow_tracking.md`) under a
  distinct run type/tag (e.g. `run_type=production_monitoring`), so
  training-time and production-time metrics are comparable in the same UI.

## 4. Alerting

**What**: when drift or performance-degradation crosses a threshold, notify
someone AND (optionally) auto-trigger retraining.

**How**: thresholds are configuration, following the same pattern as
`quality_gate.min_r2_threshold` in `params.yaml` — e.g. add:
```yaml
monitoring:
  max_drift_score: 0.1
  min_production_r2: 0.45
```
A monitoring job breaching these should:
- send a notification (Slack webhook / PagerDuty / email — whichever your
  team already uses)
- call `airflow dags trigger air_quality_autogluon_training_pipeline`
  (`12_airflow_orchestration.md`) to kick off an out-of-schedule retrain

## 5. Retrain

This is where the loop closes: the triggered Airflow DAG run walks through
`data_ingestion → ... → model_evaluation → quality_gate` exactly as
described in notes 02–07 and 12, on fresh production data, and either
promotes a new model (re-entering the CI/CD path toward a new Docker image)
or flags for further investigation if the new model *still* doesn't clear
the gate — which is itself a signal worth alerting a human about, since it
suggests the problem isn't stale data but something more fundamental (a
genuine shift in the relationship between features and target).

## Summary: what's implemented vs. what's a blueprint

| Piece | Status in this repo |
|---|---|
| Logging | ✅ implemented (`logger.py`, used everywhere) |
| Data validation (schema-level) | ✅ implemented (`data_validation.py`) |
| Quality gate (train-time) | ✅ implemented (`model_evaluation.py`) |
| MLflow tracking | ✅ implemented |
| Data drift detection | 📋 blueprint above — plug in Evidently/whylogs |
| Production performance monitoring | 📋 blueprint above — reuses `model_evaluation.py`'s metric functions |
| Alerting | 📋 blueprint above — wire to Slack/PagerDuty + `airflow dags trigger` |
