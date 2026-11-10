import os
from typing import List
import numpy as np
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas, auth, database, middleware, utils
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
def admin_health_check(current_user: models.User = Depends(auth.get_current_admin)):
    return {"status": "OK"}

# --- Auth Routes ---
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = auth.create_access_token(data={"sub": user.email})
    is_admin = bool(user.is_admin or user.email == settings.ADMIN_EMAIL)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_admin": is_admin
    }

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    is_admin = bool(user.email == settings.ADMIN_EMAIL)
    new_user = models.User(email=user.email, hashed_password=hashed_password, is_admin=is_admin)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- Prediction Routes ---
@app.post("/predict", response_model=schemas.PredictionResponse)
def predict_match(
    request: schemas.PredictionRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    middleware.check_rate_limit(current_user, db)

    try:
        result = ml_engine.predict_proba(request.home_team, request.away_team)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    pred = models.Prediction(
        user_id=current_user.id,
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
def simulate_match(
    request: schemas.PredictionRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    middleware.check_rate_limit(current_user, db)

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
def simulate_season_endpoint(
    rounds: int = 100,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if rounds > 500:
        raise HTTPException(status_code=400, detail="Max 500 rounds allowed for season simulation.")

    middleware.check_rate_limit(current_user, db)
    results = utils.simulate_season(ml_engine, rounds=rounds)
    return results

# --- Admin Routes ---
@app.post("/admin/retrain")
def retrain_model(current_user: models.User = Depends(auth.get_current_admin)):
    try:
        metrics = ml_engine.train()
        ml_engine.load_model()
        return {"message": "Model retrained", "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")

@app.get("/admin/stats")
def get_stats(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_admin)
):
    count = db.query(models.Prediction).count()
    return {"total_predictions": count}
