 # Network Security: Phishing Website Detection

An end-to-end machine learning pipeline that detects phishing websites from URL and page-based features. The project covers the full ML lifecycle — data ingestion from MongoDB, schema-based validation, transformation, model training with experiment tracking, and a FastAPI service for training and real-time predictions.

## Problem Statement

Phishing websites imitate legitimate ones to steal sensitive user information. This project builds a binary classifier that flags a website as **phishing** or **legitimate** based on 30 URL/page-derived features (IP address usage, URL length, SSL state, domain age, web traffic rank, and more).

## Architecture

```
MongoDB (raw data)
      │
      ▼
Data Ingestion  ──►  Data Validation  ──►  Data Transformation  ──►  Model Trainer
      │                     │                      │                      │
      ▼                     ▼                      ▼                      ▼
 Feature store        Schema check          Preprocessor.pkl        Model.pkl
                     (schema.yaml)         (KNN Imputer, etc.)    (best of 5 models,
                                                                    tracked via MLflow/DagsHub)
                                                                          │
                                                                          ▼
                                                              FastAPI (train / predict)
```

Each stage reads the previous stage's artifact and writes its own, keeping the pipeline modular and independently testable — the same design pattern used in production ML systems.

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3 |
| Data storage | MongoDB (`pymongo`) |
| Data processing | Pandas, NumPy |
| Modeling | scikit-learn (Random Forest, Decision Tree, Gradient Boosting, Logistic Regression, AdaBoost) |
| Experiment tracking | MLflow + DagsHub |
| Serving | FastAPI, Uvicorn |
| Serialization | dill / pickle |
| Deployment | Docker |

## Project Structure

```
networksecurity/
├── networksecurity/
│   ├── components/          # data_ingestion, data_validation, data_transformation, model_trainer
│   ├── pipeline/             # training_pipeline.py, batch_prediction.py
│   ├── entity/                # config_entity.py, artifact_entity.py (typed configs/artifacts passed between stages)
│   ├── exception/            # custom NetworkSecurityException
│   ├── logging/              # custom logger
│   ├── constant/             # pipeline-wide constants
│   └── utils/                  # ml_utils (metrics, estimator wrapper), main_utils
├── data_schema/schema.yaml    # expected columns and dtypes for validation
├── Network_Data/               # raw phishing dataset
├── final_models/                # trained model.pkl and preprocessor.pkl
├── templates/table.html        # prediction results view
├── app.py                        # FastAPI app: /train and /predict routes
├── main.py                       # runs the training pipeline end-to-end
├── push_data.py                  # pushes raw CSV data into MongoDB
├── requirements.txt
├── setup.py
└── Dockerfile
```

## Pipeline Stages

1. **Data Ingestion** — Reads data from a MongoDB collection into a Pandas DataFrame, splits it into train/test sets, and stores it as a feature store artifact.
2. **Data Validation** — Validates the ingested data against `data_schema/schema.yaml` (column count, names, and dtypes) and checks for data drift between train and test sets.
3. **Data Transformation** — Handles missing values (KNN Imputer) and prepares the final numpy arrays used for training; saves the fitted preprocessor as `preprocessor.pkl`.
4. **Model Training** — Trains multiple classifiers (Random Forest, Decision Tree, Gradient Boosting, Logistic Regression, AdaBoost) with hyperparameter search, selects the best model by F1-score, and logs metrics (F1, precision, recall) to MLflow via DagsHub. The best model is saved as `model.pkl`.
5. **Serving** — A FastAPI app exposes:
   - `GET /train` — triggers the full training pipeline
   - `POST /predict` — accepts a CSV file, runs inference using the saved preprocessor + model, writes results to `prediction_output/output.csv`, and renders them as an HTML table

## Setup & Installation

```bash
git clone https://github.com/Kartiksingh007/networksecurity.git
cd networksecurity

python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows

pip install -r requirements.txt
```

Create a `.env` file in the project root with your MongoDB connection string:

```
MONGODB_URL_KEY=<your-mongodb-connection-string>
```

## Usage

**Push raw data to MongoDB:**
```bash
python push_data.py
```

**Run the training pipeline end-to-end:**
```bash
python main.py
```

**Start the FastAPI server:**
```bash
python app.py
```
Visit `http://localhost:8000/docs` for the interactive Swagger UI, or call `/train` and `/predict` directly.

## Dataset

30 categorical/numerical features derived from URL and page properties (e.g. `having_IP_Address`, `SSLfinal_State`, `age_of_domain`, `web_traffic`, `Google_Index`), with `Result` as the binary target (phishing vs. legitimate). Full schema in `data_schema/schema.yaml`.

## Experiment Tracking

Training runs and metrics (F1-score, precision, recall) are logged to MLflow, backed by DagsHub, for comparison across model runs and hyperparameter configurations.

## Roadmap

- [ ] Complete the Dockerfile and add deployment instructions
- [ ] Add CI/CD (GitHub Actions) for automated testing and deployment
- [ ] Add unit tests for each pipeline component
- [ ] Push trained artifacts to cloud storage (S3/Azure) via the `cloud` module

## Author

**Kartik Singh** — ML Engineer / Data Scientist
