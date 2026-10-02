# Análisis sobre datos reales

Notebook `notebooks/EDA.ipynb` (reproducible, abrir con Jupyter). Todo lo de abajo está medido en
`data/playnova_real.db` (39.478 filas). Figuras en `docs/img/` y `web/assets/`.

## Hallazgos verificados

### H1 — El engagement temprano separa a los que se quedan
- Churn por cuartil de horas en reseña: Q1 (≤19 h) **44,1%** → Q4 (>498 h) **22,1%**.
- Mediana de horas en reseña: churned 45,7 h vs activos 135,5 h.
- En el modelo, `log_hours_at_review` pesa 0.067 (churn) y **0.750** (conversión):
  el que se engancha pronto, se queda y vale más.

### H2 — Cada título vive una fase distinta (y se mide)
- Churn: Dota 2 6,4% · Apex 8,4% · TF2 13,4% · Warframe 17,5% · PoE 71,1% · Fall Guys 93,7%.
- La velocidad de reseñas lo delata: Dota genera 6.800 reseñas en 21 días; Fall Guys en 804.
- Lectura honesta: son tasas de la *muestra de reseñistas*, no retención de los juegos —
  pero ordenan correctamente la fase de vida de cada título, que es lo que un
  publisher necesita para repartir esfuerzo de Live-Ops por juego.

### H3 — Satisfacción ≠ retención
- Churn entre quienes recomiendan: **34,3%** vs no recomiendan: **35,2%**.
- `voted_up` pesa 0.005 en el churn: gustar no retiene. Retiene el hábito temprano.
- Implicación de producto: no optimices la nota media; optimiza la segunda sesión.

### H4 — El proxy de valor funciona y es estable por título
- high_value (top-25% horas + recomienda): 20,0% global, 15–24% por título.
- Drivers: horas en reseña (0.75) + título (0.11) + antigüedad (0.07).
- Validación por título: ROC 0.971–0.993 en los 6 juegos.

### H5 — El modelo generaliza dentro de cada juego
- Churn ROC por título: 0.852–0.917 en los 6. No memoriza títulos: discrimina
  jugadores dentro de cada comunidad (`python src/eval_per_title.py`).

### H6 — La etiqueta se verifica y no fuga al modelo (fig. 8)
- Regla (`src/build_real_dataset.py`): churn=1 si `hours_l2w==0` + `hours_forever>=2h` +
  `days_since_last_played>30d`; churn=0 si `hours_l2w>0`; resto = ambiguo (2.082 casos, 5,0% del crudo, excluidos).
- El escalón en 30 días y `hours_l2w==0` ⇔ churned es **por construcción** (`docs/img/eda_8_etiqueta.png`).
  Por eso `hours_l2w`, `days_since_last_played` y `hours_forever` nunca entran al modelo: sería fuga de etiqueta.

### H7 — Casi nada correlaciona en lineal salvo recencia/antigüedad (fig. 9)
- Pearson vs churn: `review_age_days` +0,60 · `days_since_last_played` +0,49 (definicional) ·
  `hours_l2w` −0,43 (definicional) · `appid` +0,26 · resto |r|<0,11 (`docs/img/eda_9_corr.png`).
- Hallazgo lateral: `num_games_owned` ↔ `num_reviews` correlacionan 0,73 (coleccionistas que reseñan mucho).
- Lectura: el churn es multifactorial y no lineal; el bosque (ROC 0,93) aporta sobre cualquier regla simple.

### H8 — El engagement protege en los 6 juegos (fig. 10)
- Corte por mediana global (88,1 h), churn horas bajas → altas, dentro de cada título:
  Dota 10%→4% · Apex 11%→6% · TF2 15%→11% · Warframe 23%→14% · PoE 77%→67% · Fall Guys 96%→86%.
- La dirección es universal aunque la magnitud cambie: evidencia EDA de generalización
  antes de la prueba formal por título (`docs/img/eda_10_engagement_titulo.png`).

### H9 — Perfil del reseñista: biblioteca en U, idioma no causal (fig. 11)
- Biblioteca: 0 juegos (52,7% filas, dato oculto de Steam) 32,6% · 1–20 19,8% (mínimo) ·
  21–100 36,1% · 101+ 56,4%. El coleccionista prueba y abandona.
- Idioma (top-8): ruso 20,2% y chino simplificado 21,1% abajo; brasileño 56,4% y francés 54,1% arriba.
  No es causal: correlaciona con el título que juega cada comunidad.
- Longitud de reseña casi plana (Q1 32,0% → Q4 39,0%): escribir mucho no predice quedarse.

### H10 — Ventana de muestreo desigual, la limitación mayor (fig. 12)
- Ventana (max−min fecha de reseña): Dota 21,0 días · Apex 36,8 · TF2 38,3 · Warframe 54,7 · PoE 219,3 · Fall Guys 803,5.
  Mediana de antigüedad: 5,1 días (Dota) → 523,9 días (Fall Guys).
- Por eso `review_age_days` domina la importancia de churn (0,55): es **proxy de título/fase**, no causa.
  Se compensa con validación por título y reportando tasas solo como *muestra de reseñistas*.

### H11 — Voto × hábito: el hábito manda (fig. 13)
- 2×2 (mediana 88,1 h): horas bajas + no recomienda **50,6%** vs horas altas + recomienda **26,6%**.
- Con horas altas el voto es casi irrelevante (22,1% vs 26,6%); con horas bajas suma ~9 pp (50,6% vs 41,8%).
- Prioridad Live-Ops: (1) horas tempranas, (2) voto solo como desempate en la banda baja.

### H12 — Calidad de datos (fig. 14)
- Ceros: `num_games_owned` 52,7% (oculto, no cuenta vacía) · `hours_l2w` 34,5% (por construcción) · resto <8%.
- Outliers reales sin recortar (`log1p` + bosque los absorben): juegos max 32.502 · reviews max 26.464 · reseña max 8.000 caracteres.
- Casi constantes: `early_access` es 0 en el 100% y `refunded` en el 99,99% (2 casos; importancia 0, ruido documentado).
- `received_free`: n=212 (0,5%), churn 93,9% — se reporta, no se decide con n=212. Sin nulos en las 39.478 etiquetadas.
