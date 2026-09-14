# 07 — Fuentes externas para calibrar lo que la API de Riot NO da

> Objetivo: que cada número sintético de `src/generate_data.py` tenga una fuente real detrás.
> La API pública (account-v1, summoner-v4, match-v5, league-v4) SÍ da: PUUID, nivel,
> rango, últimas partidas (win, KDA, duración). NO da: tienda, toxicidad, logins,
> tutorial, amigos, campañas ni churn_60d. Eso se calibra con estas fuentes.
> Ver también: `src/fetch_riot.py` (prueba real EUW vía API).

## Tabla de calibración (fuente → cifra → parámetro nuestro)

| Dato que la API no da | Fuente externa real | Cifra real | Parámetro nuestro en `generate_data.py` | Estado |
|---|---|---|---|---|
| Churn base 60d | Kim et al. 2026, survival analysis con 295.008 jugadores LoL | churn +8% a 60d, +20% a 90d; social reduce churn, tier alto lo sube | `churn_60d ≈ 16,5%` vía `logit = -1.6 + 1.4*solo + 1.2*tox - 2.2*(wr-0.5) - 0.18*act - 0.9*spender` | Cuadra: nuestra ventana 60d en activos, no installs nuevos |
| Retención temprana nuevos | Proyecto EUW con API real (princethoth, 12.760 jugadores) | 97% se va tras 1ª partida; D7 1,03%; llegar a 3 partidas → 8,6x retención (15,4% vs 1,8%) | `conv_30d ≈ 44%` como *lead registrado → habitual* (no install → D30); `logit_c` premia tutorial + partidas s1 + amigos | Cuadra si se explica así en defensa |
| Benchmarks retención general | GameAnalytics / InvestGame 2026 Mobile & PC Benchmarks | Mediana móvil D1 ~22%, D7 ~4%, D30 ~0,7%; PC D1 ~7%, D30 ~0,2% | Mismo punto: nuestro 44% es lead→hábito, superior a D30 installs por definición | Contexto, no contradicción |
| Toxicidad: prevalencia y reports | Kwak et al. CHI'15, 10M reports / 1,46M tóxicos LoL | Media 1,81 reports/partida reportada, mediana 1, mayoría <3; infra-reporte documentado | `toxicity_exposure = 18%`, `tox = Poisson(1.2) si expuesto else Poisson(0.15)` | Cuadra |
| Toxicidad: efecto sistema | Riot Jeff Lin (Tribunal) vía GameSpot/Recode | Abuso verbal -40%, 91,6% se reforma tras 1 sanción, odio al 2% partidas | `churn 0 reports 11,9% → 2+ reports 40,3%` (efecto x3 en modelo) | Hallazgo estrella defendible |
| Toxicidad: percepción | Encuesta casino.ca, 4.000 gamers 2024 | 36,11% dice LoL es la más tóxica en PC | Mismo punto anterior | Refuerzo |
| Monetización: tamaño | Trackers 2025-26 (Shanethegamer / Coopboardgames / Quantumrun) | LoL ~130M MAU, $1,65-1,80B/año, $18,92B lifetime 2009-24, todo cosmética/pases; Wild Rift +$67M 2025 | `spender = 35%`, `spent = Gamma(2,12)` si paga; ARPU muestra 35€/año | Defendible: muestra = activos EUW, no MAU global (incluye inactivos + China 55%) |
| Monetización: precios | Tienda real LoL | Skin ~12-15€, pase ~10€, campeones ~7€, puntos ~20€ | `price = {skin:12.5, battlepass:10.0, champions:7.0, points:20.0} + N(0,2)` | Cuadra |
| Duración partida | gol.gg LEC 2025 + ChainCC LRN 2025 | Media 32:19 (LEC), 31,4 min (LRN) | `avg_dur = N(32 LoL / 28 otros, 6)` | Exacto |
| Social retiene | Kim et al. 2026 (SPL) | Conexión social reduce churn global | `solo_prop ~ Beta(2,3)` media ~0,4; `churn grupo 12,8% → solo 23,7%` | Cuadra |
| Racha perdedora expulsa | Kim et al. 2026 (GPL: los 6 indicadores performance bajan churn) | Performance = predictor top | `winrate_30d` top-2 feature (0,24); `wr = N(0.52,0.1)` activos vs `N(0.38/0.30)` churned | Cuadra |
| Tutorial x3 | Proyecto EUW (umbral 3 partidas) + doctrina FTUE (valor en 5-15 min) | 3 partidas → 8,6x retención | `tut = 65% Discord/Evento/Twitch vs 45% resto`; `conv sin tut 20,4% → con tut 63,9%` | Segundo hallazgo defendible |
| Canales adquisición | Twitch 2025: 1,67B views LoL; Worlds 2025 pico 6,75M | Twitch = alta intención; TikTok = volumen baja intención | `conv TikTok 28,9% vs Discord/Evento ~65%, Twitch 47%`; `logit_c -0.6 si TikTok, +0.5 si Discord/Evento` | Cuadra |

## Referencias completas

1. Kim, Kim, Kim & Li (2026). *Analyzing player churn in esports games: a survival analysis of League of Legends log data.* Sport, Business and Management, 16(4), 453-474. https://doi.org/10.1108/SBM-04-2025-0093 — Ficha: https://www.emerald.com/sbm/article/16/4/453/1333130/Analyzing-player-churn-in-esports-games-a-survival
2. princethoth (2025). *League of Legends Player Retention Analytics* (datos vivos EUW vía Riot API, 12.760 jugadores). https://github.com/princethoth/league-of-legends-product-analytics
3. Kwak, Blackburn & Han (CHI'15). *Exploring Cyberbullying and Other Toxic Behavior in Team Competition Online Games* (10M reports, 1,46M tóxicos). https://ar5iv.labs.arxiv.org/html/1504.02305
4. Riot Jeff Lin / Recode vía GameSpot (2015). *Reporting System Has Reduced Verbal Abuse.* https://www.gamespot.com/articles/league-of-legends-reporting-system-has-reduced-ver/1100-6428733
5. Esports News UK / casino.ca (2024). *LoL y CoD, comunidades más tóxicas; 36,11% LoL en PC (n=4.000).* https://esports-news.co.uk/2024/10/24/cod-lol-toxic-gaming-communities
6. ShaneTheGamer (2026). *League of Legends Statistics 2026 — 130M Players, $18B.* https://www.shanethegamer.com/research/league-of-legends-statistics
7. Coopboardgames (2026). *League of Legends Player Data and Statistics 2026* (~130M MAU, $1,65-1,80B/año). https://coopboardgames.com/online-gaming/league-of-legends
8. Games of Legends. *LEC 2025 Summer stats* (duración media 32:19). https://gol.gg/teams/team-stats/2533/split-ALL/tournament-LEC%202025%20Summer%20Season
9. ChainCC. *LRN 2025 Split 2 stats* (media 31,4 min). https://chaincc.lol/free/leagues/LRN/2025/split-2
10. GameAnalytics / InvestGame (ene-2026). *2026 Mobile & PC Gaming Benchmarks* (D1 ~22%, D7 ~4%, D30 ~0,7%). https://investgame.net/wp-content/uploads/2026/01/2026-01-27-2026-mobile-pc-benchmarks_compressed.pdf
11. Riot Developer Portal. *APIs + Getting Started* (account-v1, summoner-v4, match-v5, league-v4; dev key 24h). https://developer.riotgames.com/apis

## Frases para defensa

- *"La API no da tienda, toxicidad ni churn: los calibramos con Kim 2026 (295k LoL), Kwak CHI'15 (10M reports) y benchmarks GameAnalytics 2026. Detalle en docs/07."*
- *"Nuestro 16,5% a 60d cuadra con Kim (+8% a 60d). Nuestro 44% es lead→hábito, no install→D30 (0,7% mediano), por eso es mayor."*
- *"La duración 32 min es la media real LEC/LRN. Los precios son tienda real."*
- *"Y lo validamos con partidas reales EUW vía API: src/fetch_riot.py."*

## Limitaciones honestas (decirlas antes de que pregunten)

- Sintético calibrado ≠ real: pedimos backtest con 1 cohorte real de 30 días.
- ARPU 35€ es de muestra activa EUW, no MAU global ($13,5/MAU). Decirlo así evita la pregunta trampa.
- Matiz Kim: tier alto sube churn por frustración; en nuestra muestra Challenger es 7,1% (élite que aguanta). Discrepancia menor, documentada.
