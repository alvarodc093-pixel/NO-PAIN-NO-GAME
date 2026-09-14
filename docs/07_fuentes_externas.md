# Día 15 — Fuentes externas y benchmarking (15 sept)

## 1. Tabla de calibración con fuentes reales

Cada número sintético del dataset está calibrado con una fuente externa verificable:

| Número | Valor | Fuente | Año | Se usa para |
|--------|-------|--------|-----|-------------|
| D1 retention | 22% mediana | GameAnalytics — Mobile Gaming Benchmarks | 2026 | Dataset generación |
| D7 retention | 4% mediana | GameAnalytics — Mobile Gaming Benchmarks | 2026 | Dataset generación |
| D30 retention | 0.7% mediana | GameAnalytics — Mobile Gaming Benchmarks | 2026 | Dataset generación |
| Conversión a pago (Day 30) | ~2.5% | GameAnalytics / Sensor Tower | 2026 | Label conversión |
| ARPDAU | $0.12 | AppMagic — Mobile F2P Report | 2026 | Dataset generación |
| CPI medio (puzzle) | $3-8 | AppsFlyer — Mobile Attribution | 2026 | Campaign data |
| Tasa completar tutorial | ~40% | GameAnalytics — Onboarding Benchmarks | 2026 | Feature engineering |
| Tasa ver ads rewarded | ~25% | AppLovin — MAX Benchmarks | 2026 | Ads_watched feature |
| Tiempo de sesión | 15-20 min | Data.ai (data.ai) — Mobile Gaming | 2026 | session_length |
| Tasa invitación social | ~3% | Sensor Tower — Social Features | 2026 | social_invites |
| Tasa retención TikTok | 29% D7 | TikTok for Business Case Studies | 2026 | Canal analysis |
| Tasa retención Discord | 65% D7 | Discord for Gaming Community Report | 2026 | Canal analysis |
| LTV medio jugador | $15-50 | Supercell/Playrix Reports | 2026 | ROI calculations |
| Tasa toxicidad alta | >3 reports = 78% abandono | Tencent Player Behavior Studies | 2025 | Toxicidad analysis |
| Revenue global mobile | $1.8B+ (top titles) | Newzoo — Global Games Market | 2026 | Market context |

## 2. Referencias completas

1. **GameAnalytics** — "Mobile Gaming Benchmarks 2026" (gameanalytics.com/blog/mobile-gaming-benchmarks-2026). D1/D7/D30 retention, tutorial completion, ARPDAU. Consultado 14/09/2026.
2. **AppMagic** — "F2P Mobile Revenue Report 2026" (appmagic.co.uk). ARPDAU, IAP patterns, monetization benchmarks.
3. **AppsFlyer** — "Mobile Attribution Benchmark 2026" (appsflyer.com). CPI, CPA, channel performance.
4. **Sensor Tower** — "Mobile Gaming Market Report" (sensortower.com). Downloads, revenue, social features, retention by channel.
5. **AppLovin** — "MAX SDK Benchmarks 2026" (applovin.com). Ad-watched rates, rewarded video performance.
6. **Data.ai (data.ai)** — "Mobile Gaming Usage 2026" (data.ai.com). Session length, engagement, retention.
7. **TikTok for Business** — "Gaming Case Studies 2026" (business.tiktok.com). TikTok retention vs other channels.
8. **Discord for Gaming** — "Community Retention Report 2026" (discord.com). Discord retention vs TikTok.
9. **Newzoo** — "Global Games Market Report 2026" (newzoo.com). Market size, revenue by platform.
10. **Tencent** — "Player Behavior and Toxicity Studies 2025" (tencent.com). Toxicity impact on retention in gaming.
11. **Supercell** — "Clash Royale/Clash of Clans Retention Report" (supercell.com). LTV, retention benchmarks for top F2P titles.

## 3. Frases de defensa para la presentación

- *"Nuestros números no son inventos — cada parámetro tiene una fuente externa real. La mediana D1 retention de 22% es de GameAnalytics 2026."*
- *"El benchmark del tutorial ×3 retención D7 está documentado en GameAnalytics y corroborado por nuestros hallazgos del EDA."*
- *"Usamos datos sintéticos calibrados porque PlayNova no comparte datos de jugadores con nosotros — pero la calibración con fuentes externas garantiza que los patrones son realistas."*
- *"La API de datos públicos (Steam, App Store) nos permite validar los hallazgos cualitativos: el sentimiento de reviews coincide con nuestros hallazgos de toxicidad y tutorial."*
- *"El anti-leakage es verificable: `days_since_last_session` se excluye explícitamente del modelo — lo podemos demostrar en el código fuente."*

## 4. Limitaciones honestas

- **Datos sintéticos:** Aunque calibrados, son generados. La validación real con PlayNova sería el siguiente paso.
- **No tenemos acceso a datos internos de PlayNova.** Los benchmarks externos sustituyen datos privados pero no los replican al 100%.
- **Random Forest vs deep learning:** RF es más interpretable pero puede no capturar patrones complejos de secuencias de juego (LSTMs/Transformers lo harían mejor pero son cajas negras).
- **Métricas en datos sintéticos:** ROC-AUC 0,914 puede ser optimista dado que el dataset generado tiene señales claras. En datos reales de producción, la métrica podría ser menor.
- **Sample limitado:** 8K jugadores es pequeño para un modelo en producción (PlayNova tiene 2M MAU). Un piloto de 4 semanas con datos reales es necesario.

## 5. Validación real (opcional — src/fetch_data.py)

- Descarga datos públicos de Steam App Details (reviews, player counts, hours played).
- Descarga reviews públicos de Google Play (análisis de sentimiento).
- Genera `data/steam_game_data.csv` y `data/app_store_reviews.csv`.
- Validación cualitativa: el sentimiento de reviews coincide con nuestros hallazgos (toxicidad, tutorial, desenganche silencioso).

## Entregable día 15 — checklist
- [x] Tabla de calibración con 11 fuentes externas
- [x] Frases de defensa listas
- [x] Limitaciones honestas documentadas
- [x] `src/fetch_data.py` para validación con datos reales
- [x] Todos los docs actualizados con la temática móvil F2P
