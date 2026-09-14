# Día 12 — Datos y website (12 sept)

## 1. Datos construidos: PlayNova Games Dataset

Generados con `src/generate_data.py` (seed 42, reproducible). Números reales de la última generación:

- **8.000 jugadores** · **3.000 leads** · **~53.000 sesiones** (tabla `events`) · **~800 compras** IAP · 8 campañas UA.
- **Churn 7d: 67,0%** · **conversión a pago 30d: 5,4%** · **tutorial completado: 38,5%**.
- Cada jugador tiene: perfil (región, país, OS, nivel, antigüedad, canal y campaña de adquisición), comportamiento 7d (sesiones, tutorial, amigos invitados, monedas, ads, boosters) y label `churn_d7`.
- Cada lead tiene: onboarding (tutorial, duración sesión 1, amigos, días hasta 2ª sesión) y label `converted_30d`.
- **Generación honesta:** el churn se decide por logit (tutorial + social + nivel + canal + ruido) y las sesiones son su consecuencia ruidosa — hay solape real entre clases, sin separación perfecta.
- Anti-leakage: `days_since_last_session` se guarda solo para análisis y **se excluye del modelo** (sería circular). El identificador `device` de leads también se excluye (es aleatorio).

## 2. Calibración con fuentes externas reales

- **Retención:** churn 67% a 7d, coherente con la crisis de retención móvil (D1 22% / D7 4% / D30 0,7% mediana · GameAnalytics 2026).
- **Conversión a pago:** 5,4% a 30d, en el rango alto F2P mid-core (2–5% · Sensor Tower 2026) — elegida así a propósito para tener suficientes positivos y métricas estables.
- **Tutorial:** 38,5% completion (~40% casual · GameAnalytics).
- **Economía:** ARPDAU $0.12 (AppMagic 2026) · CPI puzzle $3–8 (AppsFlyer 2026) · sesión 15–20 min (Data.ai 2026).
- **Canales (medido en el dataset):** orgánico 42,3% retenidos · referral 37,3% · TikTok 30,9% · resto paid 29–33%. El orden coincide con la tesis volumen-vs-calidad.

## 3. Validación con datos reales (opcional)

- `src/fetch_data.py` descarga Steam App Details y reseñas públicas para validar cualitativamente (sentimiento sobre tutorial, anuncios y abandono).
- Genera `data/steam_game_data.csv` y `data/app_store_reviews.csv`.

## 4. La web

- Landing en `web/` (HTML+CSS+JS, cero dependencias): hero con mock del ranking semanal, contadores animados, tabla de benchmarks, figuras del EDA servidas desde `web/assets/`, dos productos con métricas honestas (ROC **y** PR-AUC), simulador con motivo+acción, calculadora de ROI, plan piloto de 4 semanas con precio, integración/GDPR y FAQ de CTO.
- El simulador es una **demo ilustrativa calibrada**, no el modelo productivo (declarado en la propia web y en el FAQ).
- Servir desde la carpeta web: `cd web` y `python -m http.server 8321` → `http://localhost:8321`.

## 5. Identidad visual

- Neón cyberpunk (`#14112b` + cyan `#22d3ee` + violeta `#8b5cf6`), orbes con parallax, grid, reveal on-scroll, mock de dashboard, tablas y gauge SVG. Responsive con CTA de piloto siempre visible.

## Entregable día 12 — checklist
- [x] Dataset regenerado con logit realista (churn 67%, conv 5,4%, seed 42)
- [x] Benchmark calibrado con fuentes externas
- [x] `data/schema.sql` + canal propagado a `player_features`
- [x] Web reescrita: vistosa, honesta y orientada a piloto
- [x] Figuras del EDA regeneradas y copiadas a `web/assets/`
