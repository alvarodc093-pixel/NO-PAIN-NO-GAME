# Día 12 — Datos + Website (12 sept)

## Parte 1 — Datos construidos

Generador: `src/generate_data.py` (seed 42, reproducible). Corte simulado: **2026-09-01**.

| Tabla | Filas | Descripción |
|---|---|---|
| campaigns | 8 | Twitch, TikTok, YouTube, Discord, Evento (costes 5k-20k€) |
| players | 8.000 | EUW, 3 juegos, 9 rangos, 6 países |
| matches | ~240.000 | Ventana 90 días, KDA, premade, toxicidad |
| purchases | ~10.000 | skins, battlepass, champions, points |
| new_leads | 3.000 | Registros 35-120 días antes del corte + label conversión 30d |
| player_features | 8.000 | Agregado 30d + label churn_60d |

Coherencia verificada: un jugador con 200 días de cuenta no tiene 5M de partidas; churn 60d ≈ **16-17%**; conversión 30d ≈ **44%**.
BD: `data/riot_gaming.db` (SQLite, schema en `data/schema.sql`).

Regenerar: `python src/generate_data.py` · Entrenar: `python src/train.py` → `models/churn_model.pkl`, `models/conversion_model.pkl`, `models/metrics.json`.

## Parte 2 — Website profesional (HTML + CSS + JS puro)

La web de la startup **es `web/index.html`**: landing inmersiva de una sola página con scroll interactivo, hero con parallax, contadores animados, hallazgos con las figuras del EDA, **simulador de churn en vivo** y calculadora de presupuesto.

- **Cero dependencias**: funciona offline, solo HTML + CSS + JS.
- **Identidad arcade neón**: fondo violeta profundo `#16132b`, primario cyan `#22d3ee`, secundario `#221c46` (definido en `web/styles.css`). Rojo `#ef4444` solo para churn, verde `#22c55e` para conversión (semántica).
- **Cabecera gamer**: `web/assets/header.png` generada con PIL, offline (sol, luna, confeti, destellos).
- **Simulador JS**: réplica fiel del modelo con el mismo logit calibrado (`src/fetch_riot.py` no tiene .pkl disponible en el entorno del navegador). Presets #92831 → 86 % y perfil sano → ~4 %.

Ejecutar:
```bash
cd web
python -m http.server 8321
# abrir http://localhost:8321
```

## Parte 3 — Calibración externa y validación real (cambios última hora)

- Calibración: `docs/07_fuentes_externas.md` — cada parámetro de `src/generate_data.py` cita fuente
  (Kim 2026, Kwak CHI'15, LEC 32:19, $1,8B cosmética, umbral 3 partidas).
- Validación real: `src/fetch_riot.py` — partidas reales EUW vía Riot API → `data/riot_real_*.csv`
  (necesita `$env:RIOT_API_KEY` de developer.riotgames.com). Ver página Metodología en `web/index.html`.

## Entregable día 12 — checklist
- [x] BD poblada y coherente
- [x] Website funcional (landing + demo en web profesional)
- [x] Identidad arcade + cabecera
- [x] Simulador JS réplica del modelo con coeficientes calibrados
- [x] Añadidos `matplotlib` y `requests` a `requirements.txt`
