# ⚽ EPL Match Predictor Platform

A production-ready full-stack platform designed to predict English Premier League match outcomes using advanced Machine Learning techniques, sophisticated feature engineering (Elo, team form), and rigorous MLOps practices.

---

## 🏗️ Architecture and Stack

The platform is built on a robust three-tier architecture, emphasizing scalability, maintainability, and explainability.

| Layer        | Component                | Technology                             | Role                                                                                     |
| ------------ | ------------------------ | -------------------------------------- | ---------------------------------------------------------------------------------------- |
| Frontend     | Single Page App (SPA)    | React, Vite, TailwindCSS               | User interface for predictions, simulations, and admin control.                          |
| Backend      | API Gateway & Service    | FastAPI (Python)                       | Handles user authentication (JWT), request routing, rate limiting, and ML model serving. |
| ML/Data      | Model Artifacts          | Scikit-learn, XGBoost, Optuna, SHAP    | Trains, tunes, and explains the match outcome prediction model.                          |
| Data Storage | Persistence              | SQLite (via SQLAlchemy/Alembic)        | Stores user data, match history, prediction logs, and rate limit tracking.               |
| DevOps       | Containerization & CI/CD | Docker, Docker Compose, GitHub Actions | Provides reproducible environments and automated daily model retraining.                 |

---

## ✨ Features

* **Multi-Model Support:** Selectable models including RandomForest, XGBoost, Logistic Regression, and Ensemble Averaging.
* **Advanced Feature Engineering:** Incorporates Elo Ratings, rolling average team form (points, goals for/against), and home/away strength.
* **Security & Auth:** JWT-based user authentication and strict rate limiting (30 requests per day per user).
* **Admin Override:** Unlimited access for `anouarguemri1@gmail.com`.
* **Explainability (XAI):** Integrated SHAP values to provide transparency on feature influence for every prediction.
* **Monte Carlo Simulation:** Endpoints for `/simulate-match` and `/simulate-season` simulations.
* **Auto-Update Pipeline:** Daily GitHub Actions workflow fetches latest data, retrains the model, evaluates metrics, and commits updated model artifacts.

---

## 🚀 Getting Started

### Prerequisites

* Docker & Docker Compose
* Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/epl-predictor.git
cd epl-predictor
```

### Step 2: Configuration

```bash
cp .env.example .env
# Edit .env and replace FASTAPI_SECRET_KEY with a strong random string
```

* **Verify Admin Email:** Set `ADMIN_EMAIL` to `anouarguemri1@gmail.com` for rate limit override.
* **Check Data URLs:** Review `backend/ml/data_fetch.py` and ensure URLs correspond to the current EPL season.

### Step 3: Build and Run with Docker Compose

```bash
docker-compose up --build -d
```

* Backend: port 8000
* Frontend: port 3000

### Step 4: Initial Setup (Database & Model Training)

**Train the ML Model:**

```bash
docker-compose exec backend python scripts/train_manual.py
```

**Create Admin User:**

```bash
docker-compose exec backend python scripts/create_admin.py --password [YOUR_ADMIN_PASSWORD]
```

---

## 🌐 Usage and Endpoints

| Service     | Access URL                                     | Documentation                                                          |
| ----------- | ---------------------------------------------- | ---------------------------------------------------------------------- |
| Frontend UI | [http://localhost:3000](http://localhost:3000) | Predict, Simulate, Login                                               |
| Backend API | [http://localhost:8000](http://localhost:8000) | Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs) |

### Prediction Example (After Login)

* **Endpoint:** POST `/predict`
* **Header:** Authorization: Bearer `<JWT_TOKEN>`

**Request Body:**

```json
{
  "home_team": "Manchester City",
  "away_team": "Arsenal"
}
```

**Sample Response:**

```json
{
  "probs": {
    "Home": 0.65,
    "Draw": 0.2,
    "Away": 0.15
  },
  "shap_url": "/admin/shap/uuid_filename.png",
  "features": {
    "Elo_Home": 1950.5,
    "Home_Form_Pts": 2.2,
    "...": "..."
  }
}
```

---

## 🛠️ Development and Operations

### Environment Variables

* `FASTAPI_SECRET_KEY` — JWT signing key
* `ADMIN_EMAIL` — `admin1@mail.com`
* `MODEL_TYPE` — rf, xgb, logreg, or ensemble

### Retraining & Maintenance

**Local Manual Retrain:**

```bash
docker-compose exec backend python scripts/train_manual.py
```

**Admin API Retrain:**
Access protected endpoint via UI or POST `/admin/retrain` using admin JWT.

### Testing and QA

```bash
# Run unit tests
docker-compose exec backend pytest backend/tests

# Run linting (Black and Flake8 via pre-commit)
docker-compose exec backend bash -c "pip install pre-commit && pre-commit run --all-files"
```

### Data and Model Persistence

* Historical CSV data: `backend/data/`
* Trained models & pipelines: `backend/models_store/`
* SHAP plots: `backend/reports/shap/` (served statically)
