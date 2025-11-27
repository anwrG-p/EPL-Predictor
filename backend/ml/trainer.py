import optuna
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import log_loss
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
import joblib
import os

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models_store")

def objective_rf(trial, X_train, y_train, tscv):
    n_estimators = trial.suggest_int('n_estimators', 50, 300)
    max_depth = trial.suggest_int('max_depth', 3, 15)
    
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    
    # Time Series Cross-Validation
    logloss_scores = []
    for train_index, val_index in tscv.split(X_train):
        X_tr, X_val = X_train.iloc[train_index], X_train.iloc[val_index]
        y_tr, y_val = y_train.iloc[train_index], y_train.iloc[val_index]
        
        model.fit(X_tr, y_tr)
        preds = model.predict_proba(X_val)
        logloss_scores.append(log_loss(y_val, preds))
        
    return sum(logloss_scores) / len(logloss_scores)

def tune_and_save(X, y, model_name, n_trials=50, study_name="epl_optimization"):
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Optuna setup
    storage_url = f"sqlite:///{os.path.join(MODELS_DIR, 'optuna_study.db')}"
    study = optuna.create_study(direction="minimize", study_name=study_name, storage=storage_url, load_if_exists=True)
    
    if model_name == 'rf':
        objective = lambda trial: objective_rf(trial, X, y, tscv)
    elif model_name == 'xgb':
        # Placeholder for XGB objective (simplified for brevity)
        objective = lambda trial: log_loss(y, XGBClassifier(n_estimators=100, max_depth=trial.suggest_int('max_depth', 3, 10)).fit(X,y).predict_proba(X))
    elif model_name == 'logreg':
        # Placeholder for LogReg objective
        objective = lambda trial: log_loss(y, LogisticRegression(C=trial.suggest_loguniform('C', 1e-3, 1e3), max_iter=1000).fit(X,y).predict_proba(X))
    else:
        raise ValueError(f"Unknown model type: {model_name}")

    study.optimize(objective, n_trials=n_trials)
    
    # Train final model with best params
    best_params = study.best_params
    if model_name == 'rf':
        final_model = RandomForestClassifier(**best_params, random_state=42)
    elif model_name == 'xgb':
        final_model = XGBClassifier(**best_params, use_label_encoder=False, eval_metric='mlogloss')
    elif model_name == 'logreg':
        final_model = LogisticRegression(**best_params, max_iter=1000)

    final_model.fit(X, y)
    joblib.dump(final_model, os.path.join(MODELS_DIR, f"{model_name}_tuned_model.pkl"))
    
    return study.best_value, best_params
