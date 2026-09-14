# ChurnGuard — Proyecto Bootcamp Startup (Días 10-15)

**Propuesta de valor:** Detecta el abandono antes de que ocurra. Predicción de churn D7 y conversión a pago para juegos móviles F2P.

## El Problema

Los juegos móviles F2P pierden al 97% de nuevos jugadores antes de la primera semana. La retención D1 mediana es 22%, D7 es 4%, D30 es 0.7% (GameAnalytics 2026). Los publishers gastan $3-8 por jugador adquirido sin saber quién va a abandonar.

## Los Productos

1. **D1 Churn Score:** Probabilidad de abandono a 7 días por jugador + motivo de desenganche + acción de retención automatizada. ROC-AUC 0.914, recall 1.000.
2. **Conversion Score:** Probabilidad de que un nuevo install se convierta en jugador de pago a 30 días. ROC-AUC 0.973, accuracy 0.980.

## Los Datos

- **8.000 jugadores** + 3.000 leads + ~240k partidas (SQLite, seed 42)
- Calibración con fuentes reales: GameAnalytics 2026, Sensor Tower, AppsFlyer, AppMagic, Data.ai
- Anti-leakage: `days_since_last_session` excluido del modelo
- Validación opcional con datos reales: `src/fetch_data.py`

## La Web

Landing profesional HTML+CSS+JS pura con:
- Hero con parallax y contadores animados
- Tabla de benchmarks con fuentes externas
- Simulador ChurnGuard en vivo (modelo JS replicando el RF entrenado)
- Calculadora de budget de UA
- FAQ acordeones
- 100% funcional sin backend

Ejecutar: `python -m http.server 8321`

## La Estructura

```
├── docs/          # Guías bootcamp días 10-15 + fuentes externas
├── web/           # Landing HTML+CSS+JS
├── src/           # Python: generate_data.py, train.py, fetch_data.py
├── data/          # SQLite DB, schema.sql
├── models/        # Modelos .pkl + metrics.json
├── notebooks/     # EDA reproducible
├── docs/img/      # Figuras del EDA
├── requirements.txt
└── .gitignore
```

## Métricas del Modelo

| | ROC-AUC | Accuracy | Precision | Recall | F1 |
|---|---------|-----------|--------|-----|-----|
| Churn Score | 0.914 | 0.958 | 0.948 | 1.000 | 0.973 |
| Conversion Score | 0.973 | 0.980 | 0.125 | 0.167 | 0.143 |

> Nota: La precision/recall bajas del Conversion Score se deben al desbalance de clases (~2.5% de convertidos). El ROC-AUC de 0.973 demuestra excelente discriminación.

## Instalación

```bash
pip install -r requirements.txt
python src/generate_data.py
python src/train.py
python -m http.server 8321
```

## Licencia

Proyecto bootcamp Startup — 14/09/2026
