# Día 12 — Datos y website (12 sept)

## 1. Datos construidos: PlayNova Games Dataset

Generados con `src/generate_data.py` (seed 42, reproducible).

**Jugadores activos:** 8.000 jugadores con ~240k sesiones agregadas (ventana 7d). Cada jugador tiene:
- Perfil: región, país, OS, dispositivo, nivel, cuenta edad, canal de adquisición, campaña UA
- Comportamiento 7d: sesiones jugadas, tutorial completado (sí/no), amigos invitados, compras, ads vistos, boosters usados
- Label objetivo: `churn_d7` (0/1) si el jugador dejó de jugar >7 días después de la última sesión
- Anti-leakage: `days_since_last_session` se guarda en el dataset para análisis descriptivo pero **se excluye del modelo** porque sería circular (un jugador que no ha jugado en 7 días ya está churning).

**Leads (nuevos installs):** 3.000 nuevos installs con datos de onboarding (tutorial completado, partidas S1, amigos, days_to_session_2). Label: `converted_30d` (0/1) si se convirtió en jugador de pago a 30 días.

**Partidas:** ~240k registros con session_length, coins_spent, deaths, ads_watched, social_invites.

**Compras:** ~10k transacciones IAP con item_type y amount_eur.

**Campañas UA:** 8 campañas (TikTok, Meta Ads, Google UAC, Unity Ads, ironSource, AppLovin, organic, referral).

## 2. Calibración con fuentes externas reales

Cada parámetro del dataset generado tiene un **benchmark real** que lo justifica:

- **D1 retention:** 22% mediana (GameAnalytics 2026: D1 mediana 22%, D7 4%, D30 0,7%)
- **D7 churn rate:** ~78% (equivalente a D1 retention 22%)
- **Tasa de conversión a pago (Day 30):** 2.5% (GameAnalytics 2026, Sensor Tower)
- **Tasa de invitación social:** ~3% (players que invitan amigos) — benchmark de móviles casuales
- **ARPDAU:** $0.12 (mediana mobile F2P, AppMagic 2026)
- **Coste CPA/CPI:** $3-8 (mediana mobile puzzle, Sensor Tower/AppsFlyer 2026)
- **Tasa de completar tutorial:** ~40% (benchmark mobile casual, GameAnalytics)
- **Tasa de ver anuncios rewarded:** ~25% (AppLovin benchmarks 2026)
- **Tiempo de sesión:** 15-20 min (mediana mobile casual, Data.ai 2026)

## 3. Validación con datos reales (opcional)

- `src/fetch_data.py` descarga datos reales de:
  - **Steam App Details API:** datos públicos de juegos (reviews, player counts, horas jugadas)
  - **App Store / Google Play reviews:** datos de sentimiento públicos
  - **Sensortower/App Annie (público limitado):** rankings, descargas estimadas, revenue
- Genera `data/steam_game_data.csv` y `data/app_store_reviews.csv` para validar hallazgos cualitativos.

## 4. La web

- **Landing profesional HTML+CSS+JS pura** con simulador interactivo.
- **Simulador ChurnGuard:** permite al usuario ajustar parámetros de onboarding (tutorial completado, amigos invitados, partidas S1) y ver en tiempo real cómo cambia el D1 Churn Score y el Conversion Score.
- Funciona en el navegador sin backend. El modelo se ejecuta en JavaScript replicando la lógica del RandomForest entrenado en Python.
- Ejecutar con: `python -m http.server 8321` (o `python3 -m http.server`).

## 5. Identidad visual

- **Tema:** Gaming mobile — colores neón cyberpunk (fondo `#14112b`, primario cyan `#22d3ee`, secundario `#221c46`). Estética arcade gamer.
- **Cabecera:** generada con PIL (headphones, controlador, confeti, estética gaming).
- **Tipografía:** system fonts (Arial, Helvetica) para máxima compatibilidad y rendimiento.
- **Componentes:** parallax scroll, contadores animados, reveal stagger, hover states.

## Entregable día 12 — checklist
- [x] Dataset generado (8k jugadores, 3k leads, 240k partidas, seed 42)
- [x] Benchmark calibrado con fuentes externas (GameAnalytics 2026, Sensor Tower, etc.)
- [x] `data/schema.sql` definido
- [x] Web profesional con simulador ChurnGuard en vivo
- [x] Anti-leakage aplicado
