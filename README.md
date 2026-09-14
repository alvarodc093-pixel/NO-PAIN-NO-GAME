# ChurnGuard — Proyecto Bootcamp Startup (Días 10-15)

**Propuesta de valor:** detecta el abandono antes de que ocurra. Churn a 7 días con motivo+acción y conversión a pago a 30 días para juegos móviles F2P.

## El problema (en €)

- Churn 7d del **67%** en el dataset demo calibrado. Con CPI $5 y 10.000 installs/mes, ~6.700 se pierden: **~$33.500/mes en UA sin retorno**.
- Benchmarks: D1 22% / D7 4% / D30 0,7% (GameAnalytics 2026).

## Los productos

1. **Churn Score 7d** (principal): probabilidad de abandono + motivo + acción. ROC-AUC **0.914**, PR-AUC **0.950**, F1 **0.883** (thr 0,50).
2. **Conversion Score 30d** (UA): probabilidad de pago a 30 días. ROC-AUC **0.901**, PR-AUC **0.279**, F1 **0.490** (thr 0,40 sintonizado; recall 0.758, precision 0.362).

## Los datos

- **8.000 jugadores** + **3.000 leads** + **~53.000 sesiones** + **~800 compras** (SQLite, seed 42, `src/generate_data.py`).
- Churn por logit con solape real (sin separación perfecta); canal propagado a features; conversión ~5,4%.
- Anti-leakage: `days_since_last_session` y el `device` aleatorio de leads, **excluidos** del modelo.
- Modelos en `models/` (`.pkl` con encoders incluidos) + métricas en `models/metrics.json`.

## La web

Landing en `web/` (HTML+CSS+JS, cero dependencias): hero con mock del ranking, benchmarks, figuras del EDA, métricas honestas (ROC **y** PR-AUC), simulador con motivo+acción, calculadora de ROI, piloto de 4 semanas (2.500 €), integración/GDPR y FAQ de CTO.

```bash
pip install -r requirements.txt
python src/generate_data.py
python src/train.py
python notebooks/01_eda.py
cd web
python -m http.server 8321   # → http://localhost:8321
```

## Estructura

```
├── docs/          # Guías días 10-15 + 07_fuentes_externas.md
├── web/           # Landing + assets (figuras copiadas de docs/img/)
├── src/           # generate_data.py, train.py, fetch_data.py
├── data/          # schema.sql (+ .db generada, ignorada en git)
├── models/        # .pkl + metrics.json (versionados)
├── notebooks/     # 01_eda.py reproducible
├── bootcamp/      # Storytelling .docx
├── requirements.txt
└── .gitignore
```

## Métricas (test, seed 42)

| | Thr | ROC-AUC | PR-AUC | Acc | Prec | Rec | F1 |
|---|-----|---------|--------|-----|------|-----|-----|
| Churn 7d | 0,50 | 0.914 | 0.950 | 0.844 | 0.888 | 0.878 | 0.883 |
| Conversión 30d | 0,40 | 0.901 | 0.279 | 0.913 | 0.362 | 0.758 | 0.490 |

> En conversión manda el PR-AUC (5,4% de positivos), no el ROC. El threshold 0,40 maximiza F1: captura el 76% de futuros pagadores porque un push innecesario es barato y un pagador perdido es caro.

## Licencia

Proyecto bootcamp Startup — 14/09/2026. Cliente piloto ficticio (PlayNova Games). Dataset demo sintético y calibrado.
