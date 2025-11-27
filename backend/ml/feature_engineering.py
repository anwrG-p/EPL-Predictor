import pandas as pd
import numpy as np

def calculate_elo(df, k_factor=20, base_rating=1500):
    # Dictionary to hold current ratings
    ratings = {}
    
    elo_home = []
    elo_away = []
    
    # Initialize ratings
    teams = set(df['HomeTeam']).union(set(df['AwayTeam']))
    for team in teams:
        ratings[team] = base_rating
        
    for index, row in df.iterrows():
        h_team = row['HomeTeam']
        a_team = row['AwayTeam']
        
        h_rating = ratings[h_team]
        a_rating = ratings[a_team]
        
        elo_home.append(h_rating)
        elo_away.append(a_rating)
        
        # Calculate expected score
        expected_h = 1 / (1 + 10 ** ((a_rating - h_rating) / 400))
        expected_a = 1 / (1 + 10 ** ((h_rating - a_rating) / 400))
        
        # Actual score (1=win, 0.5=draw, 0=loss)
        if row['FTHG'] > row['FTAG']:
            actual_h, actual_a = 1, 0
        elif row['FTHG'] == row['FTAG']:
            actual_h, actual_a = 0.5, 0.5
        else:
            actual_h, actual_a = 0, 1
            
        # Update ratings
        ratings[h_team] = h_rating + k_factor * (actual_h - expected_h)
        ratings[a_team] = a_rating + k_factor * (actual_a - expected_a)
        
    df['Elo_Home'] = elo_home
    df['Elo_Away'] = elo_away
    return df

def get_recent_form(df, window=5):
    # Calculate points per game for rolling window
    # Create a long-format DF first
    home_stats = df[['Date', 'HomeTeam', 'FTHG', 'FTAG', 'FTR']].rename(
        columns={'HomeTeam': 'Team', 'FTHG': 'GoalsFor', 'FTAG': 'GoalsAgainst'}
    )
    home_stats['Points'] = home_stats['FTR'].map({'H': 3, 'D': 1, 'A': 0})
    home_stats['IsHome'] = 1

    away_stats = df[['Date', 'AwayTeam', 'FTAG', 'FTHG', 'FTR']].rename(
        columns={'AwayTeam': 'Team', 'FTAG': 'GoalsFor', 'FTHG': 'GoalsAgainst'}
    )
    away_stats['Points'] = away_stats['FTR'].map({'A': 3, 'D': 1, 'H': 0})
    away_stats['IsHome'] = 0
    
    all_stats = pd.concat([home_stats, away_stats]).sort_values(['Team', 'Date'])
    
    # Rolling averages
    all_stats['Form_Points'] = all_stats.groupby('Team')['Points'].transform(
        lambda x: x.shift(1).rolling(window, min_periods=1).mean()
    )
    all_stats['Form_GoalsFor'] = all_stats.groupby('Team')['GoalsFor'].transform(
        lambda x: x.shift(1).rolling(window, min_periods=1).mean()
    )
    all_stats['Form_GoalsAgainst'] = all_stats.groupby('Team')['GoalsAgainst'].transform(
        lambda x: x.shift(1).rolling(window, min_periods=1).mean()
    )
    
    # Merge back to main df
    # We need to act carefully to merge back on specific match rows
    # For simplicity in this demo, we re-merge based on Date + Team
    
    df_merged = df.copy()
    
    # Get pre-match stats for Home Team
    h_form = all_stats[all_stats['IsHome'] == 1][['Date', 'Team', 'Form_Points', 'Form_GoalsFor', 'Form_GoalsAgainst']]
    df_merged = df_merged.merge(h_form, left_on=['Date', 'HomeTeam'], right_on=['Date', 'Team'], how='left')
    df_merged = df_merged.rename(columns={'Form_Points': 'Home_Form_Pts', 'Form_GoalsFor': 'Home_Form_GF', 'Form_GoalsAgainst': 'Home_Form_GA'}).drop(columns=['Team'])
    
    # Get pre-match stats for Away Team
    a_form = all_stats[all_stats['IsHome'] == 0][['Date', 'Team', 'Form_Points', 'Form_GoalsFor', 'Form_GoalsAgainst']]
    df_merged = df_merged.merge(a_form, left_on=['Date', 'AwayTeam'], right_on=['Date', 'Team'], how='left')
    df_merged = df_merged.rename(columns={'Form_Points': 'Away_Form_Pts', 'Form_GoalsFor': 'Away_Form_GF', 'Form_GoalsAgainst': 'Away_Form_GA'}).drop(columns=['Team'])
    
    return df_merged.fillna(0)

def prepare_features(df):
    df = calculate_elo(df)
    df = get_recent_form(df)
    
    # Target
    df['Target'] = df['FTR'].map({'H': 0, 'D': 1, 'A': 2})
    
    feature_cols = [
        'Elo_Home', 'Elo_Away', 
        'Home_Form_Pts', 'Away_Form_Pts', 
        'Home_Form_GF', 'Away_Form_GF',
        'Home_Form_GA', 'Away_Form_GA'
    ]
    
    return df, feature_cols
