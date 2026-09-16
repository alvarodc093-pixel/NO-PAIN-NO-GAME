# Análisis sobre datos reales

Script `notebooks/02_eda_real.py` (reproducible). Todo lo de abajo está medido en
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
