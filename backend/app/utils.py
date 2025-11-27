import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from ml.engine import MLEngine
from ml.data_fetch import fetch_data
from ml.feature_engineering import prepare_features
from app.config import settings

def simulate_match_outcome(home_team: str, away_team: str, ml_engine: MLEngine) -> str:
    """Simulates a single match based on predicted probabilities."""
    try:
        result = ml_engine.predict_proba(home_team, away_team)
        probs = result['probs']
    except Exception:
        # Fallback to pure random if model fails (e.g., initial run)
        probs = {"Home": 0.4, "Draw": 0.3, "Away": 0.3}

    outcomes = ['Home', 'Draw', 'Away']
    probabilities = [probs['Home'], probs['Draw'], probs['Away']]
    
    # Normalize probabilities just in case
    probabilities = np.array(probabilities) / sum(probabilities)
    
    # Monte Carlo selection
    return np.random.choice(outcomes, p=probabilities)

def simulate_season(ml_engine: MLEngine, rounds: int = 100) -> List[Dict]:
    """Runs Monte Carlo simulation for the remaining season fixtures."""
    
    # 1. Fetch current league data (simplification: assume 'current' means the last match in history)
    raw_df = fetch_data()
    
    # Identify unique teams and initialize table
    teams = sorted(list(set(raw_df['HomeTeam']).union(set(raw_df['AwayTeam']))))
    
    # Identify remaining fixtures (this is the tricky part without a 'future fixtures' source)
    # SIMPLE APPROACH: Assume current season is in E0.csv and find rows where FTHG/FTAG are null
    
    current_season_df = raw_df[raw_df['raw_source'].str.contains('2324', na=False)] 
    
    # Filter for completed matches (where scores are available)
    completed_df = current_season_df.dropna(subset=['FTHG', 'FTAG'])
    # Remaining fixtures (where scores are NaN)
    fixtures_df = current_season_df[current_season_df['FTHG'].isnull() | current_season_df['FTAG'].isnull()]

    if fixtures_df.empty:
        # Fallback: if data is fully updated, assume the next round is fixtures. 
        # For simplicity, we skip if no remaining fixtures are found.
        return [{"message": "Season complete, no remaining fixtures to simulate."}]

    final_standings = []
    
    # Monte Carlo Rounds
    for _ in range(rounds):
        temp_standings = {team: {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0} for team in teams}
        
        # Start standings from completed matches
        for _, row in completed_df.iterrows():
            ftr = row['FTR']
            h_pts, a_pts = 0, 0
            if ftr == 'H': h_pts, a_pts = 3, 0
            elif ftr == 'A': h_pts, a_pts = 0, 3
            elif ftr == 'D': h_pts, a_pts = 1, 1

            temp_standings[row['HomeTeam']]['P'] += 1
            temp_standings[row['AwayTeam']]['P'] += 1
            temp_standings[row['HomeTeam']]['Pts'] += h_pts
            temp_standings[row['AwayTeam']]['Pts'] += a_pts
            
        
        # Simulate remaining matches
        for _, fixture in fixtures_df.iterrows():
            h_team = fixture['HomeTeam']
            a_team = fixture['AwayTeam']
            
            # Predict outcome using the model
            outcome = simulate_match_outcome(h_team, a_team, ml_engine)
            
            h_pts, a_pts = 0, 0
            if outcome == 'Home': h_pts, a_pts = 3, 0
            elif outcome == 'Away': h_pts, a_pts = 0, 3
            elif outcome == 'Draw': h_pts, a_pts = 1, 1
            
            # Update points (P is handled by completed matches, but needs update for remaining)
            temp_standings[h_team]['P'] += 1
            temp_standings[a_team]['P'] += 1
            temp_standings[h_team]['Pts'] += h_pts
            temp_standings[a_team]['Pts'] += a_pts
        
        # Convert to list and sort
        round_result = sorted([{'Team': t, 'Pts': d['Pts'], 'Pos': 0} for t, d in temp_standings.items()], key=lambda x: x['Pts'], reverse=True)
        for i, team_data in enumerate(round_result):
            team_data['Pos'] = i + 1
            
        final_standings.append(round_result)

    # Aggregate: Calculate average final rank for each team
    rank_aggregation = {team: [] for team in teams}
    for standings in final_standings:
        for team_data in standings:
            rank_aggregation[team_data['Team']].append(team_data['Pos'])
            
    final_output = []
    for team in teams:
        avg_rank = np.mean(rank_aggregation[team])
        final_output.append({'Team': team, 'Avg_Final_Rank': avg_rank, 'Rounds': rounds})
        
    return sorted(final_output, key=lambda x: x['Avg_Final_Rank'])
