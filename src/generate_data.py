import sqlite3, random, datetime, os

random.seed(42)
DB_PATH = "data/playnova_games.db"
N_PLAYERS = 8000
N_LEADS = 3000

CHANNELS = ['tiktok','meta','google_uac','unity_ads','ironsource','applovin','organic','referral']
CHANNEL_RETAIN_D7 = {'tiktok':0.29,'meta':0.22,'google_uac':0.24,'unity_ads':0.23,'ironsource':0.21,'applovin':0.20,'organic':0.32,'referral':0.28}
COUNTRIES = ['ES','FR','DE','IT','PT','NL','PL','GB']

def gen_date(base, days_back): return (base - datetime.timedelta(days=random.randint(0,days_back))).isoformat()

def generate():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.executescript(open("data/schema.sql").read())
    now = datetime.date.today()

    campaigns = []
    for name, ch, game in [("TikTok Blitz","tiktok","puzzle"),("Meta UA Campaign","meta","idle"),("Google UAC Puzzle","google_uac","puzzle"),("Unity Ads Idle","unity_ads","idle"),("ironSource Puzzle","ironsource","puzzle"),("AppLovin Idle","applovin","idle"),("Organic Growth","organic","puzzle"),("Referral Program","referral","puzzle")]:
        c.execute("INSERT INTO campaigns(name,channel,game_target,cost_eur,start_date,end_date) VALUES(?,?,?,?,?,?)",(name,ch,game,random.randint(500,5000),(now-datetime.timedelta(days=90)).isoformat(),now.isoformat()))
        campaigns.append((ch, game, c.lastrowid))

    campaign_ids = [c[2] for c in campaigns]
    players = []; events = []; purchases = []
    for _ in range(N_PLAYERS):
        ch = random.choice(CHANNELS); country = random.choice(COUNTRIES)
        tutorial = random.choices([0,1], weights=[0.6,0.4])[0]
        friends = random.randint(0,5); level = random.randint(1,50); account_age = random.randint(1,365)
        c.execute("INSERT INTO players(device_id,region,country,os,app_version,level,account_age_days,acquisition_channel,acquisition_campaign_id,install_date,last_session_date) VALUES(?,?,?,?,?,?,?,?,?,?,?)",(f"p{random.randint(10000,99999)}","EU" if country in['ES','FR','DE','IT','PT','NL','PL'] else "EU-W",country,random.choice(['iOS','Android']),f"{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}",level,account_age,ch,random.choice(campaign_ids),gen_date(now,365),now.isoformat()))
        pid = c.lastrowid; retain = CHANNEL_RETAIN_D7[ch]; churn_7d = 1 if random.random()>retain else 0
        n_sessions = random.randint(1,20) if not churn_7d else random.randint(1,3)
        coins = round(random.uniform(0,50),2); ads = random.randint(0,10); boosters = random.randint(0,5)
        for _ in range(n_sessions):
            events.append((pid, gen_date(now,30), round(random.uniform(5,25),1), random.randint(0,tutorial*3), round(coins/random.randint(1,5),2), random.randint(0,boosters), random.randint(0,ads//2), random.randint(0,friends)))
        if random.random() < 0.15:
            purchases.append((pid, gen_date(now,30), random.choice(['gems','lives','booster','season_pass']), round(random.uniform(0.99,29.99),2)))
        c.execute("INSERT INTO player_features(player_id,session_count_7d,tutorial_completed,social_invites_7d,coins_spent_7d,ads_watched_7d,boosters_used_7d,level,country_region,device_type,churn_d7,days_since_last_session) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(pid,n_sessions,tutorial,friends,coins,ads,boosters,level,country,random.choice(['iOS','Android']),churn_7d,random.randint(0,30)))
        players.append(pid)

    for _ in range(N_LEADS):
        camp = random.choice(campaigns); ch = camp[0]; tut = random.choices([0,1],weights=[0.6,0.4])[0]; friends=random.randint(0,5); d2s=random.randint(1,14)
        conv = 1 if (tut and friends>=1 and d2s<=3 and random.random()<0.15) else 0
        c.execute("INSERT INTO leads(campaign_id,install_date,country,os,device,tutorial_completed,session_1_length,friends_invited,days_to_session_2,converted_30d) VALUES(?,?,?,?,?,?,?,?,?,?)",(camp[2],gen_date(now,60),random.choice(COUNTRIES),random.choice(['iOS','Android']),f"ldev{random.randint(1000,9999)}",tut,round(random.uniform(2,15),1),friends,d2s,conv))

    for e in events: c.execute("INSERT INTO events(player_id,event_date,session_length,tutorial_step,coins_spent,boosters_used,ads_watched,social_invites) VALUES(?,?,?,?,?,?,?,?)",e)
    for p in purchases: c.execute("INSERT INTO purchases(player_id,purchase_date,item_type,amount_eur) VALUES(?,?,?,?)",p)
    conn.commit(); conn.close()
    print(f"Generado: {N_PLAYERS} jugadores, {N_LEADS} leads, {len(events)} eventos, {len(purchases)} compras")

if __name__ == "__main__": generate()
