# Día 12 — Datos reales y website (12 sept)

## 1. Dataset REAL: 18.099 reseñas de Steam → 16.447 jugadores etiquetados

Pipeline (todo reproducible, seed 42):

1. `python src/fetch_steam_reviews.py` — descarga reseñas públicas de 6 títulos F2P
   (Dota 2, TF2, Warframe, PoE, Apex, Fall Guys; ~3.000 por título).
2. `python src/build_real_dataset.py` — construye `data/playnova_real.db`
   (tablas `titles`, `reviews`) + `data/real_summary.json`.
3. `python src/train_real.py` — entrena ambos modelos → `models/real_*.pkl` + `models/real_metrics.json`.
4. `python notebooks/02_eda_real.py` — EDA y figuras en `docs/img/` (copiadas a `web/assets/`).

Números reales: **churn 27,1%** · **high_value 19,9%** · recomienda 80,0% ·
mediana 95,7 h totales · 1.652 ambiguos excluidos (9,1%, contados en el resumen).
Detalle completo de procedencia, labels, anti-fuga y sesgos: `docs/08_datos_reales.md`.

## 2. Benchmarks externos (contexto de mercado, no datos)

- Retención móvil D1 22% / D7 4% / D30 0,7% (GameAnalytics 2026) — el problema existe.
- Conversión a pago F2P 2–5% (Sensor Tower 2026) — nuestro proxy high_value (19,9%)
  es deliberadamente más amplio: segmento monetizable, no pagadores observados.
- CPI puzzle $3–8 (AppsFlyer), ARPDAU $0.12 (AppMagic).

## 3. La web

- Landing en `web/` (HTML+CSS+JS, cero dependencias) con números 100% medidos:
  hero con mock del ranking, tabla de benchmarks, figuras del EDA real servidas
  desde `web/assets/`, métricas con ROC **y** PR-AUC, simulador con motivo+acción,
  calculadora de ROI, piloto de 4 semanas (2.500 €) y FAQ de CTO.
- El simulador es demo ilustrativa calibrada (declarado en la web).
- Servir desde la carpeta web: `cd web` y `python -m http.server 8321`.

## Entregable día 12 — checklist
- [x] Dataset 100% real descargado, construido y versionado (DB + resumen)
- [x] `docs/08_datos_reales.md` con procedencia, mapeo, labels y sesgos
- [x] Scripts sintéticos retirados (`generate_data.py`, `train.py` marcados legacy)
- [x] Web reescrita sobre números medidos
