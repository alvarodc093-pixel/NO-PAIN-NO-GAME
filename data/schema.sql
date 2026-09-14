-- No Pain, No Game · Schema Riot Games (EUW muestra)
-- SQLite compatible
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS player_features;
DROP TABLE IF EXISTS new_leads;
DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS campaigns;

CREATE TABLE campaigns (
    campaign_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    channel TEXT NOT NULL,          -- Twitch, YouTube, TikTok, Discord, Evento
    game_target TEXT NOT NULL,      -- LoL, Valorant, TFT
    cost_eur REAL NOT NULL,
    start_date TEXT NOT NULL,       -- ISO YYYY-MM-DD
    end_date TEXT NOT NULL
);

CREATE TABLE players (
    player_id INTEGER PRIMARY KEY,
    riot_id TEXT UNIQUE NOT NULL,   -- ej. EUW-92831
    region TEXT NOT NULL DEFAULT 'EUW',
    country TEXT NOT NULL,
    age_group TEXT NOT NULL,        -- 13-17, 18-24, 25-34, 35+
    main_game TEXT NOT NULL,        -- LoL, Valorant, TFT
    rank_tier TEXT NOT NULL,        -- Iron..Challenger, Unranked
    level INTEGER NOT NULL,
    account_age_days INTEGER NOT NULL,
    acquisition_channel TEXT NOT NULL,
    acquisition_campaign_id INTEGER REFERENCES campaigns(campaign_id),
    acquisition_date TEXT NOT NULL,
    last_login_date TEXT NOT NULL
);

CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    match_date TEXT NOT NULL,
    game TEXT NOT NULL,
    duration_min REAL NOT NULL,
    win INTEGER NOT NULL,           -- 0/1
    kills INTEGER NOT NULL,
    deaths INTEGER NOT NULL,
    assists INTEGER NOT NULL,
    chat_messages INTEGER NOT NULL,
    premade_size INTEGER NOT NULL,  -- 1=solo, 2-5=con amigos
    toxicity_reports_received INTEGER NOT NULL DEFAULT 0,
    toxicity_reports_made INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_matches_player_date ON matches(player_id, match_date);

CREATE TABLE purchases (
    purchase_id INTEGER PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(player_id),
    purchase_date TEXT NOT NULL,
    item_type TEXT NOT NULL,        -- skin, battlepass, champions, points
    amount_eur REAL NOT NULL
);
CREATE INDEX idx_purchases_player ON purchases(player_id);

CREATE TABLE new_leads (
    lead_id INTEGER PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(campaign_id),
    signup_date TEXT NOT NULL,
    age_group TEXT NOT NULL,
    region TEXT NOT NULL DEFAULT 'EUW',
    country TEXT NOT NULL,
    game_interest TEXT NOT NULL,
    tutorial_completed INTEGER NOT NULL, -- 0/1
    matches_first_week INTEGER NOT NULL,
    friends_invited INTEGER NOT NULL,
    days_to_second_session REAL,         -- NULL si solo 1 sesión
    converted_30d INTEGER NOT NULL       -- 0/1 label conversión
);

-- Tabla agregada para modelar churn (se genera vía generate_data.py)
-- days_since_last_login se guarda para análisis pero NO se usa como feature (anti-leakage).
CREATE TABLE player_features (
    player_id INTEGER PRIMARY KEY REFERENCES players(player_id),
    main_game TEXT NOT NULL,
    rank_tier TEXT NOT NULL,
    age_group TEXT NOT NULL,
    country TEXT NOT NULL,
    acquisition_channel TEXT NOT NULL,
    account_age_days INTEGER NOT NULL,
    level INTEGER NOT NULL,
    days_since_last_login INTEGER NOT NULL,
    matches_last_7d INTEGER NOT NULL,
    matches_last_30d INTEGER NOT NULL,
    avg_duration_30d REAL NOT NULL,
    winrate_30d REAL NOT NULL,
    kda_30d REAL NOT NULL,
    solo_rate_30d REAL NOT NULL,
    toxicity_received_30d INTEGER NOT NULL,
    total_spent_eur REAL NOT NULL,
    days_active_30d INTEGER NOT NULL,
    churn_60d INTEGER NOT NULL       -- 1 = abandona próximos 60d (label)
);
