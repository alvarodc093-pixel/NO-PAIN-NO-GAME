# ChurnGuard — Proyecto Bootcamp Startup (Días 10-15)

**Propuesta de valor:** detecta el abandono desde señales tempranas. Churn + jugador de alto valor para juegos F2P — con **datos 100% reales**.

## Datos reales (cero sintéticos)

- **18.099 reseñas públicas de Steam** (API pública, sin key, 2026-09-14) de 6 títulos F2P:
  Dota 2, TF2, Warframe, Path of Exile, Apex Legends, Fall Guys.
- **16.447 jugadores etiquetados** en `data/playnova_real.db`: churn **27,1%** · high_value **19,9%**.
- Labels auditables + anti-fuga por diseño (el modelo nunca ve recencia ni horas totales).
- Procedencia, mapeo, sesgos y validez por título: `docs/08_datos_reales.md`.

## Los productos (modelos `real_*`, test 3.290, seed 42)

1. **Churn Score**: ROC-AUC **0.930**, PR-AUC **0.872** (base 0,271), F1 **0.817** (thr 0,50).
   Validez por título: ROC 0.891–0.924 en los 6 juegos.
2. **Conversion Score** (high_value = top-25% horas + recomienda, proxy transparente):
   ROC-AUC **0.972**, PR-AUC **0.873** (base 0,199), F1 **0.847** (thr 0,60).
   Validez por título: ROC 0.979–0.996.

## Pipeline reproducible

```bash
pip install -r requirements.txt
python src/fetch_steam_reviews.py    # ~5 min, 18k reseñas → data/real/
python src/build_real_dataset.py    # → data/playnova_real.db + data/real_summary.json
python src/train_real.py            # → models/real_*.pkl + models/real_metrics.json
python notebooks/02_eda_real.py     # figuras en docs/img/ (+ copia a web/assets/)
python src/eval_per_title.py        # validez por título
cd web
python -m http.server 8321          # → http://localhost:8321
```

## Estructura

```
├── docs/          # guías días 10-15 + 07_fuentes + 08_datos_reales (procedencia)
├── web/           # landing + assets (figuras del EDA real)
├── src/           # fetch/build/train_real/eval (generate_data.py y train.py: retirados)
├── data/          # playnova_real.db + real_summary.json (versionados; crudo .jsonl ignorado)
├── models/        # real_*.pkl + real_metrics.json (versionados)
├── notebooks/     # 02_eda_real.py
├── bootcamp/      # storytelling .docx
└── requirements.txt
```

## Hallazgos (medidos)

- Engagement temprano: churn Q1 (≤18 h) **35,7%** → Q4 **13,2%**.
- Satisfacción ≠ retención: recomienda 26,5% vs no recomienda 29,6% de churn.
- Fase de vida por título medible (velocidad de reseñas: Dota 3 días vs Fall Guys 470 días por 3.000 reseñas).

## Licencia

Bootcamp Startup — 14/09/2026. Cliente piloto ficticio (PlayNova Games). Dataset derivado de datos públicos de Steam.
