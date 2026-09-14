# 🎮 NO PAIN, NO GAME

**Startup de Data Science para gaming: detectamos al jugador que se va a ir antes de que se vaya — y te decimos qué hacer para que se quede.**

> Primer producto para **Riot Games (EUW)**: *Churn Score* (probabilidad de abandono a 60 días por jugador + motivo + acción) y, como segunda línea, *Player Conversion Score* (probabilidad de que un nuevo registro sea habitual a 30 días).

- 🔴 Ejemplo: Jugador #92831 → **abandono 86 %** → solo-queue + toxicidad + racha de derrotas → *sugerir squad + misión comeback*.
- 🟢 Ejemplo: Nuevo jugador #18372 → **conversión 82 %** → tutorial + 8 partidas + amigos → *priorizar onboarding*.

## Demo en 3 comandos

```bash
pip install -r requirements.txt
python src/generate_data.py   # crea data/riot_gaming.db (8.000 players, ~241k partidas, 3.000 leads)
python src/train.py           # entrena y guarda models/*.pkl + models/metrics.json
cd web && python -m http.server 8321
# abrir http://localhost:8321
```

# opcional, prueba REAL con API de Riot (dev key 24h):
# $env:RIOT_API_KEY="RGAPI-xxxx"; python src/fetch_riot.py --players "Rekkles#EUW,Caps#EUW1" --matches 20

## Web profesional (HTML+CSS+JS, sin Streamlit)

Landing inmersiva de una sola página con scroll interactivo: hero con parallax, contadores animados,
hallazgos con las figuras reales del EDA, **simulador de churn en vivo** (réplica JS: preset #92831 → 86 %)
y calculadora de budget. Cero dependencias, funciona offline.

```
web/index.html + web/styles.css + web/app.js  # landing (hero, hallazgos, demo JS, valor, FAQ)
web/assets/                                    # header.png + figuras EDA (fig-*.png)
```

## Resultados (test, reproducibles)

| Modelo | Acc | Prec | Rec | ROC-AUC |
|---|---|---|---|---|
| Churn Score (n=1.600) | 0,946 | 0,793 | 0,913 | **0,985** |
| Conversion Score (n=600) | 0,763 | 0,726 | 0,748 | **0,821** |

Hallazgo estrella: toxicidad 0 reportes → 11,9 % churn; 2+ → **40,3 %**. Solo-queue 23,7 % vs grupo 12,8 %. Tutorial x3 conversión (20→64 %). TikTok 29 % vs Discord/Evento ~65 %.

Decisión técnica defendible: `days_since_last_login` **excluido** de features (sería leakage; avisamos antes, no cuando ya lleva 30 días fuera).

## Estructura

```
web/index.html + web/styles.css + web/app.js  # producto principal (web profesional)
web/assets/                                    # header.png (cabecera gamer PIL) + figuras EDA
src/generate_data.py | src/train.py           # datos + modelos
src/fetch_riot.py                             # validación REAL vía Riot API (match-v5 EUW → data/riot_real_*.csv)
data/schema.sql + data/riot_gaming.db         # BD SQLite + ER en docs/ER_diagram.mmd
notebooks/01_eda.py → docs/img/               # EDA + figuras
docs/01..05_*.md                              # días 10-14
docs/06_presentacion_guion.md                 # guion de presentación (eliminado, trasladado a bootcamp/NO_PAIN_NO_GAME_Storytelling.docx)
docs/07_fuentes_externas.md                   # benchmarks reales que calibran lo que la API no da
models/churn_model.pkl, conversion_model.pkl, metrics.json
web/index.html + web/styles.css + web/app.js  # web profesional
```

Docs por día: `docs/01_idea_startup.md` (día 10) · `02_cliente_modelo_datos.md` (día 11) · `03_datos_website.md` (día 12) · `04_analisis.md` (día 13) · `05_solucion.md` (día 14) · `07_fuentes_externas.md` (calibración: Kim 2026, Kwak CHI'15, GameAnalytics 2026, LEC 32:19). Storytelling día 15 (guion 10 min): `..\NO_PAIN_NO_GAME_Storytelling.docx` en la carpeta bootcamp.

Datos: sintética calibrada con fuentes reales (docs/07) + validación opcional con partidas reales EUW (`src/fetch_riot.py`, necesita `RIOT_API_KEY` de developer.riotgames.com). La API pública no da tienda, toxicidad, logins ni churn: por eso el modelo entrena en sintética y se valida en real.
