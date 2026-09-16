# Análisis sobre datos reales

Notebook `notebooks/EDA.ipynb` (reproducible, abrir con Jupyter). Todo lo de abajo está medido en
`data/playnova_real.db` (16.447 filas). Figuras en `docs/img/` y `web/assets/`.

## Hallazgos verificados

### H1 — El engagement temprano separa a los que se quedan
- Churn por cuartil de horas en reseña: Q1 (≤18 h) **35,7%** → Q4 (>456 h) **13,2%**.
- Mediana de horas en reseña: churned 36,8 h vs activos 120,6 h.
- En el modelo, `log_hours_at_review` pesa 0.078 (churn) y **0.749** (conversión):
  el que se engancha pronto, se queda y vale más.

### H2 — Cada título vive una fase distinta (y se mide)
- Churn: Dota 2 5,2% · Apex 5,1% · TF2 8,8% · Warframe 8,4% · PoE 50,7% · Fall Guys 91,2%.
- La velocidad de reseñas lo delata: Dota genera 3.000 reseñas en 3 días; Fall Guys en 470.
- Lectura honesta: son tasas de la *muestra de reseñistas*, no retención de los juegos —
  pero ordenan correctamente la fase de vida de cada título, que es lo que un
  publisher necesita para repartir esfuerzo de Live-Ops por juego.

### H3 — Satisfacción ≠ retención
- Churn entre quienes recomiendan: **26,5%** vs no recomiendan: **29,6%**.
- `voted_up` pesa 0.005 en el churn: gustar no retiene. Retiene el hábito temprano.
- Implicación de producto: no optimices la nota media; optimiza la segunda sesión.

### H4 — El proxy de valor funciona y es estable por título
- high_value (top-25% horas + recomienda): 19,9% global, 15–24% por título.
- Drivers: horas en reseña (0.75) + título (0.10) + antigüedad (0.07).
- Validación por título: ROC 0.979–0.996 en los 6 juegos.

### H5 — El modelo generaliza dentro de cada juego
- Churn ROC por título: 0.891–0.924 en los 6. No memoriza títulos: discrimina
  jugadores dentro de cada comunidad (`python src/eval_per_title.py`).

### H6 — La etiqueta se verifica y no fuga al modelo (fig. 8)
- Regla (`src/build_real_dataset.py`): churn=1 si `hours_l2w==0` + `hours_forever>=2h` +
  `days_since_last_played>30d`; churn=0 si `hours_l2w>0`; resto = ambiguo (1.652 casos, 9,1% del crudo, excluidos).
- El escalón en 30 días y `hours_l2w==0` ⇔ churned es **por construcción** (`docs/img/eda_8_etiqueta.png`).
  Por eso `hours_l2w`, `days_since_last_played` y `hours_forever` nunca entran al modelo: sería fuga de etiqueta.

### H7 — Casi nada correlaciona en lineal salvo recencia/antigüedad (fig. 9)
- Pearson vs churn: `review_age_days` +0,63 · `days_since_last_played` +0,51 (definicional) ·
  `hours_l2w` −0,39 (definicional) · resto |r|<0,15 (`docs/img/eda_9_corr.png`).
- Hallazgo lateral: `num_games_owned` ↔ `num_reviews` correlacionan 0,83 (coleccionistas que reseñan mucho).
- Lectura: el churn es multifactorial y no lineal; el bosque (ROC 0,93) aporta sobre cualquier regla simple.

### H8 — El engagement protege en los 6 juegos (fig. 10)
- Corte por mediana global (80,6 h), churn horas bajas → altas, dentro de cada título:
  Dota 8%→4% · Apex 6%→4% · TF2 9%→8% · Warframe 10%→8% · PoE 59%→45% · Fall Guys 94%→81%.
- La dirección es universal aunque la magnitud cambie: evidencia EDA de generalización
  antes de la prueba formal por título (`docs/img/eda_10_engagement_titulo.png`).

### H9 — Perfil del reseñista: biblioteca en U, idioma no causal (fig. 11)
- Biblioteca: 0 juegos (52,6% filas, dato oculto de Steam) 25,5% · 1–20 13,3% (mínimo) ·
  21–100 28,7% · 101+ 47,8%. El coleccionista prueba y abandona.
- Idioma (top-8): ruso 12,9% y chino simplificado 18,0% abajo; brasileño 49,0% y francés 46,6% arriba.
  No es causal: correlaciona con el título que juega cada comunidad.
- Longitud de reseña casi plana (Q1 25,3% → Q4 30,9%): escribir mucho no predice quedarse.

### H10 — Ventana de muestreo desigual, la limitación mayor (fig. 12)
- Ventana (max−min fecha de reseña): Dota 3,4 días · Apex 15,4 · TF2 15,9 · Warframe 24,9 · PoE 96,0 · Fall Guys 469,4.
  Mediana de antigüedad: 1,9 días (Dota) → 269,7 días (Fall Guys).
- Por eso `review_age_days` domina la importancia de churn (0,50): es **proxy de título/fase**, no causa.
  Se compensa con validación por título y reportando tasas solo como *muestra de reseñistas*.

### H11 — Voto × hábito: el hábito manda (fig. 13)
- 2×2 (mediana 80,6 h): horas bajas + no recomienda **43,1%** vs horas altas + recomienda **18,2%**.
- Con horas altas el voto es irrelevante (17,8% vs 18,2%); con horas bajas suma ~8 pp (43,1% vs 34,5%).
- Prioridad Live-Ops: (1) horas tempranas, (2) voto solo como desempate en la banda baja.

### H12 — Calidad de datos (fig. 14)
- Ceros: `num_games_owned` 52,6% (oculto, no cuenta vacía) · `hours_l2w` 27,1% (por construcción) · resto <8%.
- Outliers reales sin recortar (`log1p` + bosque los absorben): juegos max 32.502 · reviews max 26.464 · reseña max 7.985 caracteres.
- Constantes: `early_access` y `refunded` son 0 en el 100% (importancia 0, ruido documentado).
- `received_free`: n=81 (0,5%), churn 93,8% — se reporta, no se decide con n=81. Sin nulos en las 16.447 etiquetadas.
