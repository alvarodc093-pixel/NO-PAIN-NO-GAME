# Día 13 — Análisis y descubrimiento (13 sept)

Análisis reproducible: `notebooks/01_eda.py` (lee `data/riot_gaming.db`, guarda figuras en `docs/img/`).
Métricas de modelos: `models/metrics.json` (`src/train.py`).

## Limpieza
Sin nulos salvo `days_to_second_session` (lead con 1 sola sesión → se imputa a 9.0 y se documenta).
Tipos validados, fechas ISO, FKs activas. Sin duplicados de `player_id`.

## Hallazgos clave (lo que Riot NO sabía)

El cliente creía: *"perdemos jugadores el fin de semana por falta de contenido"*.
Los datos dicen otra cosa:

1. **La toxicidad expulsa (x3).** Churn con 0 reportes ≈ **12%** → con 2+ reportes ≈ **40%**. No es contenido, es comunidad.
2. **Jugar solo mata.** Churn en grupo ≈ **13%** → solo queue ≈ **24%**. El factor social retiene casi el doble.
3. **El que no paga se va.** Gasto 0€ ≈ **20%** churn → >20€ ≈ **10%**. El pase/battlepass es ancla de retención.
4. **TikTok trae volumen pero no comunidad.** Conversión TikTok ≈ **29%** vs Discord/Evento ≈ **65%** / Twitch ≈ 47%. El CAC barato sale caro.
5. **El tutorial lo es todo.** Conversión sin tutorial ≈ **20%** → con tutorial ≈ **64%** (x3). Y volver pronto importa: `days_to_second_session` es la feature nº1 del Conversion Score.
6. **Racha perdedora = abandono.** `winrate_30d` es top-2 del Churn Score. Solo-queue + derrota encadenada = segmento crítico.

Segmento crítico detectado: **solo-queue + 2+ reportes + winrate <40% + 0€ gastado → churn >50%** (vs ~17% global).

## 3 problemas/oportunidades

| # | Problema empresarial | Problema de datos | Valor |
|---|---|---|---|
| P1 (ELEGIDO) | ~17% de jugadores dejan de jugar en 60 días sin aviso; Live-Ops reacciona tarde con promos genéricas | Clasificar P(churn_60d) por jugador + explicar motivo + priorizar top-N accionable | Retener 10% de los que se van = ~130 jugadores/muestra (~4.550€/año) y millones a escala real |
| P2 | TikTok/YouTube traen registros que no cuajan; presupuesto de adquisición mal repartido | Predecir P(conversión_30d) por lead + comparar conversión real por canal | Reasignar 20% del spend a Discord/Evento/Twitch = +15-20% retained players con mismo budget |
| P3 | Toxicidad y solo-queue detectados tarde (soporte colapsado) | Detección temprana de perfiles con toxicidad recibida + recomendación (squad, descanso, mute) | -toxicidad, +sesiones en grupo, -churn contagio |

## Problema seleccionado → traducción a Data Science

> **P1 — Churn Score:** dado el comportamiento 30d (partidas, winrate, KDA, toxicidad, social, gasto), estimar **P(abandono en 60 días)** por jugador, ordenar por riesgo, segmentar motivo (quemado por derrotas / solo y tóxico / desenganchado silencioso / nunca enganchó al pago) y recomendar acción (squad suggestion, misión comeback, pausa + recompensa, oferta pase).

Secundario (línea futura): **Conversion Score** para leads (P(habitual a 30d)) — ya entrenado como MVP ligero (ROC-AUC ~0,82).

## Entregable día 13 — checklist
- [x] EDA + visualizaciones (`notebooks/01_eda.py` + app)
- [x] 3 problemas + 1 seleccionado + traducción a DS
