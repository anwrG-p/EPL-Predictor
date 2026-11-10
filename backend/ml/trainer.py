import os
import joblib
import optuna
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import log_loss
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models_store")
os.makedirs(MODELS_DIR, exist_ok=True)

def _cross_validate_model(model, X_train, y_train, tscv):
    logloss_scores = []
    for train_index, val_index in tscv.split(X_train):
        X_tr, X_val = X_train.iloc[train_index], X_train.iloc[val_index]
        y_tr, y_val = y_train.iloc[train_index], y_train.iloc[val_index]

        model.fit(X_tr, y_tr)
        preds = model.predict_proba(X_val)
        logloss_scores.append(log_loss(y_val, preds))

    return sum(logloss_scores) / len(logloss_scores)

def objective_rf(trial, X_train, y_train, tscv):
    n_estimators = trial.suggest_int('n_estimators', 50, 300)
    max_depth = trial.suggest_int('max_depth', 3, 15)
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    return _cross_validate_model(model, X_train, y_train, tscv)

def objective_xgb(trial, X_train, y_train, tscv):
    max_depth = trial.suggest_int('max_depth', 3, 10)
    learning_rate = trial.suggest_float('learning_rate', 0.01, 0.3, log=True)
    model = XGBClassifier(n_estimators=100, max_depth=max_depth, learning_rate=learning_rate, eval_metric='mlogloss')
    return _cross_validate_model(model, X_train, y_train, tscv)

def objective_logreg(trial, X_train, y_train, tscv):
    C = trial.suggest_float('C', 1e-3, 1e3, log=True)
    model = LogisticRegression(C=C, max_iter=1000)
    return _cross_validate_model(model, X_train, y_train, tscv)

def tune_and_save(X, y, model_name, n_trials=50, study_name="epl_optimization"):
    tscv = TimeSeriesSplit(n_splits=5)

    storage_url = f"sqlite:///{os.path.join(MODELS_DIR, 'optuna_study.db')}"
    study = optuna.create_study(direction="minimize", study_name=study_name, storage=storage_url, load_if_exists=True)

    if model_name == 'rf':
        objective = lambda trial: objective_rf(trial, X, y, tscv)
    elif model_name == 'xgb':
        objective = lambda trial: objective_xgb(trial, X, y, tscv)
    elif model_name == 'logreg':
        objective = lambda trial: objective_logreg(trial, X, y, tscv)
    else:
        raise ValueError(f"Unknown model type: {model_name}")

    study.optimize(objective, n_trials=n_trials)

    best_params = study.best_params
    if model_name == 'rf':
        final_model = RandomForestClassifier(**best_params, random_state=42)
    elif model_name == 'xgb':
        final_model = XGBClassifier(**best_params, eval_metric='mlogloss')
    elif model_name == 'logreg':
        final_model = LogisticRegression(**best_params, max_iter=1000)

    final_model.fit(X, y)
    # Save standard filename so MLEngine.load_model picks it up immediately
    joblib.dump(final_model, os.path.join(MODELS_DIR, f"{model_name}_model.pkl"))

    return study.best_value, best_params
