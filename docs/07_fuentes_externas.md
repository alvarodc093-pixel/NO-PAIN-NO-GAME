# Fuentes: datos reales + contexto de mercado

## 1. Fuente primaria de datos (el dataset ES real)

- **Steam Store `appreviews` API** — pública, sin key. 18.099 reseñas de 6 títulos F2P,
  scrapeadas el 2026-09-14 (`src/fetch_steam_reviews.py`, filtro `recent`).
  Totales en tienda ese día: Dota 2 (2,78M) · TF2 (1,25M) · Apex (1,07M) ·
  Warframe (677k) · Fall Guys (468k) · PoE (250k).
- Construcción auditada: `src/build_real_dataset.py` → `data/playnova_real.db` +
  `data/real_summary.json`. Definiciones de labels, anti-fuga y sesgos en `docs/08_datos_reales.md`.

## 2. Contexto de mercado (benchmarks, no datos)

1. **GameAnalytics** — "Gaming Benchmarks 2026" (referencia F2P): D1 22% / D7 4% / D30 0,7%.
   Prueba que el problema de retención existe más allá de nuestra muestra Steam.
2. **Sensor Tower** — "Gaming Market Report": conversión a pago F2P 2–5%.
   Nuestro proxy high_value (19,9%) es deliberadamente más amplio (documentado).
3. **AppsFlyer / AppMagic** — CAC de referencia $3–8 por jugador F2P (inputs de la calculadora ROI).
5. **Newzoo** — "Global Games Market Report 2026": tamaño de mercado (contexto del pitch).

## 3. Limitaciones honestas

- Muestra de reseñistas (sesgo documentado en `docs/08`): quien escribe ya está implicado.
- Ventanas de observación desiguales según antigüedad de reseña: el producto es
  detección de estado desde señales tempranas; el piloto hará predicción pura.
- Nuestros 6 títulos son directamente juegos PC F2P en Steam como los de PlayNova: misma plataforma y economía (gratis + in-game).
  El piloto con vuestros eventos afina por título.
- 16.447 filas: suficiente para RF, no para deep learning (ni falta que hace).
