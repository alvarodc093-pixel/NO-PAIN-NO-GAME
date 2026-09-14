# Día 13 — Análisis exploratorio de datos (13 sept)

Script `notebooks/01_eda.py` (pandas + matplotlib, reproducible). Lee `data/playnova_games.db`, genera las 3 figuras en `docs/img/` (copiadas a `web/assets/`) e imprime el resumen.

> Nota de honestidad: este dataset **no** contiene reportes de toxicidad, rachas de derrotas ni split por juego. Los hallazgos de abajo usan solo columnas que existen de verdad.

## Hallazgos verificados (números medidos en el dataset)

### H1 — El tutorial multiplica ×2,2 la retención
- Retención 7d con tutorial: **50,1%** vs sin tutorial: **22,3%** (churn 49,9% vs 77,7%).
- Es la palanca de onboarding más barata: cada punto de completion mueve la retención global.
- Importancia en el modelo: 0.042 (sexta feature; el top es sesiones 0.36 + monedas 0.24).

### H2 — Orgánico y referral retienen; el paid compra volumen
- Churn por canal (medido): organic 57,7% · referral 62,7% · google_uac 67,0% · unity_ads 68,6% · ironsource 68,9% · tiktok 69,1% · applovin 70,8% · meta 70,9%.
- En retención: **orgánico 42,3% > referral 37,3% > TikTok 30,9%**.
- Matiz honesto: en **conversión a pago** TikTok (7,0%) y referral (6,4%) lideran — el paid trae pagadores pero los retiene peor. La decisión es pujar por calidad (retención × conversión), no por installs.

### H3 — El círculo social retiene
- Churn con ≥1 amigo invitado: **57,7%** vs sin amigos: **75,1%**.
- Importancia en el modelo: 0.029 (churn) y 0.074 (conversión). El referral no es solo adquisición: es retención.

### H4 — El engagement temprano separa a los que se quedan
- Sesiones, monedas, ads y boosters concentran el 0.79 de importancia del modelo de churn (0.36 + 0.24 + 0.12 + 0.07).
- Los retenidos generan más monedas por sesión desde la semana 1 (ver figura de engagement). La primera compra también discrimina: solo ~14% compra, y compra quien sigue jugando.

### H5 — La ventana crítica son 4 días
- Top features de conversión: días hasta 2ª sesión (0.31) + duración sesión 1 (0.22) + tutorial (0.16).
- Regla operativa: install con tutorial + retorno en ≤4 días + (amigo o sesión 1 larga) convierte al 35%; el resto, al ~2%. De ahí el threshold 0.40 del modelo.

## Segmentación (solo splits que existen)

- **Por canal:** ver H2 (8 canales, tabla completa arriba).
- **Por OS/dispositivo:** iOS vs Android con importancias bajas (0.011 churn / 0.032 conversión) — no es palanca.
- **Por país:** importancias 0.031 / 0.103 — útil para calibrar pujas, no para producto.
- **No disponible:** por juego, por región APAC, por reportes de toxicidad — no se afirma nada sobre ellos.

## Entregable día 13 — checklist
- [x] `notebooks/01_eda.py` reproducible y sin bugs (columnas duplicadas y `legend()` corregidos)
- [x] 5 hallazgos verificados con números medidos, sin columnas inventadas
- [x] Figuras regeneradas en `docs/img/` y copiadas a `web/assets/`
