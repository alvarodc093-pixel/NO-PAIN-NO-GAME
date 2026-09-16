"""Entrena Churn y High-Value sobre el dataset REAL (data/playnova_real.db).

Anti-fuga: los modelos solo usan observables del momento de la reseña
(+ amplitud de cuenta). Nunca horas totales, últimas 2 semanas,
recencia ni el voto (en conversión), porque definen las etiquetas.
"""
import json, os, pickle, sqlite3
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, average_precision_score, confusion_matrix)
from sklearn.preprocessing import LabelEncoder

DB = "data/playnova_real.db"
MODELS_DIR = "models"

CHURN_FEATURES = ["hours_at_review", "voted_up", "review_len", "num_games_owned",
                  "num_reviews", "early_access", "received_free", "refunded",
                  "language", "review_age_days", "appid"]
VALUE_FEATURES = ["hours_at_review", "review_len", "num_games_owned",
                  "num_reviews", "early_access", "received_free", "refunded",
                  "language", "review_age_days", "appid"]


def load():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM reviews WHERE churn IS NOT NULL", conn)
    conn.close()
    return df


def encode(df, cols):
    X = df[cols].copy()
    X["log_hours_at_review"] = np.log1p(X["hours_at_review"])
    X["log_review_len"] = np.log1p(X["review_len"])
    X["log_games_owned"] = np.log1p(X["num_games_owned"])
    X = X.drop(columns=["hours_at_review", "review_len", "num_games_owned"])
    encoders = {}
    for col in X.select_dtypes(include=["object", "string"]).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le.classes_.tolist()
    # idioma: agrupa colas raras en "other" para estabilidad
    return X, encoders


def best_threshold(y_true, y_prob):
    best = (0.5, -1.0)
    for t in [round(x, 2) for x in np.arange(0.15, 0.86, 0.05)]:
        f1 = f1_score(y_true, (y_prob >= t).astype(int), zero_division=0)
        if f1 > best[1]:
            best = (t, f1)
    return best[0]


def build(df, target, features, name):
    y = df[target].astype(int)
    X, encoders = encode(df, features)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    # Umbral calibrado en VALIDACIÓN interna (split del train), nunca en test:
    # el test se toca una sola vez para el reporte final.
    Xfit, Xval, yfit, yval = train_test_split(
        Xtr, ytr, test_size=0.25, random_state=42, stratify=ytr)
    probe = RandomForestClassifier(n_estimators=300, max_depth=12, min_samples_leaf=5,
                                   class_weight="balanced_subsample", random_state=42, n_jobs=-1)
    probe.fit(Xfit, yfit)
    thr = best_threshold(yval, probe.predict_proba(Xval)[:, 1])
    model = RandomForestClassifier(n_estimators=300, max_depth=12, min_samples_leaf=5,
                                   class_weight="balanced_subsample", random_state=42, n_jobs=-1)
    model.fit(Xtr, ytr)
    prob = model.predict_proba(Xte)[:, 1]
    pred = (prob >= thr).astype(int)
    metrics = {
        "model": name, "threshold": round(float(thr), 2),
        "accuracy": round(float(accuracy_score(yte, pred)), 4),
        "precision": round(float(precision_score(yte, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(yte, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(yte, pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(yte, prob)), 4),
        "pr_auc": round(float(average_precision_score(yte, prob)), 4),
        "baseline_pr": round(float(yte.mean()), 4),
        "n_test": int(len(yte)),
        "confusion_matrix": confusion_matrix(yte, pred).tolist(),
        "features": list(X.columns),
        "top_features": dict(sorted(zip(X.columns.tolist(), model.feature_importances_.tolist()),
                                    key=lambda x: x[1], reverse=True)[:12]),
    }
    with open(f"{MODELS_DIR}/{name}.pkl", "wb") as f:
        pickle.dump({"model": model, "encoders": encoders,
                     "features": list(X.columns), "threshold": thr}, f)
    print(f"\n=== {name} (thr={thr}) ===")
    print(f"ROC {metrics['roc_auc']:.4f} | PR {metrics['pr_auc']:.4f} (base {metrics['baseline_pr']:.3f}) | "
          f"Acc {metrics['accuracy']:.4f} | Prec {metrics['precision']:.4f} | "
          f"Rec {metrics['recall']:.4f} | F1 {metrics['f1']:.4f}")
    for k, v in list(metrics["top_features"].items())[:8]:
        print(f"  {k}: {v:.4f}")
    return metrics


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    df = load()
    print(f"Filas etiquetadas: {len(df)} · churn={df['churn'].mean():.1%} · high_value={df['high_value'].mean():.1%}")
    out = {
        "churn_model": build(df, "churn", CHURN_FEATURES, "real_churn_model"),
        "conversion_model": build(df, "high_value", VALUE_FEATURES, "real_conversion_model"),
    }
    with open(f"{MODELS_DIR}/real_metrics.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nMétricas en models/real_metrics.json")


if __name__ == "__main__":
    main()
