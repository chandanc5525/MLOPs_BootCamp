# ---------------------------------------------------------------------------
# Serving image for the FastAPI app.
#
# DESIGN CHOICE: Note: this image does NOT train the model. Training (AutoGluon,
# which needs a lot of CPU/RAM and build tooling) happens in CI or on a
# dedicated training job, and produces artifacts/model_trainer/model.pkl.
# This image just COPIES that pre-trained artifact in and serves it - this
# keeps the production image small(er) and startup fast, matching the
# diagram's "Staging -> FastAPI -> Docker -> Production" flow.
# ---------------------------------------------------------------------------
FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps AutoGluon / lightgbm / scikit-learn wheels sometimes need
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install deps first for better layer caching (only re-installs on
# requirements.txt change, not on every source-code change).
COPY requirements.txt setup.py ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt

# App code + the pre-trained artifact
COPY app ./app
COPY config ./config
COPY params.yaml schema.yaml ./
COPY artifacts/model_trainer/model.pkl ./artifacts/model_trainer/model.pkl

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
