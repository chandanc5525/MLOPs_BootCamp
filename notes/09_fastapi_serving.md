# 09 — Serving the Model with FastAPI

**Files:** `app/main.py`, `app/schemas.py`,
`src/mlops_project/pipeline/predict_pipeline.py`

## Purpose

Once a model clears the Quality Gate, this is the `Staging → FastAPI` box:
a REST API that loads `artifacts/model_trainer/model.pkl` and serves
real-time predictions.

## Why FastAPI

- **Automatic validation** — `app/schemas.py`'s `AirQualityInput` pydantic
  model rejects malformed requests (wrong type, missing field) with a
  clear `422` response before your code ever runs.
- **Automatic docs** — visiting `/docs` gives you a full interactive Swagger
  UI, generated from the same pydantic models, with zero extra work.
- **Async-ready** — FastAPI runs on Uvicorn/ASGI, so it scales well for
  I/O-bound serving workloads without extra configuration.

## Design: training and serving share ONE artifact

```python
MODEL_PATH = os.getenv("MODEL_PKL_PATH", "artifacts/model_trainer/model.pkl")

@app.on_event("startup")
def load_model():
    global _predictor
    _predictor = PredictionPipeline(MODEL_PATH)   # pickle.load() under the hood
```

This is deliberate: training (`model_trainer.py`) and serving (`app/main.py`)
never independently re-implement preprocessing or feature handling — they
both just point at the same `model.pkl`. This eliminates an entire class of
"training/serving skew" bugs.

The model loads **once**, at process startup — not on every request — so
`/predict` calls stay fast.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | basic liveness message |
| `GET` | `/health` | `{"status": "ok", "model_loaded": true/false}` — used by Docker's `HEALTHCHECK` and by orchestration platforms (k8s liveness/readiness probes) |
| `POST` | `/predict` | takes `AirQualityInput` JSON, returns `{"predicted_AQI": ..., "model_version": ...}` |

## Example request

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
        "PM2_5": 45.2, "PM10": 70.5, "NO2": 18.3, "SO2": 6.1,
        "CO": 0.8, "O3": 32.0, "Temperature": 27.5,
        "Humidity": 60.0, "WindSpeed": 3.2
      }'
```

## Running locally (outside Docker)

```bash
uvicorn app.main:app --reload --port 8000
```

## Error handling philosophy

If the model fails to load at startup, the app does **not** crash — it
starts, but `/health` reports `model_loaded: false` and `/predict` returns
`503 Service Unavailable`. This lets an orchestrator (k8s/Docker) detect the
unhealthy state via the healthcheck and restart or alert, rather than the
whole container immediately crash-looping with no diagnostic info.
