"""Entrena Churn Score (7d) y Conversion Score (30d) con RandomForest.

Anti-leakage: `days_since_last_session` se excluye siempre. `device` en leads
es un identificador aleatorio y también se excluye.
"""
import sqlite3, json, pickle, pandas as pd, numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, average_precision_score, confusion_matrix)
from sklearn.preprocessing import LabelEncoder
import os

DB_PATH = "data/playnova_games.db"
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

EXCLUDE = {'player_id', 'lead_id', 'churn_d7', 'converted_30d',
           'days_since_last_session', 'device'}

def load_player_features():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM player_features", conn)
    conn.close()
    return df

def load_leads_features():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT l.tutorial_completed, l.session_1_length, l.friends_invited,
               l.days_to_session_2, l.converted_30d, l.country, l.os,
               c.channel as acquisition_channel
        FROM leads l
        JOIN campaigns c ON l.campaign_id = c.campaign_id
    """, conn)
    conn.close()
    return df

def encode_frame(df, feature_cols, encoders=None):
    X = df[feature_cols].copy()
    if encoders is None:
        encoders = {}
        for col in X.select_dtypes(include=['object', 'string']).columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le.classes_.tolist()
    else:
        for col, classes in encoders.items():
            if col in X.columns:
                mapping = {v: i for i, v in enumerate(classes)}
                X[col] = X[col].astype(str).map(mapping).fillna(-1).astype(int)
    return X, encoders

def best_threshold(y_true, y_prob):
    best = (0.5, -1)
    for t in [round(x, 2) for x in np.arange(0.15, 0.86, 0.05)]:
        pred = (y_prob >= t).astype(int)
        f1 = f1_score(y_true, pred, zero_division=0)
        if f1 > best[1]:
            best = (t, f1)
    return best[0]

def build_model(df, target_col, model_name, tune_threshold=False):
    feature_cols = [c for c in df.columns if c not in EXCLUDE and c != target_col]
    y = df[target_col].copy()
    X_raw = df[feature_cols]
    X, encoders = encode_frame(df, feature_cols)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=300, max_depth=12, min_samples_leaf=5,
                                   class_weight='balanced_subsample', random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)[:, 1]
    thr = best_threshold(y_test, y_prob) if tune_threshold else 0.5
    y_pred = (y_prob >= thr).astype(int)

    metrics = {
        'model': model_name,
        'threshold': round(float(thr), 2),
        'accuracy': round(float(accuracy_score(y_test, y_pred)), 4),
        'precision': round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        'recall': round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        'f1': round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        'roc_auc': round(float(roc_auc_score(y_test, y_prob)), 4),
        'pr_auc': round(float(average_precision_score(y_test, y_prob)), 4),
        'n_features': len(feature_cols),
        'n_test': int(len(y_test)),
        'positive_rate_test': round(float(y_test.mean()), 4),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'features': feature_cols,
        'top_features': dict(sorted(zip(X.columns.tolist(), model.feature_importances_.tolist()),
                                    key=lambda x: x[1], reverse=True)[:12]),
    }
    with open(f"{MODELS_DIR}/{model_name}.pkl", 'wb') as f:
        pickle.dump({'model': model, 'encoders': encoders, 'features': feature_cols,
                     'threshold': thr}, f)

    print(f"\n=== {model_name} (thr={thr}) ===")
    print(f"ROC-AUC {metrics['roc_auc']:.4f} | PR-AUC {metrics['pr_auc']:.4f} | "
          f"Acc {metrics['accuracy']:.4f} | Prec {metrics['precision']:.4f} | "
          f"Rec {metrics['recall']:.4f} | F1 {metrics['f1']:.4f}")
    for feat, imp in list(metrics['top_features'].items())[:8]:
        print(f"  {feat}: {imp:.4f}")
    return metrics

def main():
    player_df = load_player_features()
    print(f"Player features: {len(player_df)} rows, churn={player_df['churn_d7'].mean():.1%}")
    churn_metrics = build_model(player_df, 'churn_d7', 'churn_model')

    leads_df = load_leads_features()
    print(f"Leads: {len(leads_df)} rows, conv={leads_df['converted_30d'].mean():.1%}")
    conv_metrics = build_model(leads_df, 'converted_30d', 'conversion_model', tune_threshold=True)

    with open(f"{MODELS_DIR}/metrics.json", 'w') as f:
        json.dump({'churn_model': churn_metrics, 'conversion_model': conv_metrics}, f, indent=2)
    print("\nMetrics guardados en models/metrics.json")

if __name__ == "__main__":
    main()
