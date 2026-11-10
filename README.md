# ⚽ EPL Match Predictor Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg?style=flat&logo=React&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-4.5.x-646CFF.svg?style=flat&logo=Vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.3-38B2AC.svg?style=flat&logo=TailwindCSS&logoColor=white)](https://tailwindcss.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=Docker&logoColor=white)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready, full-stack machine learning platform engineered to predict English Premier League (EPL) football match outcomes with explainable AI (XAI) and Monte Carlo season simulation.

---

## 🏗️ Architecture Overview

The platform uses a modular three-tier architecture connecting a responsive React SPA frontend to an asynchronous FastAPI backend and an MLOps pipeline.

```mermaid
flowchart TD
    subgraph Client["Presentation Layer"]
        UI["React SPA (Vite + TailwindCSS)"]
    end

    subgraph Gateway["API & Application Layer"]
        API["FastAPI Gateway"]
        Auth["JWT Auth & Rate Limiter"]
        Health["System & Admin Health Checks"]
    end

    subgraph ML["Machine Learning & Analytics Engine"]
        Engine["MLEngine (Ensemble / XGBoost / RF / LogReg)"]
        FeatureEngine["Feature Engineering (Elo + Rolling Form)"]
        SHAP["Explainable AI (SHAP Plot Generator)"]
        Sim["Monte Carlo Simulation (Match & Season)"]
    end

    subgraph Data["Persistence & Storage"]
        DB[("SQLite Database via SQLAlchemy")]
        Models["Model Store (.pkl artifacts)"]
        DataCache["Historical CSV Cache"]
    end

    UI -->|"HTTP / REST API"| API
    API --> Auth
    API --> Health
    API --> Engine
    API --> Sim
    Engine --> FeatureEngine
    Engine --> SHAP
    Engine --> Models
    FeatureEngine --> DataCache
    Auth --> DB
    Sim --> Engine
```

---

## ✨ Key Features

- **Multi-Model Support:** Choose between **RandomForest**, **XGBoost**, **Logistic Regression**, or an **Ensemble Average** of all three.
- **Dynamic Feature Engineering:** Computes dynamic Elo ratings and rolling team form (points per game, goals scored, goals conceded) from multi-season match histories.
- **Explainable AI (XAI):** Integrated **SHAP** (SHapley Additive exPlanations) generates visual bar charts showing the exact feature contributions for each prediction.
- **Monte Carlo Simulations:**
  - `/simulate-match`: Simulates probabilistic match outcomes across 100 iterations.
  - `/simulate-season`: Simulates remaining league fixtures across customizable rounds (up to 500) to project final standings.
- **Security & Rate Limiting:** JWT-based user authentication with a built-in rate limit (30 requests/day per standard user) and admin bypass.
- **Automated MLOps Retraining:** Scheduled GitHub Actions workflow retrains the model on fresh league data and commits updated model artifacts.
- **Extensible Agent Skills:** Includes 45 modular agent skills under `.agents/skills/` (featuring [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) and [mattpocock/skills](https://github.com/mattpocock/skills)).

---

## 🚀 Quickstart with Docker Compose

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- [Git](https://git-scm.com/)

### 1. Clone the Repository
```bash
git clone https://github.com/anwrG-p/EPL-Predictor.git
cd EPL-Predictor
```

### 2. Configure Environment
Copy the example environment file:
```bash
cp .env.example .env
```
*(Optional: edit `.env` to set your custom `SECRET_KEY` and `ADMIN_EMAIL`)*

### 3. Launch Services
```bash
docker-compose up --build -d
```
The services will be available at:
- **Frontend Web UI:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Initialize Model & Admin User
Run the setup commands inside the backend container:

```bash
# 1. Train the initial ML model artifacts
docker-compose exec backend python scripts/train_manual.py

# 2. Create the administrator account
docker-compose exec backend python scripts/create_admin.py --password YourSecurePassword123!
```

---

## 🌐 API Reference

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/register` | Public | Register a new user account |
| `POST` | `/token` | Public | Obtain JWT bearer token (returns `access_token` and `is_admin`) |
| `GET` | `/health` | Public | Service health check |
| `POST` | `/predict` | Authenticated | Generate match outcome probabilities & SHAP explanation URL |
| `POST` | `/simulate-match` | Authenticated | Run Monte Carlo match simulation (100 rounds) |
| `GET` | `/simulate-season` | Authenticated | Run Monte Carlo season simulation (query param: `rounds`) |
| `GET` | `/admin/health` | Admin | Health monitor for the Admin Panel dashboard |
| `POST` | `/admin/retrain` | Admin | Trigger background model retraining pipeline |
| `GET` | `/admin/stats` | Admin | View platform usage statistics |

### Prediction Request Example

**POST** `/predict`  
**Header:** `Authorization: Bearer <JWT_TOKEN>`

```json
{
  "home_team": "Manchester City",
  "away_team": "Arsenal"
}
```

**Response:**
```json
{
  "probs": {
    "Home": 0.52,
    "Draw": 0.26,
    "Away": 0.22
  },
  "shap_url": "/admin/shap/man_city_vs_arsenal.png",
  "features": {
    "Elo_Home": 1940.2,
    "Elo_Away": 1895.8,
    "Home_Form_Pts": 2.4,
    "Away_Form_Pts": 2.0,
    "Home_Form_GF": 2.2,
    "Away_Form_GF": 1.8,
    "Home_Form_GA": 0.8,
    "Away_Form_GA": 1.0
  }
}
```

---

## ⚙️ Configuration (`.env`)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | `super_secure_random_string...` | Secret key used for signing JWT tokens |
| `ALGORITHM` | `HS256` | JWT cryptographic algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token expiration period in minutes (default: 24h) |
| `DATABASE_URL` | `sqlite:///./data/backend.db` | SQLAlchemy database connection URI |
| `ADMIN_EMAIL` | `admin@email.com` | Email granted admin override and unlimited rate limits |
| `MODEL_TYPE` | `ensemble` | Selected model: `rf`, `xgb`, `logreg`, or `ensemble` |

---

## 🧪 Local Development & Testing

### Backend Unit Tests
```bash
# Using local Python environment
pytest backend/tests

# Or inside Docker
docker-compose exec backend pytest tests
```

### Frontend Build
```bash
cd frontend
npm install
npm run build
```

---

## 🤖 Agent Skills Installed

This repository is equipped with agent skills managed via [skills-lock.json](skills-lock.json):
- **Ponytail Suite:** `ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`, `ponytail-review`.
- **Engineering & Architecture:** `code-review`, `codebase-design`, `diagnosing-bugs`, `domain-modeling`, `tdd`, `to-spec`, `to-tickets`, `wayfinder`.
- **Productivity & Review:** `ask-matt`, `grill-me`, `grill-with-docs`, `handoff`, `writing-for-agents`.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
