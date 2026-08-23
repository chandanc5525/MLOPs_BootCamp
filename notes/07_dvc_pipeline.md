# 07 — The DVC Pipeline (`dvc.yaml`)

**Files:** `dvc.yaml`, `params.yaml`

## Purpose

DVC ("Data Version Control") is what makes this project's `Data + ML
Pipeline` box in your diagram real: it (a) tracks large data/model files
outside of git, and (b) defines a reproducible, cacheable DAG of stages.

## Why DVC (and not just a Makefile or bash script)

- **Caching by content hash**: if `data/raw/air_quality.csv` hasn't changed
  and `params.yaml`'s `autogluon.*` values haven't changed, `dvc repro`
  skips `model_trainer` entirely instead of re-running a 2-hour AutoGluon
  job for nothing.
- **Data versioning without bloating git**: `artifacts/model_trainer/model.pkl`
  can be tens/hundreds of MB. DVC stores it in a `.dvc`-tracked cache and,
  optionally, a remote (S3/GCS/Azure/DagsHub) via `dvc push`/`dvc pull`,
  while git only stores small pointer files.
- **A visualizable, honest DAG**: `dvc dag` prints exactly what depends on
  what — matching the diagram's `Data Validate / Preprocess / Train →
  Evaluate` fan-in.

## Anatomy of one stage (from `dvc.yaml`)

```yaml
model_trainer:
  cmd: python -m src.mlops_project.pipeline.stage_04_model_trainer
  deps:
    - src/mlops_project/pipeline/stage_04_model_trainer.py
    - src/mlops_project/components/model_trainer.py
    - artifacts/data_transformation/train.csv
  params:
    - autogluon.presets
    - autogluon.time_limit
    - autogluon.eval_metric
  outs:
    - artifacts/model_trainer/model.pkl
    - artifacts/model_trainer/autogluon_model
```

- `cmd` — exactly what to run (same command you'd run by hand).
- `deps` — code + upstream data. Changing ANY of these invalidates the
  cache for this stage on the next `dvc repro`.
- `params` — specific *keys* inside `params.yaml`. This is finer-grained
  than `deps`: only `autogluon.presets`/`time_limit`/`eval_metric` changing
  triggers a re-run, not unrelated keys like `quality_gate.min_r2_threshold`.
- `outs` — DVC-tracked outputs. Content-hashed, cached, and (if you set up
  a remote) push/pull-able independent of git.

## The full 5-stage DAG

```
data_ingestion → data_validation → data_transformation → model_trainer → model_evaluation
```

This is literally the `Data Validate / Preprocess / Train → Evaluate` chain
from your architecture diagram, expressed as code.

## Common commands

```bash
dvc init                    # one-time, creates .dvc/
dvc repro                   # run the whole pipeline (skips unchanged stages)
dvc repro model_trainer     # run up to (and including) just this stage
dvc dag                     # ascii DAG of stage dependencies
dvc metrics show            # print artifacts/model_evaluation/metrics.json
dvc metrics diff            # compare metrics vs. the last git commit

# Remote storage (configure once):
dvc remote add -d storage s3://my-bucket/dvc-store
dvc push                    # upload tracked data/artifacts to the remote
dvc pull                    # download them (e.g. fresh CI runner, new teammate)
```

## Where this plugs into CI/CD and Airflow

- `.github/workflows/ci-cd.yaml`'s `dvc-pipeline` job runs `dvc repro`
  directly.
- `dags/air_quality_training_dag.py`'s Airflow tasks each run
  `dvc repro <stage_name>` via `BashOperator` — Airflow decides *when*,
  DVC still owns *what/how/caching*.
