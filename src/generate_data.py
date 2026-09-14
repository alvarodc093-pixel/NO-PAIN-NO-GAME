"""RETIRADO — generador SINTÉTICO (ya no se usa).

El proyecto usa datos 100% reales desde 2026-09-14:
ver src/fetch_steam_reviews.py, src/build_real_dataset.py y docs/08_datos_reales.md.
Se conserva el archivo solo como historial.
"""
import sqlite3, random, datetime, os, math

random.seed(42)
DB_PATH = "data/playnova_games.db"
N_PLAYERS = 8000
N_LEADS = 3000

CHANNELS = ['tiktok','meta','google_uac','unity_ads','ironsource','applovin','organic','referral']
# Retención D7 objetivo por canal (calibrada GameAnalytics 2026 + casos TikTok/Discord).
CHANNEL_RETAIN_D7 = {'tiktok':0.29,'meta':0.22,'google_uac':0.24,'unity_ads':0.23,'ironsource':0.21,'applovin':0.20,'organic':0.32,'referral':0.28}
COUNTRIES = ['ES','FR','DE','IT','PT','NL','PL','GB']

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

def gen_date(base, days_back):
    return (base - datetime.timedelta(days=random.randint(0, days_back))).isoformat()

def generate():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript(open("data/schema.sql", encoding="utf-8").read())
    now = datetime.date.today()

    campaigns = []
    for name, ch, game in [("TikTok Blitz","tiktok","puzzle"),("Meta UA Campaign","meta","idle"),("Google UAC Puzzle","google_uac","puzzle"),("Unity Ads Idle","unity_ads","idle"),("ironSource Puzzle","ironsource","puzzle"),("AppLovin Idle","applovin","idle"),("Organic Growth","organic","puzzle"),("Referral Program","referral","puzzle")]:
        c.execute("INSERT INTO campaigns(name,channel,game_target,cost_eur,start_date,end_date) VALUES(?,?,?,?,?,?)",
                  (name, ch, game, random.randint(500, 5000),
                   (now - datetime.timedelta(days=90)).isoformat(), now.isoformat()))
        campaigns.append((ch, game, c.lastrowid))

    campaign_ids = [x[2] for x in campaigns]
    events = []
    purchases = []
    churn_count = 0
    for _ in range(N_PLAYERS):
        ch = random.choice(CHANNELS)
        country = random.choice(COUNTRIES)
        os_name = random.choice(['iOS', 'Android'])
        device_type = os_name
        # Tutorial: base 40%, mejor en orgánico/referral (onboarding con intención).
        tut_p = 0.36 + (0.10 if ch in ('organic', 'referral') else 0.0)
        tutorial = 1 if random.random() < tut_p else 0
        # Amigos: correlacionado con tutorial.
        if tutorial:
            friends = random.choices([0,1,2,3,4,5], weights=[0.35,0.22,0.15,0.12,0.09,0.07])[0]
        else:
            friends = random.choices([0,1,2,3,4,5], weights=[0.65,0.15,0.08,0.06,0.04,0.02])[0]
        level = random.randint(1, 50)
        account_age = random.randint(1, 365)
        c.execute("INSERT INTO players(device_id,region,country,os,app_version,level,account_age_days,acquisition_channel,acquisition_campaign_id,install_date,last_session_date) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                  (f"p{random.randint(10000,99999)}",
                   "EU" if country in ['ES','FR','DE','IT','PT','NL','PL'] else "EU-W",
                   country, os_name,
                   f"{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}",
                   level, account_age, ch, random.choice(campaign_ids),
                   gen_date(now, 365), now.isoformat()))
        pid = c.lastrowid

        # --- Churn por logit (comportamiento primero, etiqueta después) ---
        # Así session_count NO determina la etiqueta: hay solape real.
        chan_bonus = (CHANNEL_RETAIN_D7[ch] - 0.25) * 4.0  # organic +0.28, applovin -0.20
        logit = (1.9
                 - 1.1 * tutorial
                 - 0.25 * friends
                 - 0.015 * level
                 - chan_bonus
                 + random.gauss(0, 0.6))
        churn_prob = sigmoid(logit)
        churn_7d = 1 if random.random() < churn_prob else 0
        churn_count += churn_7d

        # Sesiones: consecuencia ruidosa del engagement, con solape entre clases.
        base = 8.0 + tutorial * 2.0 + friends * 0.6 + chan_bonus - (3.5 if churn_7d else 0.0)
        n_sessions = max(1, min(20, int(random.gauss(base, 3.0))))
        coins = round(max(0.0, random.gauss(18 if not churn_7d else 6, 12)), 2)
        ads = max(0, min(10, int(random.gauss(4 if not churn_7d else 2, 2.5))))
        boosters = max(0, min(5, int(random.gauss(2 if not churn_7d else 1, 1.5))))
        for _ in range(n_sessions):
            events.append((pid, gen_date(now, 30), round(max(1.0, random.gauss(16 if not churn_7d else 9, 6)), 1),
                           random.randint(0, tutorial * 3),
                           round(coins / random.randint(1, 5), 2),
                           random.randint(0, boosters), random.randint(0, max(0, ads // 2)),
                           random.randint(0, friends)))
        if random.random() < (0.22 if not churn_7d else 0.05):
            purchases.append((pid, gen_date(now, 30),
                              random.choice(['gems','lives','booster','season_pass']),
                              round(random.uniform(0.99, 29.99), 2)))
        # days_since_last_session coherente con la etiqueta (análisis sí, modelo no).
        dsls = random.randint(8, 30) if churn_7d else random.randint(0, 6)
        c.execute("INSERT INTO player_features(player_id,session_count_7d,tutorial_completed,social_invites_7d,coins_spent_7d,ads_watched_7d,boosters_used_7d,level,country_region,device_type,acquisition_channel,churn_d7,days_since_last_session) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (pid, n_sessions, tutorial, friends, coins, ads, boosters, level,
                   country, device_type, ch, churn_7d, dsls))

    conv_count = 0
    for _ in range(N_LEADS):
        camp = random.choice(campaigns)
        tut = 1 if random.random() < 0.42 else 0
        friends = random.choices([0,1,2,3,4,5], weights=[0.55,0.18,0.10,0.08,0.05,0.04])[0]
        d2s = random.randint(1, 14)
        s1 = round(random.uniform(2, 15), 1)
        # Conversión ~9-11%: onboarding fuerte + retorno rápido + social.
        if tut and d2s <= 4 and (friends >= 1 or s1 >= 6):
            conv = 1 if random.random() < 0.35 else 0
        else:
            conv = 1 if random.random() < 0.02 else 0
        conv_count += conv
        c.execute("INSERT INTO leads(campaign_id,install_date,country,os,device,tutorial_completed,session_1_length,friends_invited,days_to_session_2,converted_30d) VALUES(?,?,?,?,?,?,?,?,?,?)",
                  (camp[2], gen_date(now, 60), random.choice(COUNTRIES),
                   random.choice(['iOS','Android']), random.choice(['iOS','Android']),
                   tut, s1, friends, d2s, conv))

    for e in events:
        c.execute("INSERT INTO events(player_id,event_date,session_length,tutorial_step,coins_spent,boosters_used,ads_watched,social_invites) VALUES(?,?,?,?,?,?,?,?)", e)
    for p in purchases:
        c.execute("INSERT INTO purchases(player_id,purchase_date,item_type,amount_eur) VALUES(?,?,?,?)", p)
    conn.commit()
    conn.close()
    print(f"Generado: {N_PLAYERS} jugadores (churn {churn_count/N_PLAYERS:.1%}), {N_LEADS} leads (conv {conv_count/N_LEADS:.1%}), {len(events)} eventos, {len(purchases)} compras")

if __name__ == "__main__":
    generate()
