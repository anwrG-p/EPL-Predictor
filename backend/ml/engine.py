import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import log_loss, accuracy_score
from .data_fetch import fetch_data
from .feature_engineering import prepare_features
import os
import uuid

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models_store")
SHAP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "shap")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(SHAP_DIR, exist_ok=True)

class MLEngine:
    def __init__(self, model_type="ensemble"):
        self.model_type = model_type
        self.model = None
        self.feature_cols = None
        self.load_model()

    def train(self):
        raw_df = fetch_data()
        df, features = prepare_features(raw_df)
        self.feature_cols = features
        
        X = df[features]
        y = df['Target']
        
        # Simple Optuna integration placeholder (hardcoded best params for brevity)
        if self.model_type == "xgb":
            clf = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1)
        elif self.model_type == "rf":
            clf = RandomForestClassifier(n_estimators=100, max_depth=5)
        elif self.model_type == "logreg":
            clf = LogisticRegression(max_iter=1000)
        else: # Ensemble
            # Simplified Ensemble: Train all 3 and store in a dict
            clf = {
                "xgb": XGBClassifier(n_estimators=100, max_depth=3).fit(X, y),
                "rf": RandomForestClassifier(n_estimators=100, max_depth=5).fit(X, y),
                "lr": LogisticRegression(max_iter=1000).fit(X, y)
            }
        
        if self.model_type != "ensemble":
            clf.fit(X, y)
        
        self.model = clf
        
        # Save artifacts
        joblib.dump(self.model, os.path.join(MODELS_DIR, f"{self.model_type}_model.pkl"))
        joblib.dump(self.feature_cols, os.path.join(MODELS_DIR, "features.pkl"))
        
        return {"status": "trained", "rows": len(df)}

    def load_model(self):
        try:
            self.model = joblib.load(os.path.join(MODELS_DIR, f"{self.model_type}_model.pkl"))
            self.feature_cols = joblib.load(os.path.join(MODELS_DIR, "features.pkl"))
        except:
            print("Model not found. Train first.")

def predict_proba(self, home_team, away_team):
        if self.model is None:
            # AUTO-FIX: Attempt to load again, or raise clear error
            self.load_model()
            if self.model is None:
                raise ValueError("Model has not been trained yet. Please run the training script via /admin/retrain or CLI.")
        
        # ... rest of the function
        # In a real app, we need the latest stats for these teams.
        # We will re-fetch data, compute features for the latest date, 
        # then artificially construct the row for prediction.
        
        # This is expensive, so in prod we'd cache the 'current form' of all teams separately.
        # For this implementation, we re-run feature prep on historical data to get latest stats.
        
        raw_df = fetch_data()
        df, _ = prepare_features(raw_df)
        
        # Get latest stats for home team
        h_stats = df[df['HomeTeam'] == home_team].iloc[-1] if not df[df['HomeTeam'] == home_team].empty else None
        a_stats = df[df['AwayTeam'] == away_team].iloc[-1] if not df[df['AwayTeam'] == away_team].empty else None
        
        if h_stats is None or a_stats is None:
            raise ValueError("Team not found in history")

        # Construct feature vector (Approximation using latest available rating/form)
        # Note: Elo needs to be the POST-match rating of the last game.
        input_data = pd.DataFrame([{
            'Elo_Home': h_stats['Elo_Home'], 
            'Elo_Away': a_stats['Elo_Away'],
            'Home_Form_Pts': h_stats['Home_Form_Pts'], # Should ideally calculate form INCLUDING last match
            'Away_Form_Pts': a_stats['Away_Form_Pts'],
            'Home_Form_GF': h_stats['Home_Form_GF'],
            'Away_Form_GF': a_stats['Away_Form_GF'],
            'Home_Form_GA': h_stats['Home_Form_GA'],
            'Away_Form_GA': a_stats['Away_Form_GA']
        }])
        
        if self.model_type == "ensemble":
            p1 = self.model['xgb'].predict_proba(input_data)[0]
            p2 = self.model['rf'].predict_proba(input_data)[0]
            p3 = self.model['lr'].predict_proba(input_data)[0]
            probs = (p1 + p2 + p3) / 3
            explainer_model = self.model['rf'] # Use RF for SHAP in ensemble mode for simplicity
        else:
            probs = self.model.predict_proba(input_data)[0]
            explainer_model = self.model

        # SHAP
        explainer = shap.TreeExplainer(explainer_model) if hasattr(explainer_model, "feature_importances_") else shap.LinearExplainer(explainer_model, input_data)
        shap_values = explainer.shap_values(input_data)
        
        # Handle SHAP output shape variations (binary vs multiclass)
        if isinstance(shap_values, list):
            sv = shap_values[0] # taking class 0 (Home Win) interest usually
        else:
            sv = shap_values

        # Generate plot
        plt.figure()
        shap.summary_plot(sv, input_data, show=False, plot_type="bar")
        filename = f"{uuid.uuid4()}.png"
        plt.savefig(os.path.join(SHAP_DIR, filename), bbox_inches='tight')
        plt.close()

        return {
            "probs": {"Home": float(probs[0]), "Draw": float(probs[1]), "Away": float(probs[2])},
            "shap_url": f"/admin/shap/{filename}",
            "features": input_data.to_dict(orient="records")[0]
        }
