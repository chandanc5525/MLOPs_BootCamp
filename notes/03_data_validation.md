# 03 — Data Validation

**Files:** `src/mlops_project/components/data_validation.py`,
`src/mlops_project/pipeline/stage_02_data_validation.py`, `schema.yaml`

## Purpose

Fail **fast and cheap**, before you spend minutes of compute on AutoGluon
training a model on bad data. This stage checks the ingested CSV's columns
against the contract declared in `schema.yaml`.

## Why this matters

In the architecture diagram, `Data Validate` sits right after `DVC` starts
the pipeline, before `Preprocess`/`Train`. That ordering is deliberate:
catching a missing/renamed column here costs a few milliseconds; catching it
after a 2-hour `best_quality` AutoGluon run wastes real time and money — and
in a scheduled Airflow run, might not be noticed until the next day.

## What the code does

```python
def validate(self) -> bool:
    df = pd.read_csv(self.config.raw_data_file)
    missing = set(expected_cols) - set(all_cols)
    validation_status = len(missing) == 0
    # write True/False + details to artifacts/data_validation/status.txt
    return validation_status
```

`stage_02_data_validation.py` raises a `ValueError` if validation fails,
which:
- stops `dvc repro` immediately (later stages never run on bad data)
- fails the GitHub Actions job (`dvc-pipeline` job in `ci-cd.yaml`)
- is visible in the Airflow task log if triggered from the DAG

## Extending it

Right now this only checks *column presence*. In production you'd likely
extend `DataValidation.validate()` to also check:
- dtypes (`schema.yaml` already has a `dtype` field per column, ready to use)
- null-rate thresholds per column
- value ranges (e.g. `Humidity` should be 0–100)
- row-count sanity bounds (dataset shouldn't suddenly be 10x smaller)

This is also exactly the kind of check you'd re-use inside the **Data
Drift** monitoring stage in production (see `13_monitoring_and_retraining.md`)
— drift detection is really "validation, but comparing today's data
distribution to yesterday's" instead of to a fixed schema.

## How to run just this stage

```bash
python -m src.mlops_project.pipeline.stage_02_data_validation
# or:
dvc repro data_validation
```
