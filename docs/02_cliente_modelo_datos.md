# Día 11 — Cliente y modelo de datos (11 sept)

## 1. Ficha del cliente (ficticio pero realista)

| Campo | Detalle |
|---|---|
| **Nombre** | PlayNova Games (ficticio, mid-tier F2P publisher) |
| **Sector** | Juegos móviles free-to-play (puzzle, idle, match-3) |
| **Actividad** | 3 títulos activos (puzzle casual, idle RPG, match-3). Operación UA (user acquisition), Live-Ops, monetización in-app, push notifications. |
| **Tamaño** | ~150 empleados global (Dublín, Lisboa, Varsovia). ~2M MAU · 450k DAU · ARPDAU ~$0.12. Facturación ~$25M/año. |
| **Productos** | Puzzle Stars (match-3), Idle Legends (idle RPG), Coin Masters (puzzle casual). Tienda in-app, pases de temporada, anuncios rewarded. |
| **Modelo de negocio** | F2P + microtransacciones (gemas, vidas, boosters) + pases de temporada + anuncios rewarded. ARPDAU ~$0.12, ARPU ~$3.50/mes. |
| **Procesos principales** | 1) Onboarding/tutorial 2) Sesiones diarias (15-20 min) 3) Live-Ops (eventos diarios/semanales) 4) Monetización (tienda, ads) 5) UA (TikTok, Unity Ads, Meta, Google UAC) 6) Retargeting / re-engagement. |
| **Situación actual** | Crecimiento plano desde Q2 2025. El equipo cree que "el tutorial no es suficiente" y "TikTok trae gente mala". Tienen análisis descriptivo (crashlytics, firebase) pero NO un sistema predictivo de churn. |
| **Problemas** | Retención D1 22% mediana (GameAnalytics 2026), churn 7d ~67% en la demo, budget de UA quemado sin LTV, desenganche silencioso, campañas de re-engagement genéricas sin personalizar. |
| **Necesidades** | 1) Ranking semanal D1-churn 2) Motivo de desenganche por segmento 3) Qué canal/tutorial trae jugadores que SÍ pagan 4) Demo usable por PMs no-técnicos. |

**Qué pierde si no actúa:** con 2M MAU y ARPDAU $0.12, cada punto de D1 retention = 20.000 jugadores/€30.000/mes en valor de retorno. A escala, un 5% de mejora en D1 = +$1.5M/año en LTV recuperada.

## 2. Datos disponibles (lo que PlayNova ya produce)

- **Jugadores:** device_id, app_version, región, país, dispositivo, OS, nivel, cuenta de jugador, fecha de install, última sesión, source attribution.
- **Eventos de juego:** session_length, tutorial_step, coins_spent, boosters_used, ads_watched, social_invites (agregado 7d por jugador).
- **Sesiones:** fecha, duración, tipo (casual/deep), push_notifications_recibidas, notificaciones abiertas.
- **Monetización:** compras in-app (gemas, vidas, boosters, pase_temporada), importe, fecha, IAP vs ad.
- **UA/Marketing:** campaña, canal (TikTok, Meta, Google UAC, Unity Ads), coste, install atribuido, primer evento post-install.
- **Onboarding:** tutorial_completed, session_1_length, friends_invited, days_to_session_2.
- **Support/reports:** reportes de jugador, tickets, baja de app.

## 3. Diseño de la base de datos

Tablas (SQLite `data/playnova_games.db`, schema en `data/schema.sql`):

- **campaigns(campaign_id PK, name, channel, game_target, cost_eur, start_date, end_date)** — campañas de UA (TikTok, Meta, Google UAC, Unity Ads).
- **players(player_id PK, device_id, region, country, os, app_version, level, account_age_days, acquisition_channel, acquisition_campaign_id FK, install_date, last_session_date)** — jugadores activos.
- **events(event_id PK, player_id FK, event_date, session_length, tutorial_step, coins_spent, boosters_used, ads_watched, social_invites)** — eventos de juego diarios agregados.
- **purchases(purchase_id PK, player_id FK, purchase_date, item_type, amount_eur)** — compras in-app.
- **leads(lead_id PK, campaign_id FK, install_date, country, os, device, tutorial_completed, session_1_length, friends_invited, days_to_session_2, converted_30d)** — nuevos installs + label conversión 30d.
- **player_features(player_id PK/FK, agregados 7d + churn_d7 label)** — agregado ventana 7d + label churn_7d para modelar. `days_since_last_session` se guarda para análisis (excluido del modelo, anti-leakage).

Claves foráneas: events.player_id → players, purchases.player_id → players, leads.campaign_id → campaigns, player_features.player_id → players.

## 4. Diagrama Entidad-Relación

Ver `docs/ER_diagram.mmd` (Mermaid, renderiza en GitHub). Tablas: CAMPAIGNS 1───∞ PLAYERS 1───∞ EVENTS; CAMPAIGNS 1───∞ LEADS; PLAYERS 1───1 PLAYER_FEATURES.

## Entregable día 11 — checklist
- [x] Ficha cliente completa
- [x] Lista de datos disponibles
- [x] `data/schema.sql` + diagrama ER
