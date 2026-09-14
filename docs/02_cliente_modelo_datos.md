# Día 11 — Cliente y modelo de datos (11 sept)

## 1. Ficha del cliente (ficticio pero realista)

| Campo | Detalle |
|---|---|
| **Nombre** | Riot Games — División EMEA / Live-Ops EUW (cliente piloto) |
| **Sector** | Videojuegos (free-to-play competitivo) |
| **Actividad** | Operación de League of Legends, Valorant y TFT en Europa. Eventos, ranked seasons, tienda, esports. |
| **Tamaño** | Grande: ~4500 empleados global, ~450 en EMEA (Dublín + Berlín). Facturación global ~1.8B€/año. |
| **Nº clientes (jugadores)** | ~32M MAU global; **muestra del proyecto: 8.000 jugadores actuales + 3.000 nuevos leads EUW** (cohorte 2024-2026, representativa). |
| **Productos** | LoL (MOBA), Valorant (FPS táctico), TFT (auto-battler), tienda (skins, pases, VP/RP), esports. |
| **Modelo de negocio** | Free-to-play + microtransacciones cosméticas + pases de batalla + patrocinios esports. ARPU ~35€/año. |
| **Procesos principales** | 1) Onboarding y tutorial 2) Matchmaking y ranked 3) Live-Ops (parches, eventos) 4) Moderación / anti-toxicidad 5) Tienda y monetización 6) Marketing de adquisición (Twitch, YouTube, TikTok, Discord, eventos). |
| **Situación actual** | Pico post-evento y caída posterior. El equipo cree que "el problema son los fines de semana", pero no tiene un sistema anticipativo. Solo reporting descriptivo. |
| **Problemas** | Churn silencioso (~17% a 60 días en la muestra), toxicidad que expulsa a nuevos, adquisición cara sin scoring, promociones genéricas sin personalizar. |
| **Necesidades** | 1) Ranking semanal de riesgo 2) Motivo de abandono por segmento 3) Qué campaña trae jugadores que SÍ se quedan 4) Demo usable por PMs no-técnicos. |

**Qué pierde si no actúa:** con 8.000 jugadores y ARPU 35€, cada punto de churn = 2.800€/año solo en la muestra. Escalado a EUW real (millones), cada punto son millones. Más colas largas y efecto contagio ("mis amigos lo dejan → yo también").

## 2. Datos disponibles (lo que Riot ya produce)

- **Clientes/jugadores:** cuenta, región, rango, nivel, antigüedad, país, edad aproximada.
- **Partidas:** fecha, duración, victoria/derrota, KDA, toxicidad, si juega con amigos, mensajes.
- **Sesiones/logins:** último login, frecuencia 7/30 días.
- **Tienda:** compras (skins, pases), importe, fecha.
- **Soporte/moderación:** reportes recibidos/emitidos, sanciones.
- **Marketing:** campañas, canal, coste, registros atribuidos.
- **Onboarding:** tutorial completado, partidas 1ª semana, amigos invitados, tiempo hasta 2ª sesión.

## 3. Diseño de la base de datos

Tablas (SQLite `data/riot_gaming.db`, schema en `data/schema.sql`):

- **players(player_id PK, riot_id, region, country, age_group, main_game, rank_tier, level, account_age_days, acquisition_channel, acquisition_campaign_id FK, acquisition_date, last_login_date)**
- **matches(match_id PK, player_id FK, match_date, game, duration_min, win, kills, deaths, assists, chat_messages, premade_size, toxicity_reports_received, toxicity_reports_made)**
- **purchases(purchase_id PK, player_id FK, purchase_date, item_type, amount_eur)**
- **campaigns(campaign_id PK, name, channel, game_target, cost_eur, start_date, end_date)**
- **new_leads(lead_id PK, campaign_id FK, signup_date, age_group, region, country, game_interest, tutorial_completed, matches_first_week, friends_invited, days_to_second_session, converted_30d)**
- **player_features(player_id PK/FK, agregados 30d + churn_60d label)** — vista materializada para modelar. `days_since_last_login` se guarda solo para análisis (excluido del modelo, anti-leakage).

Claves foráneas: matches.player_id → players, purchases.player_id → players, players.acquisition_campaign_id → campaigns, new_leads.campaign_id → campaigns, player_features.player_id → players.

## 4. Diagrama Entidad-Relación

Ver `docs/ER_diagram.mmd` (Mermaid, renderiza en GitHub). Tablas: CAMPAIGNS 1───∞ PLAYERS 1───∞ MATCHES / PURCHASES; CAMPAIGNS 1───∞ NEW_LEADS; PLAYERS 1───1 PLAYER_FEATURES.

## Entregable día 11 — checklist
- [x] Ficha cliente completa
- [x] Lista de datos disponibles
- [x] `data/schema.sql` + diagrama ER
