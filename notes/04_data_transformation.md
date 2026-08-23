# 04 — Data Transformation

**Files:** `src/mlops_project/components/data_transformation.py`,
`src/mlops_project/pipeline/stage_03_data_transformation.py`

## Purpose

Produce a reproducible train/test split that both `model_trainer.py` and
`model_evaluation.py` consume.

## Why this is deliberately "light"

Unlike a classic scikit-learn pipeline, we do **not** hand-build encoders,
imputers, or scalers here. AutoGluon's `TabularPredictor.fit()` already does
robust automatic preprocessing internally (missing-value imputation,
categorical encoding, feature type detection) as part of training. Doing it
twice would be redundant and could actually leak information differently
than AutoGluon's own internal split does.

So this stage focuses on the two things AutoGluon does **not** do for you:

1. **Basic hygiene** — drop fully-empty rows and exact duplicates.
2. **The train/test split itself** — done here, as its own DVC-tracked
   output, so:
   - the exact same test set is reused across every retraining run
     (comparable metrics over time — critical for the Quality Gate to mean
     anything)
   - DVC content-hashes `train.csv`/`test.csv`, so if you re-run with the
     same data, this whole stage (and downstream training) is skipped
   - the test set never touches training in any way, protecting the R²
     computed in `06_model_evaluation.md` from being optimistic

## What the code does

```python
train_df, test_df = train_test_split(df, test_size=self.config.test_size, random_state=42)
train_df.to_csv(self.config.train_data_file, index=False)
test_df.to_csv(self.config.test_data_file, index=False)
```

`test_size` lives in `params.yaml` (`data_transformation.test_size`), not
hard-coded — so DVC knows to re-split (and retrain) if you change the split
ratio.

## How to run just this stage

```bash
python -m src.mlops_project.pipeline.stage_03_data_transformation
# or:
dvc repro data_transformation
```
