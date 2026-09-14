CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL,
    channel        TEXT    NOT NULL,
    game_target    TEXT    NOT NULL,
    cost_eur       REAL    NOT NULL DEFAULT 0,
    start_date     TEXT    NOT NULL,
    end_date       TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    player_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id              TEXT    NOT NULL,
    region                 TEXT    NOT NULL,
    country                TEXT    NOT NULL,
    os                     TEXT    NOT NULL,
    app_version            TEXT    NOT NULL DEFAULT '1.0.0',
    level                  INTEGER NOT NULL DEFAULT 1,
    account_age_days       INTEGER NOT NULL DEFAULT 0,
    acquisition_channel    TEXT    NOT NULL DEFAULT 'organic',
    acquisition_campaign_id INTEGER,
    install_date           TEXT    NOT NULL,
    last_session_date      TEXT    NOT NULL,
    FOREIGN KEY (acquisition_campaign_id) REFERENCES campaigns(campaign_id)
);

CREATE TABLE IF NOT EXISTS events (
    event_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id      INTEGER NOT NULL,
    event_date     TEXT    NOT NULL,
    session_length REAL    NOT NULL DEFAULT 0,
    tutorial_step  INTEGER NOT NULL DEFAULT 0,
    coins_spent    REAL    NOT NULL DEFAULT 0,
    boosters_used  INTEGER NOT NULL DEFAULT 0,
    ads_watched    INTEGER NOT NULL DEFAULT 0,
    social_invites INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE TABLE IF NOT EXISTS purchases (
    purchase_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id    INTEGER NOT NULL,
    purchase_date TEXT   NOT NULL,
    item_type    TEXT    NOT NULL,
    amount_eur   REAL    NOT NULL DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE TABLE IF NOT EXISTS leads (
    lead_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id          INTEGER NOT NULL,
    install_date         TEXT    NOT NULL,
    country              TEXT    NOT NULL,
    os                   TEXT    NOT NULL,
    device               TEXT    NOT NULL,
    tutorial_completed   INTEGER NOT NULL DEFAULT 0,
    session_1_length     REAL    NOT NULL DEFAULT 0,
    friends_invited      INTEGER NOT NULL DEFAULT 0,
    days_to_session_2    INTEGER NOT NULL DEFAULT 999,
    converted_30d        INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

CREATE TABLE IF NOT EXISTS player_features (
    player_id            INTEGER PRIMARY KEY,
    session_count_7d     INTEGER NOT NULL DEFAULT 0,
    tutorial_completed   INTEGER NOT NULL DEFAULT 0,
    social_invites_7d    INTEGER NOT NULL DEFAULT 0,
    coins_spent_7d       REAL    NOT NULL DEFAULT 0,
    ads_watched_7d       INTEGER NOT NULL DEFAULT 0,
    boosters_used_7d     INTEGER NOT NULL DEFAULT 0,
    level                INTEGER NOT NULL DEFAULT 1,
    country_region       TEXT    NOT NULL DEFAULT 'unknown',
    device_type          TEXT    NOT NULL DEFAULT 'unknown',
    acquisition_channel  TEXT    NOT NULL DEFAULT 'organic',
    churn_d7             INTEGER NOT NULL DEFAULT 0,
    days_since_last_session INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE INDEX IF NOT EXISTS idx_events_player   ON events(player_id);
CREATE INDEX IF NOT EXISTS idx_purchases_player ON purchases(player_id);
CREATE INDEX IF NOT EXISTS idx_features_player  ON player_features(player_id);
CREATE INDEX IF NOT EXISTS idx_leads_campaign   ON leads(campaign_id);
CREATE INDEX IF NOT EXISTS idx_players_acq      ON players(acquisition_channel);
