# 01 — Project Structure

## Full folder layout

```
mlops_autogluon_bootcamp/
├── .github/workflows/ci-cd.yaml      # GitHub Actions: test → dvc repro → quality gate → docker build/push
├── dags/air_quality_training_dag.py  # Airflow DAG: orchestrates dvc repro on a schedule / on trigger
│
├── config/config.yaml                # WHERE things live (paths)
├── params.yaml                       # HOW training behaves (AutoGluon presets, thresholds)
├── schema.yaml                       # WHAT the data must look like (expected columns + target)
│
├── data/raw/air_quality.csv          # raw input data (DVC-tracked in a real setup)
├── scripts_generate_sample_data.py   # generates the synthetic demo CSV above
│
├── src/mlops_project/
│   ├── logger.py                     # shared logging setup
│   ├── exception.py                  # CustomException with file/line context
│   ├── constants/__init__.py         # file-path constants
│   ├── entity/config_entity.py       # typed dataclasses: one per pipeline stage's config
│   ├── config/configuration.py       # ConfigurationManager: yaml → entity objects
│   ├── utils/common.py               # read_yaml, save/load pickle & json, create_directories
│   ├── components/                   # THE ACTUAL LOGIC of each stage
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   ├── data_transformation.py
│   │   ├── model_trainer.py          # AutoGluon TabularPredictor.fit()
│   │   └── model_evaluation.py       # metrics + MLflow logging + quality gate
│   └── pipeline/                     # THIN entrypoint scripts DVC/CLI call
│       ├── stage_01_data_ingestion.py
│       ├── stage_02_data_validation.py
│       ├── stage_03_data_transformation.py
│       ├── stage_04_model_trainer.py
│       ├── stage_05_model_evaluation.py
│       └── predict_pipeline.py       # used by FastAPI for inference
│
├── app/
│   ├── main.py                       # FastAPI app (loads model.pkl, exposes /predict)
│   └── schemas.py                    # pydantic request/response models
│
├── artifacts/                        # ALL pipeline outputs land here (git-ignored, DVC-tracked)
│   ├── data_ingestion/raw_data.csv
│   ├── data_validation/status.txt
│   ├── data_transformation/{train,test}.csv
│   ├── model_trainer/model.pkl       # <-- the pickle artifact FastAPI serves
│   ├── model_trainer/autogluon_model/# AutoGluon's own internal save format
│   └── model_evaluation/metrics.json
│
├── dvc.yaml                          # the 5-stage DVC pipeline DAG
├── main.py                           # runs all 5 stages with plain `python main.py`
├── Dockerfile                        # builds the FastAPI serving image
├── docker-compose.yaml               # runs API + a local MLflow server together
├── requirements.txt / setup.py
├── tests/test_basic.py               # fast smoke tests for CI
└── notes/                            # you are here
```

## The "3 yaml files" pattern — why split config this way?

This is the single most important structural idea in the whole project, so
it's worth calling out on its own:

- **`config.yaml`** — *where things live*. Paths only. Changing this doesn't
  change what the model learns, just where files get read/written.
- **`params.yaml`** — *how training behaves*. AutoGluon's `presets`,
  `time_limit`, the quality gate's `min_r2_threshold`. DVC watches this file:
  if you bump `time_limit`, DVC knows the `model_trainer` stage (and
  everything downstream) must re-run, but `data_ingestion` doesn't.
- **`schema.yaml`** — *what the data contracts to*. Column names + the
  target column name. `data_validation.py` enforces this before any
  training happens.

## The `entity → config → component → pipeline` chain

Every stage follows the same 4-layer pattern, and once you understand it for
one stage you understand it for all five:

1. **entity** (`config_entity.py`) — a frozen dataclass describing exactly
   what fields this stage needs (typed, no magic strings).
2. **config** (`configuration.py`) — reads the 3 yaml files and builds one
   of those entity objects.
3. **component** (`components/*.py`) — the real logic; takes an entity
   object in its constructor, has no idea yaml files exist.
4. **pipeline** (`pipeline/stage_*.py`) — a ~15-line script: build config →
   construct component → call its method. This is what DVC's `dvc.yaml`
   actually executes as `cmd:`.

This separation means you can unit-test `components/model_trainer.py` by
constructing a `ModelTrainerConfig` directly in a test, with no yaml files
or DVC involved at all (see `tests/test_basic.py`).
