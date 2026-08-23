# 10 — Dockerizing the FastAPI Service

**Files:** `Dockerfile`, `docker-compose.yaml`, `.dockerignore`

## Purpose

Package the FastAPI service (and only the FastAPI service — see design
choice below) into a portable image: the `Docker → Production` step in your
diagram.

## Design choice: this image serves, it does not train

AutoGluon training needs meaningful CPU/RAM/time and a heavier dependency
set. Baking training into the serving image would make it huge and slow to
build/deploy for a step (serving) that should be fast and lightweight.

Instead:
1. Training happens via `dvc repro` — locally, in CI, or via Airflow —
   producing `artifacts/model_trainer/model.pkl`.
2. The Docker build **copies that pre-trained artifact in**:
   ```dockerfile
   COPY artifacts/model_trainer/model.pkl ./artifacts/model_trainer/model.pkl
   ```
3. The image only needs serving-time dependencies at runtime (though
   `requirements.txt` currently installs everything for simplicity — see
   "further optimization" below).

## Key Dockerfile decisions, explained

```dockerfile
FROM python:3.10-slim AS base          # small base image
RUN apt-get install -y libgomp1 build-essential   # LightGBM/XGBoost wheels need libgomp
COPY requirements.txt setup.py ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt   # deps layer cached separately from app code
COPY app ./app
COPY artifacts/model_trainer/model.pkl ...            # the trained artifact, copied in last
HEALTHCHECK ... CMD python -c "...urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- **Layer ordering** — `requirements.txt` is copied and installed *before*
  application code, so editing `app/main.py` doesn't invalidate the (slow)
  pip-install layer on rebuild.
- **`HEALTHCHECK`** — wired to the same `/health` endpoint FastAPI exposes,
  so `docker ps` and orchestrators can see container health without extra
  tooling.
- **`.dockerignore`** — excludes `.git`, `notes/`, `tests/`, `mlruns/`, raw
  `data/`, etc. so the build context (and resulting image) stays small and
  doesn't leak unrelated files into the image.

## Building & running

```bash
# Build (make sure artifacts/model_trainer/model.pkl exists first! run dvc repro / python main.py)
docker build -t mlops-autogluon-airquality:latest .

docker run -p 8000:8000 mlops-autogluon-airquality:latest
# -> http://localhost:8000/docs

# Or, with the bundled local MLflow server too:
docker compose up --build
```

## Further optimization ideas (left as an exercise / production hardening)

- Multi-stage build: a `builder` stage that pip-installs into a venv, and a
  slim final stage that only copies the venv + app code, dropping build
  tools like `build-essential`.
- Split `requirements.txt` into `requirements-train.txt` (AutoGluon + DVC)
  vs `requirements-serve.txt` (fastapi/uvicorn/pydantic/scikit-learn only)
  so the serving image never installs AutoGluon's heavy training deps at all.
- Pin exact versions (`==`) for full reproducibility, not just for CI but
  for a `pip-compile`/`requirements.lock` style workflow.
