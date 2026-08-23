# 11 — CI/CD with GitHub Actions

**Files:** `.github/workflows/ci-cd.yaml`

## Purpose

This is the `GitHub → GitHub Actions CI/CD` box at the very top of your
diagram: every push to `main` (or PR) automatically tests, retrains,
gate-checks, and — if everything passes — builds and pushes a new Docker
image.

## Why 3 separate jobs (not one big job)

```
lint-and-test  →  dvc-pipeline  →  build-and-push-image
```

Each job only runs if the previous one succeeded (`needs:`). This ordering
is intentional and saves real CI minutes:

1. **`lint-and-test`** — fast unit tests (`tests/test_basic.py`, seconds to
   run). Catches config/wiring mistakes immediately, before spending any
   time on the (slower) DVC pipeline.
2. **`dvc-pipeline`** — runs `dvc repro` (the real ingestion → validation →
   transformation → AutoGluon training → evaluation chain), then explicitly
   checks `metrics.json`'s `quality_gate_passed` and **fails the workflow**
   if the gate didn't pass:
   ```python
   if not m["quality_gate_passed"]:
       sys.exit(1)
   ```
   This is the CI-level enforcement of the `Quality Gate` in your diagram —
   a model that doesn't clear the bar simply cannot reach the next job.
3. **`build-and-push-image`** — only runs on pushes to `main` AND only
   after the gate passed. Downloads the `model.pkl` produced by job 2 as a
   build artifact, builds the Docker image (see `10_docker.md`), and pushes
   it to DockerHub with two tags: `latest` and the git SHA (so you can
   always pin/rollback to an exact build).

## Secrets you'd configure (repo Settings → Secrets and variables → Actions)

| Secret | Used for |
|---|---|
| `DOCKERHUB_USERNAME` | Docker registry login + image tag namespace |
| `DOCKERHUB_TOKEN` | Docker registry auth token |

If you're storing DVC-tracked data/artifacts on a remote (S3/GCS/DagsHub),
uncomment the `dvc pull` / `dvc push` steps and add the matching cloud
credentials as secrets too.

## Extending toward real deployment

The workflow ends after pushing the image; the actual "swap the running
container for the new one" step is infra-specific (SSH + `docker compose
pull && up -d` on a VM; `kubectl set image` / a Helm upgrade on k8s; an ECS
service update on AWS). A placeholder step is left in the workflow file for
you to fill in:

```yaml
# - name: Deploy to production
#   run: ./scripts/deploy.sh
```

## Local equivalent (for testing before you push)

```bash
pytest tests/ -v
dvc repro
python -c "import json; print(json.load(open('artifacts/model_evaluation/metrics.json')))"
docker build -t mlops-autogluon-airquality:local .
```
