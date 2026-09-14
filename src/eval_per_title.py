"""Evaluación por título de los modelos reales (evidencia para docs/08).

Uso: python src/eval_per_title.py
"""
import pickle
import numpy as np
import pandas as pd
import sqlite3
from sklearn.metrics import roc_auc_score, f1_score

NAMES = {570: "Dota 2", 440: "TF2", 230410: "Warframe", 238960: "PoE",
         1172470: "Apex", 1097150: "Fall Guys"}


def frame(g, feats, enc):
    X = pd.DataFrame()
    if "log_hours_at_review" in feats:
        X["log_hours_at_review"] = np.log1p(g["hours_at_review"])
    if "log_review_len" in feats:
        X["log_review_len"] = np.log1p(g["review_len"])
    if "log_games_owned" in feats:
        X["log_games_owned"] = np.log1p(g["num_games_owned"])
    for col in ["voted_up", "num_reviews", "early_access", "received_free",
                "refunded", "review_age_days", "appid"]:
        if col in feats:
            X[col] = g[col]
    for col, classes in enc.items():
        mp = {v: i for i, v in enumerate(classes)}
        src = "appid" if col == "appid" else col
        X[col] = g[src].astype(str).map(mp).fillna(-1).astype(int)
    return X[feats]


def main():
    conn = sqlite3.connect("data/playnova_real.db")
    df = pd.read_sql("SELECT * FROM reviews WHERE churn IS NOT NULL", conn)
    conn.close()
    for mfile, tcol in [("models/real_churn_model.pkl", "churn"),
                        ("models/real_conversion_model.pkl", "high_value")]:
        b = pickle.load(open(mfile, "rb"))
        print("==", mfile, "thr", b["threshold"])
        for appid, g in sorted(df.groupby("appid")):
            X = frame(g, b["features"], b["encoders"])
            p = b["model"].predict_proba(X)[:, 1]
            y = g[tcol].astype(int)
            try:
                auc = roc_auc_score(y, p)
            except ValueError:
                auc = float("nan")
            f1 = f1_score(y, (p >= b["threshold"]).astype(int), zero_division=0)
            print(f"  {NAMES[appid]:<9} n={len(g):>5} pos={100*y.mean():5.1f}% ROC={auc:.3f} F1={f1:.3f}")


if __name__ == "__main__":
    main()
