import sqlite3, json, pickle, pandas as pd, numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder
import os

DB_PATH = "data/playnova_games.db"
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

LE = LabelEncoder()

def load_player_features():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM player_features", conn)
    conn.close()
    return df

def load_leads_features():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT l.lead_id, l.country, l.os, l.device, l.tutorial_completed,
               l.session_1_length, l.friends_invited, l.days_to_session_2,
               l.converted_30d, c.channel as acquisition_channel
        FROM leads l
        JOIN campaigns c ON l.campaign_id = c.campaign_id
    """, conn)
    conn.close()
    return df

def build_model(df, target_col, model_name):
    exclude = ['player_id','churn_d7','converted_30d','days_since_last_session','lead_id']
    feature_cols = [c for c in df.columns if c not in exclude and c != target_col]
    X = df[feature_cols].copy()
    y = df[target_col].copy()

    obj_cols = X.select_dtypes(include='object').columns
    for col in obj_cols:
        X[col] = LE.fit_transform(X[col].astype(str))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=300, max_depth=12, min_samples_leaf=5, class_weight='balanced_subsample', random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:,1]

    metrics = {
        'model': model_name,
        'accuracy': round(accuracy_score(y_test,y_pred),4),
        'precision': round(precision_score(y_test,y_pred),4),
        'recall': round(recall_score(y_test,y_pred),4),
        'f1': round(f1_score(y_test,y_pred),4),
        'roc_auc': round(roc_auc_score(y_test,y_prob),4),
        'n_features': len(feature_cols),
        'n_test': len(y_test),
        'confusion_matrix': confusion_matrix(y_test,y_pred).tolist(),
        'top_features': dict(zip(X.columns.tolist(), model.feature_importances_.tolist()))
    }
    metrics['top_features'] = dict(sorted(metrics['top_features'].items(), key=lambda x: x[1], reverse=True)[:15])

    with open(f"{MODELS_DIR}/{model_name}.pkl",'wb') as f: pickle.dump(model, f)

    metrics['top_features'] = dict(sorted(metrics['top_features'].items(), key=lambda x: x[1], reverse=True)[:15])
    return metrics

def main():
    print("Cargando datos...")
    player_df = load_player_features()
    print(f"Player features: {len(player_df)} rows")

    print("\n--- Entrenando Churn Score (D7) ---")
    churn_metrics = build_model(player_df, 'churn_d7', 'churn_model')

    leads_df = load_leads_features()
    print(f"\nLeads: {len(leads_df)} rows")
    print("\n--- Entrenando Conversion Score (converted_30d) ---")
    conv_metrics = build_model(leads_df, 'converted_30d', 'conversion_model')

    all_metrics = {'churn_model': churn_metrics, 'conversion_model': conv_metrics}
    with open(f"{MODELS_DIR}/metrics.json",'w') as f: json.dump(all_metrics, f, indent=2, default=str)
    print(f"\nMetrics guardados en {MODELS_DIR}/metrics.json")

if __name__ == "__main__": main()
