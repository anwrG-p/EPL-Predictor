import pytest
import pandas as pd
from ml.feature_engineering import prepare_features
from ml.engine import MLEngine, normalize_team_name
from app.utils import simulate_match_outcome, simulate_season

def test_feature_engineering():
    data = {
        'Date': ['01/01/2023', '08/01/2023'],
        'HomeTeam': ['TeamA', 'TeamB'],
        'AwayTeam': ['TeamB', 'TeamA'],
        'FTHG': [1, 2],
        'FTAG': [0, 2],
        'FTR': ['H', 'D']
    }
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

    processed_df, features = prepare_features(df)

    assert 'Elo_Home' in processed_df.columns
    assert 'Home_Form_Pts' in processed_df.columns
    assert 'Target' in processed_df.columns
    assert processed_df.iloc[0]['Target'] == 0
    assert processed_df.iloc[1]['Target'] == 1

def test_team_normalization():
    assert normalize_team_name("Manchester City") == "Man City"
    assert normalize_team_name("  Manchester United  ") == "Man United"
    assert normalize_team_name("Arsenal") == "Arsenal"

def test_ml_engine_has_predict_method():
    engine = MLEngine(model_type="rf")
    assert hasattr(engine, "predict_proba")
    assert callable(getattr(engine, "predict_proba"))

def test_simulate_match_outcome_sampling():
    probs = {"Home": 0.9, "Draw": 0.05, "Away": 0.05}
    outcomes = [simulate_match_outcome("TeamA", "TeamB", precomputed_probs=probs) for _ in range(50)]
    assert "Home" in outcomes
    assert all(o in ["Home", "Draw", "Away"] for o in outcomes)
