from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    match_id = Column(Integer, nullable=True)
    home_team = Column(String)
    away_team = Column(String)
    probs_json = Column(JSON)
    features_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RateLimit(Base):
    __tablename__ = "rate_limits"
    __table_args__ = (UniqueConstraint('user_id', 'date', name='uq_user_date'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    date = Column(String) # YYYY-MM-DD
    requests_count = Column(Integer, default=0)
