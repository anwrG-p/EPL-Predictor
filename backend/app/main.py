import os
from typing import List
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import Depends
from sqlalchemy.orm import Session

from . import models, schemas, database, utils
from .config import settings
from ml.engine import MLEngine

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="EPL Predictor")

# Global ML Engine instance
ml_engine = MLEngine(model_type=settings.MODEL_TYPE)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for SHAP explanation charts
SHAP_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "shap")
os.makedirs(SHAP_PATH, exist_ok=True)
app.mount("/admin/shap", StaticFiles(directory=SHAP_PATH), name="shap")

# --- System Health Routes ---
@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.get("/admin/health")
def admin_health_check():
    return {"status": "OK"}

# --- Prediction Routes ---
@app.post("/predict", response_model=schemas.PredictionResponse)
def predict_match(
    request: schemas.PredictionRequest,
    db: Session = Depends(database.get_db)
):
    try:
        result = ml_engine.predict_proba(request.home_team, request.away_team)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    pred = models.Prediction(
        home_team=request.home_team,
        away_team=request.away_team,
        probs_json=result['probs'],
        features_json=result['features']
    )
    db.add(pred)
    db.commit()

    return result

# --- Simulation Routes ---
@app.post("/simulate-match", response_model=schemas.SimulationMatchResponse)
def simulate_match(request: schemas.PredictionRequest):
    try:
        pred_res = ml_engine.predict_proba(request.home_team, request.away_team)
        probs = pred_res['probs']
    except Exception:
        probs = {"Home": 0.45, "Draw": 0.25, "Away": 0.30}

    outcomes = ['Home', 'Draw', 'Away']
    probabilities = [probs['Home'], probs['Draw'], probs['Away']]
    probabilities = np.array(probabilities, dtype=float)
    total = probabilities.sum()
    probabilities = probabilities / total if total > 0 else np.array([0.45, 0.25, 0.30])

    samples = np.random.choice(outcomes, size=100, p=probabilities)
    counts = pd.Series(samples).value_counts(normalize=True).to_dict()

    return {
        "home_team": request.home_team,
        "away_team": request.away_team,
        "sim_probs": {
            "Home": float(counts.get('Home', 0.0)),
            "Draw": float(counts.get('Draw', 0.0)),
            "Away": float(counts.get('Away', 0.0))
        }
    }

@app.get("/simulate-season", response_model=List[schemas.SimulationSeasonResponse])
def simulate_season_endpoint(rounds: int = 100):
    if rounds > 500:
        raise HTTPException(status_code=400, detail="Max 500 rounds allowed for season simulation.")

    results = utils.simulate_season(ml_engine, rounds=rounds)
    return results

# --- Admin Routes ---
@app.post("/admin/retrain")
def retrain_model():
    try:
        metrics = ml_engine.train()
        ml_engine.load_model()
        return {"message": "Model retrained", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

@app.get("/admin/stats")
def get_stats(db: Session = Depends(database.get_db)):
    count = db.query(models.Prediction).count()
    return {"total_predictions": count}
