from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    home_team = Column(String)
    away_team = Column(String)
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    ftr = Column(String) # Full Time Result (H, D, A)
    raw_source = Column(String) # e.g., 'E0.csv'

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    match_id = Column(Integer, nullable=True) # If linked to a real future match
    home_team = Column(String)
    away_team = Column(String)
    probs_json = Column(JSON) # {"H": 0.5, "D": 0.2, "A": 0.3}
    features_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RateLimit(Base):
    __tablename__ = "rate_limits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    date = Column(String) # YYYY-MM-DD
    requests_count = Column(Integer, default=0)

class RetrainLog(Base):
    __tablename__ = "retrain_logs"
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    metrics_json = Column(JSON) # Accuracy, LogLoss etc
