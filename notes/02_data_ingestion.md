# 02 — Data Ingestion

**Files:** `src/mlops_project/components/data_ingestion.py`,
`src/mlops_project/pipeline/stage_01_data_ingestion.py`

## Purpose

Take raw data from wherever it originates and land it in one predictable
place: `artifacts/data_ingestion/raw_data.csv`. Every later stage reads
*only* from this path — never from the original source directly.

## Why this matters (the logic behind it)

If every stage read from "wherever the data happens to be" (an S3 bucket
today, a warehouse table tomorrow), you'd need to update every downstream
file whenever the source changes. By funneling everything through one
ingestion step:

- Swapping the source (local CSV → S3 → a database query → an API pull) is
  a one-file change (`DataIngestion._load_source()`), nothing else moves.
- DVC can hash `raw_data.csv` and know exactly when downstream stages need
  to re-run — it doesn't need to understand S3 or your database.
- You get a natural point to add retry logic, source-format handling
  (json/parquet/csv), or credentials handling, isolated from ML logic.

## What the code does

```python
class DataIngestion:
    def _load_source(self) -> pd.DataFrame:
        return pd.read_csv(self.config.source_path)

    def ingest(self) -> str:
        df = self._load_source()
        df.to_csv(self.config.raw_data_file, index=False)
        return self.config.raw_data_file
```

In this bootcamp, `source_path` is the local
`data/raw/air_quality.csv` (a synthetic dataset — see
`scripts_generate_sample_data.py`). In production, replace `_load_source()`
with, e.g.:

```python
def _load_source(self) -> pd.DataFrame:
    import boto3, io
    obj = boto3.client("s3").get_object(Bucket="my-bucket", Key="air_quality/latest.csv")
    return pd.read_csv(io.BytesIO(obj["Body"].read()))
```

Nothing else in the repo needs to change.

## How to run just this stage

```bash
python -m src.mlops_project.pipeline.stage_01_data_ingestion
# or, via DVC:
dvc repro data_ingestion
```
