"""No Pain, No Game — Generador de datos sintéticos Riot EUW.
Crea data/riot_gaming.db coherente: 8000 players + 3000 leads.
Cutoff (hoy simulado): 2026-09-01. Ventana features: últimos 30d.
Seed fija para reproducibilidad.
Uso: python src/generate_data.py

Calibración externa (ver docs/07_fuentes_externas.md):
- Churn base ~16% 60d: Kim et al. 2026 (295k LoL, +8% a 60d).
- Toxicidad 18% expuestos: Kwak CHI'15 (10M reports) + Riot Lin (-40% abuso).
- Duración 32min LoL: LEC 2025 (gol.gg 32:19).
- Revenue cosmética: LoL $1.65-1.8B/año (trackers 2025-26).
- Retención temprana x8 con 3 partidas: proyecto EUW API (princethoth).
La API real (src/fetch_riot.py) NO da tienda/toxicidad/churn: por eso se calibra aquí.
"""
import sqlite3, random
from pathlib import Path
from datetime import date, timedelta
import numpy as np

SEED = 42
N_PLAYERS = 8000
N_LEADS = 3000
CUTOFF = date(2026, 9, 1)
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "riot_gaming.db"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "data" / "schema.sql"

rng = np.random.default_rng(SEED)
random.seed(SEED)

GAMES = ["LoL", "Valorant", "TFT"]
GAME_P = [0.5, 0.35, 0.15]
RANKS = ["Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Challenger"]
RANK_P = [0.18, 0.10, 0.18, 0.20, 0.16, 0.10, 0.06, 0.015, 0.005]
COUNTRIES = ["España", "Francia", "Alemania", "UK", "Italia", "Polonia"]
COUNTRY_P = [0.28, 0.18, 0.18, 0.14, 0.12, 0.10]
AGES = ["13-17", "18-24", "25-34", "35+"]
AGE_P = [0.22, 0.45, 0.25, 0.08]
CHANNELS = ["Twitch", "YouTube", "TikTok", "Discord", "Evento", "Orgánico"]
CHANNEL_P = [0.25, 0.22, 0.18, 0.10, 0.05, 0.20]

CAMPAIGNS = [
    (1, "Mundial LoL Watch Party", "Twitch", "LoL", 18000, "2026-06-01", "2026-06-30"),
    (2, "Valorant Clips Rush", "TikTok", "Valorant", 12000, "2026-05-01", "2026-05-31"),
    (3, "Guías TFT Express", "YouTube", "TFT", 8000, "2026-04-01", "2026-04-30"),
    (4, "Discord Community Cup", "Discord", "LoL", 5000, "2026-07-01", "2026-07-31"),
    (5, "Gamepolis Live Arena", "Evento", "Valorant", 15000, "2026-07-15", "2026-07-20"),
    (6, "Back to School Pass", "YouTube", "LoL", 9000, "2026-08-01", "2026-08-31"),
    (7, "Streamer collab: Ibai Cup", "Twitch", "Valorant", 20000, "2026-08-01", "2026-08-20"),
    (8, "TikTok #PentakillChallenge", "TikTok", "LoL", 7000, "2026-03-01", "2026-03-31"),
]

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    cur = con.cursor()
    cur.executemany("INSERT INTO campaigns VALUES (?,?,?,?,?,?,?)", CAMPAIGNS)

    # --- Players base ---
    players, features = [], []
    matches, purchases = [], []
    match_id, purchase_id = 1, 1

    for pid in range(1, N_PLAYERS + 1):
        game = rng.choice(GAMES, p=GAME_P)
        rank = rng.choice(RANKS, p=RANK_P)
        country = rng.choice(COUNTRIES, p=COUNTRY_P)
        age = rng.choice(AGES, p=AGE_P)
        channel = rng.choice(CHANNELS, p=CHANNEL_P)
        camp = int(rng.integers(1, 9)) if channel != "Orgánico" and rng.random() < 0.7 else None
        account_age = int(rng.integers(30, 1800))
        level = int(np.clip(rng.normal(180 if account_age > 365 else 60, 60), 5, 600))
        # fecha adquisición coherente con antigüedad
        acq_date = (CUTOFF - timedelta(days=int(account_age + rng.integers(-10, 10)))).isoformat()
        if acq_date < "2021-01-01":
            acq_date = "2021-06-15"

        # Perfil latente de engagement (0=desenganchado, 1=hardcore)
        solo_prop = float(rng.beta(2, 3))  # media ~0.4 solo (Kim 2026 SPL: social reduce churn)
        base_skill = float(rng.normal(0, 1))
        spender = rng.random() < 0.35  # 35% pagadores en muestra ACTIVA (global ~$13.5/MAU; muestra activa ARPU 35€, ver docs/07)
        toxicity_exposure = rng.random() < 0.18  # 18% sufre toxicidad alta (Kwak CHI'15 + Lin; infra-reporte)

        # Probabilidad de churn latente (drivers reales: Kim 2026 GEL/GPL/SPL; base ~16.5% 60d)
        winrate_latent = float(np.clip(0.5 + base_skill * 0.08 - (0.06 if toxicity_exposure else 0), 0.15, 0.85))
        activity_latent = float(rng.gamma(2.0, 2.0))  # partidas/mes aprox
        logit = (-1.6
                 + 1.4 * solo_prop
                 + (1.2 if toxicity_exposure else 0)
                 - 2.2 * (winrate_latent - 0.5)
                 - 0.18 * activity_latent
                 - (0.9 if spender else 0)
                 + (0.5 if rank in ("Unranked", "Iron") and account_age < 90 else 0))
        churn_prob = float(sigmoid(logit))
        churn = int(rng.random() < churn_prob)

        # last_login coherente con churn pero CON SOLAPE (evita leakage perfecto)
        # Churned: 70% 32-60 días + 30% 18-30 (aún entran pero desenganchados)
        # Activos: 0-30 días (8% con racha rara de 18-30, ruido realista)
        if churn:
            days_since = int(rng.choice(
                [rng.integers(18, 31), rng.integers(32, 61)],
                p=[0.30, 0.70]))
        else:
            days_since = int(min(30, abs(rng.normal(4, 6))))
            if rng.random() < 0.08:
                days_since = int(rng.integers(18, 31))
        last_login = (CUTOFF - timedelta(days=days_since)).isoformat()

        riot_id = f"EUW-{90000 + pid}"
        players.append((pid, riot_id, "EUW", country, age, game, rank, level,
                        account_age, channel, camp, acq_date, last_login))

        # Features ventana 30d con solape realista:
        # 70% churned de libro (0-6 partidas) + 30% "freno brusco" (7-14 partidas
        # pero con mala experiencia: racha de derrotas + toxicidad).
        if churn:
            if rng.random() < 0.70:
                m30 = int(rng.choice([0, 1, 2, 3, 4, 5, 6], p=[0.25, 0.2, 0.18, 0.14, 0.1, 0.06, 0.07]))
                wr = float(np.clip(rng.normal(0.38, 0.12), 0.05, 0.9))
            else:
                m30 = int(rng.integers(7, 15))
                wr = float(np.clip(rng.normal(0.30, 0.10), 0.05, 0.7))  # racha perdedora
                toxicity_exposure = True
            m7 = int(min(m30, rng.integers(0, 2)))
            days_active = int(min(m30, rng.integers(0, max(2, m30 + 1))))
        else:
            m30 = int(np.clip(rng.normal(14, 9), 1, 60))
            m7 = int(np.clip(rng.normal(m30 / 4, 2), 0, m30))
            days_active = int(np.clip(rng.normal(min(20, m30 * 0.7), 5), 1, 30))
            wr = float(np.clip(rng.normal(0.52, 0.1), 0.1, 0.95))
        avg_dur = float(np.clip(rng.normal(32 if game == "LoL" else 28, 6), 10, 60))  # LEC 2025 media 32:19 (gol.gg)
        kda = float(np.clip(rng.normal(2.6 if not churn else 1.9, 0.8), 0.3, 8))
        tox = int(rng.poisson(1.2) if toxicity_exposure else rng.poisson(0.15))  # Kwak: media 1.81 en reportadas, mediana 1
        spent = round(float(rng.gamma(2, 12) if spender else (rng.random() < 0.08) * rng.gamma(1, 8)), 2)  # cosmética/pases, ARPU muestra 35€ (ver docs/07)

        features.append((pid, game, rank, age, country, channel, account_age, level,
                         days_since, m7, m30, avg_dur, wr, kda, solo_prop,
                         tox, spent, days_active, churn))

        # Partidas detalle (ventana 90d; churned con fechas más antiguas)
        n_matches_total = int(np.clip(m30 * 2.2 + rng.integers(0, 8), 0, 90))
        for _ in range(n_matches_total):
            if churn:
                d_ago = int(rng.integers(25, 90))
            else:
                d_ago = int(abs(rng.normal(12, 12)) % 90)
            mdate = (CUTOFF - timedelta(days=d_ago)).isoformat()
            win = int(rng.random() < wr)
            matches.append((match_id, pid, mdate, game,
                            round(float(np.clip(rng.normal(avg_dur, 6), 8, 65)), 1),
                            win,
                            int(rng.integers(0, 18)), int(rng.integers(0, 15)), int(rng.integers(0, 20)),
                            int(rng.integers(0, 25)),
                            1 if rng.random() < solo_prop else int(rng.integers(2, 6)),
                            int(rng.poisson(0.3) if tox > 0 else 0),
                            int(rng.integers(0, 2))))
            match_id += 1

        # Compras
        n_purch = 0
        if spender:
            n_purch = int(rng.integers(1, 7))
        elif rng.random() < 0.08:
            n_purch = 1
        for _ in range(n_purch):
            pdate = (CUTOFF - timedelta(days=int(rng.integers(0, 180)))).isoformat()
            item = rng.choice(["skin", "battlepass", "champions", "points"], p=[0.5, 0.2, 0.15, 0.15])
            price = {"skin": 12.5, "battlepass": 10.0, "champions": 7.0, "points": 20.0}[item] + round(float(rng.normal(0, 2)), 2)  # precios tienda real LoL
            purchases.append((purchase_id, pid, pdate, item, round(max(2.0, price), 2)))
            purchase_id += 1

    cur.executemany("INSERT INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", players)
    cur.executemany("""INSERT INTO player_features VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", features)
    cur.executemany("INSERT INTO matches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", matches)
    cur.executemany("INSERT INTO purchases VALUES (?,?,?,?,?)", purchases)

    # --- New leads (conversión) ---
    leads = []
    for lid in range(1, N_LEADS + 1):
        camp_id = int(rng.integers(1, 9))
        ch = CAMPAIGNS[camp_id - 1][2]
        game = CAMPAIGNS[camp_id - 1][3]
        age = rng.choice(AGES, p=AGE_P)
        country = rng.choice(COUNTRIES, p=COUNTRY_P)
        signup = (CUTOFF - timedelta(days=int(rng.integers(35, 120)))).isoformat()
        tut = int(rng.random() < (0.65 if ch in ("Discord", "Evento", "Twitch") else 0.45))  # FTUE: valor en 5-15 min o churn (GameAnalytics 2026)
        m1w = int(np.clip(rng.normal(6 if tut else 2.5, 3), 0, 25))  # umbral 3 partidas → 8.6x retención (proyecto EUW API)
        friends = int(rng.poisson(1.4) if ch in ("Discord", "Evento") else rng.poisson(0.6))
        d2nd = round(float(abs(rng.normal(1.5 if tut else 4, 2))), 1)
        if m1w <= 1:
            d2nd = None
        logit_c = (-1.2 + 1.1 * tut + 0.22 * m1w + 0.45 * min(friends, 3)
                   - (0.35 * d2nd if d2nd else 0.8)
                   + (0.5 if ch in ("Discord", "Evento") else 0)
                   - (0.6 if ch == "TikTok" else 0))
        conv = int(rng.random() < sigmoid(logit_c))
        leads.append((lid, camp_id, signup, age, "EUW", country, game, tut, m1w, friends, d2nd, conv))
    cur.executemany("INSERT INTO new_leads VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", leads)
    con.commit()

    n_m = cur.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    n_p = cur.execute("SELECT COUNT(*) FROM purchases").fetchone()[0]
    ch_rate = cur.execute("SELECT AVG(churn_60d) FROM player_features").fetchone()[0]
    cv_rate = cur.execute("SELECT AVG(converted_30d) FROM new_leads").fetchone()[0]
    con.close()
    print(f"OK db={DB_PATH} players={N_PLAYERS} matches={n_m} purchases={n_p} churn={ch_rate:.3f} conv={cv_rate:.3f}")

if __name__ == "__main__":
    main()
