# Datos 100% reales — procedencia, mapeo y limitaciones

> Este proyecto **no usa datos sintéticos**. Todo lo afirmado en web y docs sale de
> `data/playnova_real.db`, construida con `src/build_real_dataset.py` desde
> 41.560 reseñas públicas de Steam descargadas con `src/fetch_steam_reviews.py`.

## 1. Fuente

- **Steam Store `appreviews` API**: pública, sin key, 100 reseñas/petición con paginación por cursor.
  Fecha de scraping: **2026-10-02**. Filtro `recent`, idioma `all`.
- **6 títulos PC F2P en Steam** (gratuitos, con economía in-game, como los de PlayNova Games):
  Dota 2 (570), Team Fortress 2 (440), Warframe (230410), Path of Exile (238960),
  Apex Legends (1172470), Fall Guys (1097150). ~6.800–7.400 reseñas por título.
- **Descartado**: OpenDota API (evaluada como fuente de telemetría por partida;
  inalcanzable desde aquí — timeouts repetidos — y sin ventaja frente a Steam para este caso).
- Crudo reproducible: `data/real/steam_reviews.jsonl` (39 MB, ignorado en git;
  se regenera en ~15 min con el script). Versionado: `data/playnova_real.db` (5 MB) + `data/real_summary.json`.

## 2. Qué trae cada reseña (real, sin inventar nada)

Del autor: `playtime_forever`, `playtime_at_review`, `playtime_last_two_weeks`,
`last_played`, `num_games_owned`, `num_reviews`. De la reseña: `voted_up`, texto
(solo se usa su longitud), `votes_up/funny`, `comment_count`, `received_for_free`,
`steam_purchase`, `refunded`, `written_during_early_access`, `language`,
`timestamp_created/updated`. Cobertura de los campos clave: **100%** (0 nulos).

## 3. Labels (definiciones auditables en `build_real_dataset.py`)

- **churn = 1**: `playtime_forever ≥ 120 min` + `0 min` últimas 2 semanas + última partida hace **> 30 días**.
- **churn = 0**: `> 0 min` en las últimas 2 semanas.
- **Ambiguo (NULL, excluido, 2.082 casos = 5,0%)**: p. ej. < 2 h totales y 0 min recientes (turistas, no churn).
- Resultado: **39.478 filas etiquetadas, churn 34,5%**.
- **high_value = 1** (proxy de jugador monetizable — los F2P no exponen pagos):
  `playtime_forever ≥ p75 del título` **y** `voted_up = 1` → **20,0%**.

## 4. Anti-fuga

Los modelos solo ven **observables del momento de la reseña** (+ amplitud de cuenta).
Excluidos por definir las etiquetas: horas totales, últimas 2 semanas, recencia,
p75 del título y —en conversión— el voto. Verificable en `src/train_real.py`.

## 5. Tasas por título (medidas, no benchmarks)

| Título | n | churn | high_value | p75 horas | ventana reseñas |
|---|---|---|---|---|---|
| Dota 2 | 6.646 | 6,4% | 16,0% | 1.164 h | 21,0 días |
| Apex | 7.080 | 8,4% | 15,5% | 443 h | 36,8 días |
| TF2 | 6.435 | 13,4% | 24,0% | 187 h | 38,3 días |
| Warframe | 6.497 | 17,5% | 21,7% | 743 h | 54,7 días |
| PoE | 6.247 | 71,1% | 21,3% | 1.301 h | 219,3 días |
| Fall Guys | 6.573 | 93,7% | 21,7% | 86 h | 803,5 días |

## 6. Sesgos conocidos (leídos antes de la defensa)

1. **Muestra de reseñistas, no de jugadores.** Quien escribe una reseña ya está
   implicado; las tasas por título **no** son tasas de retención de esos juegos.
   Lo que sí generaliza: las *relaciones* features→estado (validadas por título).
2. **Velocidad de reseñas ≠ salud idéntica.** Dota 2 genera 6.800 reseñas en
   21 días y Fall Guys en 804: por eso `review_age_days` (0.55) y `appid` (0.23)
   dominan el churn — delatan la **fase de vida del título**. Es señal real y útil
   para un publisher con portfolio, pero el piloto debe validar por título.
3. **Ventana de observación desigual.** Una reseña de hace 400 días tuvo más tiempo
   para volverse churn que una de ayer (mediana de antigüedad: 185,6 días en churned
   vs 19,0 en activos). Por eso el producto se presenta como **detección de estado
   desde señales tempranas**, no como profecía: el piloto con eventos y ventanas
   fijas hará predicción pura.
4. **high_value es proxy**, no pago observado. Su definición es transparente y su
   validación por título es excelente (ROC 0.971–0.993).

## 7. Validez por título (generaliza de verdad)

Churn ROC por título: TF2 0.852 · Dota 2 0.852 · Warframe 0.889 · PoE 0.883 ·
Fall Guys 0.917 · Apex 0.910. Conversión ROC: 0.971–0.993.
El modelo discrimina **dentro** de cada juego, no memoriza títulos.
Nota: el F1 por título con el umbral global (0.50) varía con la prevalencia
(Dota 2/Apex/TF2 bajos por tener ~6–13% de positivos; PoE 0.87, Fall Guys 0.97);
el ROC confirma que el ranking por juego ordena bien, y el umbral se calibraría
por título en el piloto. Reproducible con `python src/eval_per_title.py`.
