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
| **Necesidades** | 1) Ranking semanal de churn 2) Motivo por segmento 3) Qué perfiles llegan a alto valor 4) Demo usable por PMs no-técnicos. |

**Qué pierde si no actúa:** con 2M MAU y ARPDAU $0.12, cada punto de D1 retention = 20.000 jugadores/€30.000/mes en valor de retorno. A escala, un 5% de mejora en D1 = +$1.5M/año en LTV recuperada.

## 2. Datos: de la wishlist al dataset real

La lista original (telemetría interna ideal) se sustituyó por datos 100% reales y
auditables. Lo que PlayNova produciría en el piloto vs lo que usamos hoy:

- **Piloto (eventos internos):** sesiones, progresión/tutorial, compras, atribución de canal.
- **Hoy (Steam público):** por reseña — `playtime_forever/at_review/last_two_weeks`,
  `last_played`, `num_games_owned/reviews`, `voted_up`, longitud, idioma, fechas,
  early access, gratis/de pago. Mapeo completo en `docs/08_datos_reales.md`.

## 3. Diseño de la base de datos (real)

SQLite `data/playnova_real.db`, construida por `src/build_real_dataset.py`:

- **titles(appid PK, name, p75_hours)** — 6 títulos F2P.
- **reviews(review_id PK, appid FK, voted_up, hours_forever/at_review/l2w,
  days_since_last_played, review_age_days, review_len, num_games_owned/reviews,
  early_access, received_free, refunded, language, timestamp_created,
  churn NULL|0|1, high_value 0|1)** — 18.099 filas (16.447 etiquetadas).

Claves: reviews.appid → titles.appid. (El schema sintético antiguo `data/schema.sql`
quedó obsoleto con el cambio a datos reales.)

## 4. Diagrama Entidad-Relación

Ver `docs/ER_diagram.mmd` (Mermaid, renderiza en GitHub). Tablas: TITLES 1───∞ REVIEWS.

## Entregable día 11 — checklist
- [x] Ficha cliente completa
- [x] Lista de datos disponibles
- [x] `data/playnova_real.db` + diagrama ER real
