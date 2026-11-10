from pydantic import BaseModel
from typing import Dict, Any

class PredictionRequest(BaseModel):
    home_team: str
    away_team: str

class PredictionResponse(BaseModel):
    probs: Dict[str, float]
    shap_url: str
    features: Dict[str, Any]

class SimulationMatchResponse(BaseModel):
    home_team: str
    away_team: str
    sim_probs: Dict[str, float]

class SimulationSeasonResponse(BaseModel):
    Team: str
    Avg_Final_Rank: float
    Rounds: int
