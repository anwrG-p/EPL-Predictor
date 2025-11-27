import sys
import os
import pytest
import pandas as pd
from ml.feature_engineering import prepare_features

def test_feature_engineering():
    # Mock data
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
    # Check Target mapping (H=0, D=1, A=2)
    assert processed_df.iloc[0]['Target'] == 0
    assert processed_df.iloc[1]['Target'] == 1
