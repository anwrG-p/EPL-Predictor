import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from ml.engine import MLEngine
from ml.data_fetch import fetch_data

def simulate_match_outcome(
    home_team: str,
    away_team: str,
    ml_engine: Optional[MLEngine] = None,
    precomputed_probs: Optional[Dict[str, float]] = None
) -> str:
    """Simulates a single match based on predicted probabilities."""
    probs = precomputed_probs
    if probs is None and ml_engine is not None:
        try:
            result = ml_engine.predict_proba(home_team, away_team)
            probs = result['probs']
        except Exception:
            probs = {"Home": 0.45, "Draw": 0.25, "Away": 0.30}
    elif probs is None:
        probs = {"Home": 0.45, "Draw": 0.25, "Away": 0.30}

    outcomes = ['Home', 'Draw', 'Away']
    probabilities = [probs.get('Home', 0.45), probs.get('Draw', 0.25), probs.get('Away', 0.30)]
    probabilities = np.array(probabilities, dtype=float)
    total = probabilities.sum()
    probabilities = probabilities / total if total > 0 else np.array([0.45, 0.25, 0.30])

    return str(np.random.choice(outcomes, p=probabilities))

def simulate_season(ml_engine: MLEngine, rounds: int = 100) -> List[Dict]:
    """Runs Monte Carlo simulation for the remaining season fixtures."""
    raw_df = fetch_data()
    if raw_df.empty:
        return []

    # Filter to current season
    if 'raw_source' in raw_df.columns:
        current_season_df = raw_df[raw_df['raw_source'].str.contains('2425|2324', na=False)]
        if current_season_df.empty:
            current_season_df = raw_df
    else:
        current_season_df = raw_df

    teams = sorted(list(set(current_season_df['HomeTeam']).union(set(current_season_df['AwayTeam']))))
    if not teams:
        return []

    completed_df = current_season_df.dropna(subset=['FTHG', 'FTAG'])
    fixtures_df = current_season_df[current_season_df['FTHG'].isnull() | current_season_df['FTAG'].isnull()]

    # Baseline points from completed matches
    base_standings = {team: {'Pts': 0, 'P': 0} for team in teams}
    for _, row in completed_df.iterrows():
        h_team, a_team, ftr = row['HomeTeam'], row['AwayTeam'], row.get('FTR')
        if ftr == 'H':
            base_standings[h_team]['Pts'] += 3
        elif ftr == 'A':
            base_standings[a_team]['Pts'] += 3
        elif ftr == 'D':
            base_standings[h_team]['Pts'] += 1
            base_standings[a_team]['Pts'] += 1
        base_standings[h_team]['P'] += 1
        base_standings[a_team]['P'] += 1

    # If all matches are completed, return final standings directly
    if fixtures_df.empty:
        ranked = sorted(teams, key=lambda t: base_standings[t]['Pts'], reverse=True)
        return [
            {'Team': team, 'Avg_Final_Rank': float(pos + 1), 'Rounds': rounds}
            for pos, team in enumerate(ranked)
        ]

    # Precompute prediction probabilities once per fixture to keep simulation fast
    unique_fixtures = fixtures_df[['HomeTeam', 'AwayTeam']].drop_duplicates().to_dict(orient='records')
    fixture_probs = {}
    for fix in unique_fixtures:
        h, a = fix['HomeTeam'], fix['AwayTeam']
        try:
            res = ml_engine.predict_proba(h, a)
            fixture_probs[(h, a)] = res['probs']
        except Exception:
            fixture_probs[(h, a)] = {"Home": 0.45, "Draw": 0.25, "Away": 0.30}

    # Run Monte Carlo rounds
    fixture_list = fixtures_df[['HomeTeam', 'AwayTeam']].to_dict(orient='records')
    rank_history = {team: [] for team in teams}

    for _ in range(rounds):
        round_points = {t: base_standings[t]['Pts'] for t in teams}
        for fix in fixture_list:
            h, a = fix['HomeTeam'], fix['AwayTeam']
            probs = fixture_probs.get((h, a), {"Home": 0.45, "Draw": 0.25, "Away": 0.30})
            outcome = simulate_match_outcome(h, a, precomputed_probs=probs)
            if outcome == 'Home':
                round_points[h] += 3
            elif outcome == 'Away':
                round_points[a] += 3
            else:
                round_points[h] += 1
                round_points[a] += 1

        sorted_teams = sorted(teams, key=lambda t: round_points[t], reverse=True)
        for rank, team in enumerate(sorted_teams, start=1):
            rank_history[team].append(rank)

    results = [
        {'Team': team, 'Avg_Final_Rank': float(np.round(np.mean(rank_history[team]), 2)), 'Rounds': rounds}
        for team in teams
    ]
    return sorted(results, key=lambda x: x['Avg_Final_Rank'])
