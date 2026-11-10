import os
import re
import uuid
import joblib
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shap

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression

from .data_fetch import fetch_data
from .feature_engineering import prepare_features

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models_store")
SHAP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "shap")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(SHAP_DIR, exist_ok=True)

# Common team name aliases to handle varied client inputs
TEAM_ALIASES = {
    "manchester city": "Man City",
    "manchester united": "Man United",
    "nottingham forest": "Nott'm Forest",
    "wolverhampton wanderers": "Wolves",
    "wolverhampton": "Wolves",
    "tottenham hotspur": "Tottenham",
    "brighton and hove albion": "Brighton",
    "west ham united": "West Ham",
    "newcastle united": "Newcastle",
    "sheffield utd": "Sheffield United",
}

def normalize_team_name(name: str) -> str:
    cleaned = name.strip()
    return TEAM_ALIASES.get(cleaned.lower(), cleaned)

def _get_team_stats(df: pd.DataFrame, team: str):
    matches = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)]
    if matches.empty:
        return None
    last = matches.iloc[-1]
    if last['HomeTeam'] == team:
        return {
            'Elo': last.get('Elo_Home', 1500),
            'Form_Pts': last.get('Home_Form_Pts', 1.0),
            'Form_GF': last.get('Home_Form_GF', 1.0),
            'Form_GA': last.get('Home_Form_GA', 1.0),
        }
    else:
        return {
            'Elo': last.get('Elo_Away', 1500),
            'Form_Pts': last.get('Away_Form_Pts', 1.0),
            'Form_GF': last.get('Away_Form_GF', 1.0),
            'Form_GA': last.get('Away_Form_GA', 1.0),
        }

class MLEngine:
    def __init__(self, model_type="ensemble"):
        self.model_type = model_type
        self.model = None
        self.feature_cols = None
        self.prepared_df = None
        self.load_model()

    def train(self):
        raw_df = fetch_data(force_refresh=True)
        df, features = prepare_features(raw_df)
        self.feature_cols = features
        self.prepared_df = df

        X = df[features]
        y = df['Target']

        if self.model_type == "xgb":
            clf = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, eval_metric='mlogloss')
        elif self.model_type == "rf":
            clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        elif self.model_type == "logreg":
            clf = LogisticRegression(max_iter=1000)
        else: # Ensemble
            clf = {
                "xgb": XGBClassifier(n_estimators=100, max_depth=3, eval_metric='mlogloss').fit(X, y),
                "rf": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42).fit(X, y),
                "lr": LogisticRegression(max_iter=1000).fit(X, y)
            }

        if self.model_type != "ensemble":
            clf.fit(X, y)

        self.model = clf

        # Save artifacts
        joblib.dump(self.model, os.path.join(MODELS_DIR, f"{self.model_type}_model.pkl"))
        joblib.dump(self.feature_cols, os.path.join(MODELS_DIR, "features.pkl"))
        joblib.dump(self.prepared_df, os.path.join(MODELS_DIR, "prepared_df.pkl"))

        return {"status": "trained", "rows": len(df)}

    def load_model(self):
        model_path = os.path.join(MODELS_DIR, f"{self.model_type}_model.pkl")
        features_path = os.path.join(MODELS_DIR, "features.pkl")
        cached_df_path = os.path.join(MODELS_DIR, "prepared_df.pkl")

        if os.path.exists(model_path) and os.path.exists(features_path):
            try:
                self.model = joblib.load(model_path)
                self.feature_cols = joblib.load(features_path)
                if os.path.exists(cached_df_path):
                    self.prepared_df = joblib.load(cached_df_path)
            except Exception as e:
                print(f"Error loading model artifacts: {e}")
        else:
            print("Model artifacts not found on disk. Training required.")

    def predict_proba(self, home_team: str, away_team: str):
        if self.model is None:
            self.load_model()
            if self.model is None:
                raise ValueError("Model has not been trained yet. Please train the model first.")

        home_clean = normalize_team_name(home_team)
        away_clean = normalize_team_name(away_team)

        # Use cached dataframe or compute once
        if self.prepared_df is None or self.prepared_df.empty:
            raw_df = fetch_data()
            if raw_df.empty:
                raise ValueError("No historical match data available to extract team stats.")
            self.prepared_df, _ = prepare_features(raw_df)

        h_stats = _get_team_stats(self.prepared_df, home_clean)
        a_stats = _get_team_stats(self.prepared_df, away_clean)

        if h_stats is None:
            raise ValueError(f"Home team '{home_team}' not found in match history.")
        if a_stats is None:
            raise ValueError(f"Away team '{away_team}' not found in match history.")

        input_data = pd.DataFrame([{
            'Elo_Home': h_stats['Elo'],
            'Elo_Away': a_stats['Elo'],
            'Home_Form_Pts': h_stats['Form_Pts'],
            'Away_Form_Pts': a_stats['Form_Pts'],
            'Home_Form_GF': h_stats['Form_GF'],
            'Away_Form_GF': a_stats['Form_GF'],
            'Home_Form_GA': h_stats['Form_GA'],
            'Away_Form_GA': a_stats['Form_GA'],
        }])

        if self.model_type == "ensemble":
            p1 = self.model['xgb'].predict_proba(input_data)[0]
            p2 = self.model['rf'].predict_proba(input_data)[0]
            p3 = self.model['lr'].predict_proba(input_data)[0]
            probs = (p1 + p2 + p3) / 3
            explainer_model = self.model['rf']
        else:
            probs = self.model.predict_proba(input_data)[0]
            explainer_model = self.model

        # SHAP plot generation with fixed filenames to prevent disk leaks
        safe_home = re.sub(r'[^a-zA-Z0-9]', '_', home_clean.lower())
        safe_away = re.sub(r'[^a-zA-Z0-9]', '_', away_clean.lower())
        filename = f"{safe_home}_vs_{safe_away}.png"
        shap_filepath = os.path.join(SHAP_DIR, filename)

        try:
            explainer = shap.TreeExplainer(explainer_model) if hasattr(explainer_model, "feature_importances_") else shap.LinearExplainer(explainer_model, input_data)
            shap_values = explainer.shap_values(input_data)
            sv = shap_values[0] if isinstance(shap_values, list) else shap_values

            fig = plt.figure(figsize=(6, 4))
            shap.summary_plot(sv, input_data, show=False, plot_type="bar")
            plt.tight_layout()
            plt.savefig(shap_filepath, bbox_inches='tight')
            plt.close('all')
        except Exception as shap_err:
            plt.close('all')
            print(f"SHAP explanation generation skipped: {shap_err}")

        return {
            "probs": {
                "Home": float(probs[0]),
                "Draw": float(probs[1]),
                "Away": float(probs[2])
            },
            "shap_url": f"/admin/shap/{filename}",
            "features": input_data.to_dict(orient="records")[0]
        }
