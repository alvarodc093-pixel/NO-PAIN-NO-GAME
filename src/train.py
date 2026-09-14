"""Entrena Churn Score + Conversion Score. Guarda modelos y métricas.
Uso: python src/train.py
"""
import sqlite3, json
from pathlib import Path
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, average_precision_score, confusion_matrix)

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "riot_gaming.db"
MODELS = ROOT / "models"
MODELS.mkdir(exist_ok=True)

# NOTA DE DISEÑO (para defender en presentación):
# days_since_last_login NO se usa como feature: sería leakage (cuando ya lleva
# 30 días fuera ya es tarde). El modelo predice con comportamiento previo
# para alertar ANTES. Se guarda en BD solo para análisis, no para predecir.
CHURN_NUM = ["account_age_days", "level",
  "matches_last_7d",
  "matches_last_30d", "avg_duration_30d", "winrate_30d", "kda_30d", "solo_rate_30d",
  "toxicity_received_30d", "total_spent_eur", "days_active_30d"]
CHURN_CAT = ["main_game", "rank_tier", "age_group", "country", "acquisition_channel"]
CONV_NUM = ["matches_first_week", "friends_invited", "days_to_second_session", "tutorial_completed"]
CONV_CAT = ["age_group", "country", "game_interest"]

def build_pipe(num, cat):
    pre = ColumnTransformer([
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
    clf = RandomForestClassifier(n_estimators=300, min_samples_leaf=5,
        class_weight="balanced_subsample", random_state=42, n_jobs=-1)
    return Pipeline([("pre", pre), ("clf", clf)])

def evaluate(y_true, y_proba, thr=0.5):
    y_pred = (y_proba >= thr).astype(int)
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_proba)), 4),
        "pr_auc": round(float(average_precision_score(y_true, y_proba)), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "threshold": thr,
    }

def main():
    con = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM player_features", con)
    leads = pd.read_sql("SELECT * FROM new_leads", con)
    camps = pd.read_sql("SELECT * FROM campaigns", con)
    con.close()
    leads["days_to_second_session"] = leads["days_to_second_session"].fillna(9.0)
    cmap = dict(zip(camps.campaign_id, camps.channel))
    leads["channel"] = leads.campaign_id.map(cmap)

    # --- CHURN ---
    X, y = df[CHURN_NUM + CHURN_CAT], df["churn_60d"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    pipe = build_pipe(CHURN_NUM, CHURN_CAT).fit(Xtr, ytr)
    proba = pipe.predict_proba(Xte)[:, 1]
    m_churn = evaluate(yte, proba)
    joblib.dump(pipe, MODELS / "churn_model.pkl")

    ohe = pipe.named_steps["pre"].named_transformers_["cat"]
    feat_names = CHURN_NUM + list(ohe.get_feature_names_out(CHURN_CAT))
    imps = pipe.named_steps["clf"].feature_importances_
    top = sorted(zip(feat_names, imps), key=lambda x: -x[1])[:12]
    m_churn["top_features"] = [(k, round(float(v), 4)) for k, v in top]
    m_churn["n_train"], m_churn["n_test"] = len(Xtr), len(Xte)
    m_churn["base_rate"] = round(float(y.mean()), 4)

    # --- CONVERSION ---
    X2, y2 = leads[CONV_NUM + CONV_CAT], leads["converted_30d"]
    Xtr2, Xte2, ytr2, yte2 = train_test_split(X2, y2, test_size=0.2, stratify=y2, random_state=42)
    pipe2 = build_pipe(CONV_NUM, CONV_CAT).fit(Xtr2, ytr2)
    proba2 = pipe2.predict_proba(Xte2)[:, 1]
    m_conv = evaluate(yte2, proba2)
    joblib.dump(pipe2, MODELS / "conversion_model.pkl")
    ohe2 = pipe2.named_steps["pre"].named_transformers_["cat"]
    fn2 = CONV_NUM + list(ohe2.get_feature_names_out(CONV_CAT))
    imps2 = pipe2.named_steps["clf"].feature_importances_
    top2 = sorted(zip(fn2, imps2), key=lambda x: -x[1])[:10]
    m_conv["top_features"] = [(k, round(float(v), 4)) for k, v in top2]
    m_conv["n_train"], m_conv["n_test"] = len(Xtr2), len(Xte2)
    m_conv["base_rate"] = round(float(y2.mean()), 4)

    # --- EDA resumida para docs ---
    eda = {}
    eda["churn_global"] = round(float(y.mean()), 4)
    eda["conv_global"] = round(float(y2.mean()), 4)
    eda["churn_by_game"] = df.groupby("main_game")["churn_60d"].mean().round(3).to_dict()
    eda["churn_by_channel"] = df.groupby("acquisition_channel")["churn_60d"].mean().round(3).to_dict()
    eda["churn_by_rank"] = df.groupby("rank_tier")["churn_60d"].mean().round(3).to_dict()
    df["toxic_bucket"] = pd.cut(df.toxicity_received_30d, [-1, 0, 1, 99], labels=["0", "1", "2+"])
    eda["churn_by_toxicity"] = df.groupby("toxic_bucket", observed=True)["churn_60d"].mean().round(3).to_dict()
    df["solo_bucket"] = pd.cut(df.solo_rate_30d, [-0.01, 0.33, 0.66, 1.01], labels=["en grupo", "mixto", "solo"])
    eda["churn_by_solo"] = df.groupby("solo_bucket", observed=True)["churn_60d"].mean().round(3).to_dict()
    df["spent_bucket"] = pd.cut(df.total_spent_eur, [-0.01, 0.01, 20, 1e9], labels=["0€", "1-20€", ">20€"])
    eda["churn_by_spend"] = df.groupby("spent_bucket", observed=True)["churn_60d"].mean().round(3).to_dict()
    eda["conv_by_channel"] = leads.groupby("channel")["converted_30d"].mean().round(3).to_dict()
    eda["conv_by_tutorial"] = leads.groupby("tutorial_completed")["converted_30d"].mean().round(3).to_dict()
    eda["conv_by_game"] = leads.groupby("game_interest")["converted_30d"].mean().round(3).to_dict()

    out = {"churn": m_churn, "conversion": m_conv, "eda": eda}
    (MODELS / "metrics.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
