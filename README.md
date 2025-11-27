# EPL Match Predictor Platform

A production-ready full-stack application to predict English Premier League match outcomes using Machine Learning (RandomForest, XGBoost, Logistic Regression, Ensemble).

## Features
- **ML Pipeline**: Automated data fetching, Elo calculation, feature engineering, and Optuna hyperparameter tuning.
- **Explainability**: SHAP value integration for prediction transparency.
- **Simulations**: Monte Carlo simulation for match and season outcomes.
- **Security**: JWT Auth, Rate Limiting (30 req/day) with unlimited Admin override.
- **DevOps**: Dockerized, CI/CD via GitHub Actions for daily re-training.

## Installation & Running

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Quick Start (Docker)
1. Clone repo.
2. Copy env: `cp .env.example .env`
3. Build and run:
   ```bash
   docker-compose up --build
4.Access Frontend: http://localhost:3000
5.Access Backend Docs: http://localhost:8000/docs
