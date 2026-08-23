# 05 — Model Training with AutoGluon

**Files:** `src/mlops_project/components/model_trainer.py`,
`src/mlops_project/pipeline/stage_04_model_trainer.py`, `params.yaml`

## Purpose

Train a strong model with minimal manual tuning, and persist it as the
canonical **pickle artifact** the rest of the system (evaluation, FastAPI,
Docker) depends on.

## Why AutoGluon

`autogluon.tabular.TabularPredictor` automatically:
- infers the problem type (regression here, since `AQI` is continuous)
- tries multiple model families (LightGBM, CatBoost, XGBoost, Random
  Forest/Extra Trees, neural nets) and stacks/ensembles the best ones
- handles missing values, categorical encoding, and feature typing
  internally

That's ideal for a bootcamp: it lets you focus on *the pipeline* (this whole
repo) rather than manually tuning gradient boosting hyperparameters.

## What the code does

```python
predictor = TabularPredictor(
    label=self.config.target_column,      # "AQI", from schema.yaml
    path=self.config.model_dir,            # artifacts/model_trainer/autogluon_model/
    eval_metric=self.config.eval_metric,   # "r2", from params.yaml
).fit(
    train_data=train_df,
    presets=self.config.presets,           # "medium_quality" by default
    time_limit=self.config.time_limit,     # 120s by default
)

save_pickle(self.config.model_pkl_file, predictor)   # artifacts/model_trainer/model.pkl
```

### `presets` — the main knob you'll tune

| preset | trade-off |
|---|---|
| `medium_quality` | fast, good baseline — used as the default here so the bootcamp trains quickly |
| `good_quality` | better accuracy, more compute |
| `high_quality` | further stacked ensembling |
| `best_quality` | maximum accuracy, longest training time — use for the final "real" model |

Change it in `params.yaml` under `autogluon.presets`; DVC will detect the
change and re-run `model_trainer` (and everything after it) automatically.

### `time_limit` — the second knob

`120` seconds is intentionally short so `dvc repro` / CI runs finish
quickly for the bootcamp. For a real production model, raise this
substantially (e.g. 1800–3600s) in `params.yaml`.

## The artifact strategy — "pickle file" requirement, explained

You asked for the artifact to be a file where a **pickle file** gets stored.
There are two "save formats" at play here, both produced by this stage:

1. **`artifacts/model_trainer/autogluon_model/`** — a *directory*.
   This is AutoGluon's own native persistence format, written automatically
   by `TabularPredictor(path=...)`, and is what AutoGluon itself recommends
   loading back with `TabularPredictor.load(path)`.

2. **`artifacts/model_trainer/model.pkl`** — a single **pickle file**,
   written explicitly by `save_pickle()` right after `.fit()` completes.
   This is the artifact that:
   - DVC declares as the `model_trainer` stage's canonical output in `dvc.yaml`
   - `model_evaluation.py` loads for scoring
   - the FastAPI app (`app/main.py`) loads for real-time inference
   - gets copied into the Docker image (see `Dockerfile`)

Keeping both means you get AutoGluon's own robust save/load path *and* a
single portable `.pkl` file that fits the "one artifact file" requirement
and is trivial to pass around (upload as a CI artifact, attach to an MLflow
run, copy into a Docker build context).

## How to run just this stage

```bash
python -m src.mlops_project.pipeline.stage_04_model_trainer
# or:
dvc repro model_trainer
```
