from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    is_admin: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

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
