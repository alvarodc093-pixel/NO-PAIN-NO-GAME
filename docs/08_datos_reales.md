# Datos 100% reales — procedencia, mapeo y limitaciones

> Este proyecto **no usa datos sintéticos**. Todo lo afirmado en web y docs sale de
> `data/playnova_real.db`, construida con `src/build_real_dataset.py` desde
> 18.099 reseñas públicas de Steam descargadas con `src/fetch_steam_reviews.py`.
> Los scripts sintéticos antiguos (`generate_data.py`, `train.py`) están **retirados**.

## 1. Fuente

- **Steam Store `appreviews` API**: pública, sin key, 100 reseñas/petición con paginación por cursor.
  Fecha de scraping: **2026-09-14**. Filtro `recent`, idioma `all`.
- **6 títulos PC F2P en Steam** (gratuitos, con economía in-game, como los de PlayNova Games):
  Dota 2 (570), Team Fortress 2 (440), Warframe (230410), Path of Exile (238960),
  Apex Legends (1172470), Fall Guys (1097150). ~3.000 reseñas por título.
- **Descartado**: OpenDota API (evaluada como fuente de telemetría por partida;
  inalcanzable desde aquí — timeouts repetidos — y sin ventaja frente a Steam para este caso).
- Crudo reproducible: `data/real/steam_reviews.jsonl` (17 MB, ignorado en git;
  se regenera en ~5 min con el script). Versionado: `data/playnova_real.db` (2 MB) + `data/real_summary.json`.

## 2. Qué trae cada reseña (real, sin inventar nada)

Del autor: `playtime_forever`, `playtime_at_review`, `playtime_last_two_weeks`,
`last_played`, `num_games_owned`, `num_reviews`. De la reseña: `voted_up`, texto
(solo se usa su longitud), `votes_up/funny`, `comment_count`, `received_for_free`,
`steam_purchase`, `refunded`, `written_during_early_access`, `language`,
`timestamp_created/updated`. Cobertura de los campos clave: **100%** (0 nulos).

## 3. Labels (definiciones auditables en `build_real_dataset.py`)

- **churn = 1**: `playtime_forever ≥ 120 min` + `0 min` últimas 2 semanas + última partida hace **> 30 días**.
- **churn = 0**: `> 0 min` en las últimas 2 semanas.
- **Ambiguo (NULL, excluido, 1.652 casos = 9,1%)**: p. ej. < 2 h totales y 0 min recientes (turistas, no churn).
- Resultado: **16.447 filas etiquetadas, churn 27,1%**.
- **high_value = 1** (proxy de jugador monetizable — los F2P no exponen pagos):
  `playtime_forever ≥ p75 del título` **y** `voted_up = 1` → **19,9%**.

## 4. Anti-fuga

Los modelos solo ven **observables del momento de la reseña** (+ amplitud de cuenta).
Excluidos por definir las etiquetas: horas totales, últimas 2 semanas, recencia,
p75 del título y —en conversión— el voto. Verificable en `src/train_real.py`.

## 5. Tasas por título (medidas, no benchmarks)

| Título | n | churn | high_value | p75 horas | ventana reseñas |
|---|---|---|---|---|---|
| Dota 2 | 2.920 | 5,2% | 15,4% | 1.153 h | 3,4 días |
| Apex | 2.977 | 5,1% | 15,3% | 423 h | ~15 días |
| TF2 | 2.827 | 8,8% | 23,7% | 162 h | 16 días |
| Warframe | 2.699 | 8,4% | 24,0% | 693 h | 25 días |
| PoE | 2.227 | 50,7% | 21,1% | 1.257 h | 96 días |
| Fall Guys | 2.797 | 91,2% | 20,5% | 85 h | 470 días |

## 6. Sesgos conocidos (leídos antes de la defensa)

1. **Muestra de reseñistas, no de jugadores.** Quien escribe una reseña ya está
   implicado; las tasas por título **no** son tasas de retención de esos juegos.
   Lo que sí generaliza: las *relaciones* features→estado (validadas por título).
2. **Velocidad de reseñas ≠ salud idéntica.** Dota 2 genera 3.000 reseñas en
   3 días y Fall Guys en 470: por eso `review_age_days` (0.50) y `appid` (0.24)
   dominan el churn — delatan la **fase de vida del título**. Es señal real y útil
   para un publisher con portfolio, pero el piloto debe validar por título.
3. **Ventana de observación desigual.** Una reseña de hace 400 días tuvo más tiempo
   para volverse churn que una de ayer (mediana de antigüedad: 97,7 días en churned
   vs 7,1 en activos). Por eso el producto se presenta como **detección de estado
   desde señales tempranas**, no como profecía: el piloto con eventos y ventanas
   fijas hará predicción pura.
4. **high_value es proxy**, no pago observado. Su definición es transparente y su
   validación por título es excelente (ROC 0.98–1.00).

## 7. Validez por título (generaliza de verdad)

Churn ROC por título: TF2 0.891 · Dota 2 0.915 · Warframe 0.891 · PoE 0.916 ·
Fall Guys 0.918 · Apex 0.924. Conversión ROC: 0.979–0.996.
El modelo discrimina **dentro** de cada juego, no memoriza títulos.
Reproducible con `python src/eval_per_title.py`.
