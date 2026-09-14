"""Construye el dataset REAL desde reseñas de Steam (data/real/steam_reviews.jsonl).

Diseño metodológico (sin fuga):
- Features = observables en el momento de la reseña + amplitud de cuenta.
- Label churn = estado de actividad en la fecha de scraping (sep-2026):
    churned (1): playtime_forever >= 120 min, 0 min últimas 2 semanas y
                 última partida hace > 30 días.
    activo (0):  > 0 min en las últimas 2 semanas.
    resto: ambiguo (NULL, se excluye del modelo; se cuenta en el resumen).
- Label high_value (proxy de jugador monetizable, los F2P no exponen pago):
    playtime_forever >= p75 del título Y voted_up = 1.
    El modelo lo predice SOLO con señales tempranas (horas en reseña,
    longitud, cuenta, early access…), nunca con sus componentes.

Salida:
    data/playnova_real.db (tablas titles, reviews)
    data/real_summary.json (conteos, tasas por título, fechas)
"""
import json, os, sqlite3, time
from datetime import datetime, timezone

import pandas as pd

RAW = "data/real/steam_reviews.jsonl"
DB = "data/playnova_real.db"
SUMMARY = "data/real_summary.json"

NOW = time.time()  # fecha de scraping ≈ fecha de observación
DAY = 86400


def load():
    rows = []
    with open(RAW, encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows


def build(rows):
    recs, titles = [], {}
    for r in rows:
        a = r.get("author", {}) or {}
        forever = (a.get("playtime_forever") or 0) / 60.0
        at_rev = (a.get("playtime_at_review") or 0) / 60.0
        l2w = (a.get("playtime_last_two_weeks") or 0) / 60.0
        last_played = a.get("last_played") or 0
        dslp = (NOW - last_played) / DAY if last_played else None
        created = r.get("timestamp_created") or 0
        text = r.get("review") or ""
        titles[r["_appid"]] = r["_appname"]
        recs.append({
            "review_id": str(r.get("recommendationid")),
            "appid": r["_appid"],
            "voted_up": 1 if r.get("voted_up") else 0,
            "hours_forever": round(forever, 2),
            "hours_at_review": round(at_rev, 2),
            "hours_l2w": round(l2w, 2),
            "days_since_last_played": round(dslp, 1) if dslp is not None else None,
            "review_age_days": round((NOW - created) / DAY, 1) if created else None,
            "review_len": len(text),
            "num_games_owned": a.get("num_games_owned") or 0,
            "num_reviews": a.get("num_reviews") or 0,
            "early_access": 1 if r.get("written_during_early_access") else 0,
            "received_free": 1 if r.get("received_for_free") else 0,
            "refunded": 1 if r.get("refunded") else 0,
            "language": r.get("language") or "unknown",
            "timestamp_created": created,
        })
    df = pd.DataFrame(recs).drop_duplicates("review_id")

    # p75 de horas por título (para high_value)
    p75 = df.groupby("appid")["hours_forever"].quantile(0.75).to_dict()

    def churn(row):
        if row["hours_l2w"] > 0:
            return 0
        if (row["hours_forever"] >= 2.0 and row["days_since_last_played"] is not None
                and row["days_since_last_played"] > 30):
            return 1
        return None

    df["churn"] = df.apply(churn, axis=1)
    df["p75_title"] = df["appid"].map(p75)
    df["high_value"] = ((df["hours_forever"] >= df["p75_title"]) & (df["voted_up"] == 1)).astype(int)
    return df, titles, p75


def save(df, titles, p75):
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    df.to_sql("reviews", conn, index=False)
    pd.DataFrame([{"appid": k, "name": v, "p75_hours": round(p75[k], 1)}
                  for k, v in titles.items()]).to_sql("titles", conn, index=False)
    conn.execute("CREATE INDEX idx_rev_app ON reviews(appid)")
    conn.execute("CREATE INDEX idx_rev_churn ON reviews(churn)")
    conn.close()

    lab = df[df["churn"].notna()]
    summary = {
        "scrape_date": datetime.fromtimestamp(NOW, tz=timezone.utc).strftime("%Y-%m-%d"),
        "source": "Steam Store appreviews API (pública, sin key)",
        "n_raw": int(len(df)),
        "n_labeled_churn": int(len(lab)),
        "n_ambiguous_dropped": int(df["churn"].isna().sum()),
        "churn_rate": round(float(lab["churn"].mean()), 4),
        "high_value_rate": round(float(lab["high_value"].mean()), 4),
        "voted_up_rate": round(float(df["voted_up"].mean()), 4),
        "median_hours_forever": round(float(df["hours_forever"].median()), 1),
        "by_title": {
            titles[appid]: {
                "n": int((df["appid"] == appid).sum()),
                "churn_rate": round(float(lab[lab["appid"] == appid]["churn"].mean()), 4),
                "high_value_rate": round(float(lab[lab["appid"] == appid]["high_value"].mean()), 4),
                "p75_hours": round(float(p75[appid]), 1),
            } for appid in titles
        },
    }
    with open(SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    rows = load()
    print(f"Reseñas crudas: {len(rows)}")
    df, titles, p75 = build(rows)
    save(df, titles, p75)
    print(f"\nDB: {DB} ({len(df)} filas) · resumen: {SUMMARY}")
