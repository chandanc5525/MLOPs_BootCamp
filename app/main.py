"""
FastAPI serving layer.

PURPOSE (see architecture diagram: Staging -> FastAPI -> Docker -> Production):
  Once a model passes the MLflow quality gate, this is the service that
  exposes it for real-time inference. It loads the SAME model.pkl artifact
  produced by the training pipeline (src/mlops_project/components/model_trainer.py)
  - training and serving never diverge because they share one artifact file.

  Run locally:      uvicorn app.main:app --reload --port 8000
  Run in Docker:     see Dockerfile / docker-compose.yaml
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import AirQualityInput, PredictionResponse, HealthResponse
from src.mlops_project.pipeline.predict_pipeline import PredictionPipeline
from src.mlops_project.logger import get_logger

logger = get_logger(__name__)

MODEL_PATH = os.getenv("MODEL_PKL_PATH", "artifacts/model_trainer/model.pkl")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1")

app = FastAPI(
    title="AutoGluon Air Quality Prediction API",
    description="Serves the AutoGluon model trained by the DVC/MLflow MLOps pipeline",
    version=MODEL_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_predictor: PredictionPipeline | None = None


@app.on_event("startup")
def load_model():
    """Load the pickled model once at startup, not on every request."""
    global _predictor
    try:
        _predictor = PredictionPipeline(MODEL_PATH)
        logger.info(f"Model loaded from {MODEL_PATH}")
    except Exception as e:
        # Don't crash the app - /health will report model_loaded=False so
        # orchestration (k8s/Docker healthcheck) can detect and restart/alert.
        logger.exception(f"Failed to load model at startup: {e}")
        _predictor = None


@app.get("/", tags=["meta"])
def root():
    return {"message": "AutoGluon Air Quality Prediction API. See /docs for usage."}


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health():
    return HealthResponse(status="ok", model_loaded=_predictor is not None)


@app.post("/predict", response_model=PredictionResponse, tags=["inference"])
def predict(payload: AirQualityInput):
    if _predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Check /health and server logs.",
        )
    try:
        prediction = _predictor.predict(payload.dict())
        return PredictionResponse(predicted_AQI=round(prediction, 2), model_version=MODEL_VERSION)
    except Exception as e:
        logger.exception(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
