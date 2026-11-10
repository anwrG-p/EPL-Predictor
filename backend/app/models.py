from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    home_team = Column(String)
    away_team = Column(String)
    probs_json = Column(JSON)
    features_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
