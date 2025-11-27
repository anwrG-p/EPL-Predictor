from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import os

from . import models, schemas, auth, database, middleware
from .config import settings
from ml.engine import MLEngine

# Create Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="EPL Predictor")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for SHAP
SHAP_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "shap")
os.makedirs(SHAP_PATH, exist_ok=True)
app.mount("/admin/shap", StaticFiles(directory=SHAP_PATH), name="shap")
=== FILE: backend/app/main.py (SIMULATION ROUTES APPENDED) ===
# ... existing imports and app setup ...

# --- Simulation Routes ---
@app.post("/simulate-match", response_model=schemas.SimulationMatchResponse)
def simulate_match(
    request: schemas.PredictionRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # Rate Limit
    middleware.check_rate_limit(current_user, db)
    
    # We run the simulation multiple times for robust results
    results = [utils.simulate_match_outcome(request.home_team, request.away_team, ml_engine) for _ in range(100)]
    
    counts = pd.Series(results).value_counts(normalize=True).to_dict()
    
    return {
        "home_team": request.home_team,
        "away_team": request.away_team,
        "sim_probs": {
            "Home": counts.get('Home', 0), 
            "Draw": counts.get('Draw', 0), 
            "Away": counts.get('Away', 0)
        }
    }

@app.get("/simulate-season", response_model=List[schemas.SimulationSeasonResponse])
def simulate_season_endpoint(
    rounds: int = 100,
    current_user: models.User = Depends(auth.get_current_user)
):
    if rounds > 500:
        raise HTTPException(status_code=400, detail="Max 500 rounds allowed for season simulation.")
    
    results = utils.simulate_season(ml_engine, rounds=rounds)
    return results

# ... existing admin routes ...
# Initialize ML Engine
ml_engine = MLEngine(model_type=settings.MODEL_TYPE)

# --- Auth Routes ---
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
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
    # Rate Limit
    middleware.check_rate_limit(current_user, db)
    
    try:
        result = ml_engine.predict_proba(request.home_team, request.away_team)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Save Prediction
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

# --- Admin Routes ---
@app.post("/admin/retrain")
def retrain_model(current_user: models.User = Depends(auth.get_current_admin)):
    metrics = ml_engine.train()
    # Reload model in memory
    ml_engine.load_model()
    return {"message": "Model retrained", "metrics": metrics}

@app.get("/admin/stats")
def get_stats(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_admin)):
    count = db.query(models.Prediction).count()
    return {"total_predictions": count}
