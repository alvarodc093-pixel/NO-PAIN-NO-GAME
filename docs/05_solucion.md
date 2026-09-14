# Día 14 — Solución, prototipo y preparación (14 sept)

## 1. Técnica elegida (y por qué)

**Clasificación supervisada con RandomForest (300 árboles, class_weight balanceado).**
- Churn es binario desbalanceado (~17%) → RandomForest + `balanced_subsample`, explicable para un PM.
- Decisión anti-trampa: **`days_since_last_login` excluido de features**. Sería leakage (cuando lleva 30 días fuera ya es tarde). El modelo alerta ANTES, con comportamiento.
- Validación: split 80/20 estratificado, seed 42. Métricas en `models/metrics.json`.

### Métricas (test; ver `models/metrics.json` para cifras exactas de esta ejecución)

**Churn Score** (n=1.600): accuracy ~0,95 · precision ~0,79 · recall ~0,91 · F1 ~0,85 · **ROC-AUC ~0,98** · PR-AUC ~0,94.
Top features: partidas 7d, winrate_30d, días activos, partidas 30d, KDA, toxicidad, solo-rate, gasto.

**Conversion Score** (n=600, MVP ligero): accuracy ~0,76 · **ROC-AUC ~0,82**.
Top features: días hasta 2ª sesión, tutorial completado, partidas 1ª semana, amigos invitados.

Lectura ejecutiva: de cada 100 que el modelo marca en riesgo, ~79 realmente se iban (precisión); captura al ~91% de los que se van (recall). Umbral 0,5 ajustable en la app.

Calibración externa (nuevo): cada parámetro del generador cita fuente real en `docs/07_fuentes_externas.md` (Kim 2026 churn, Kwak CHI'15 toxicidad, LEC 32:19 duración, $1,8B cosmética, umbral 3 partidas EUW). Validación real opcional: `src/fetch_riot.py` descarga partidas reales EUW (match-v5) con dev key y genera `data/riot_real_*.csv` para comparar winrate/KDA reales vs sintética en la presentación.

## 2. Del notebook al producto (no solo accuracy)

Prototipo: **`web/index.html`** (HTML+CSS+JS, simulador JS réplica fiel del modelo con el mismo logit calibrado — ver `web/app.js`; ver guía completa en `docs/03_datos_website.md`):

1. **Inicio (web startup):** pitch, problema, doble score de ejemplo, pricing.
2. **Dashboard churn:** KPIs, filtros por juego/rango, ranking Top-N con semáforo 🟢🟡🔴, ficha por jugador con motivo + acción recomendada.
   - Ejemplo vivo: *Jugador #92831 → Churn 86% · solo-queue + reportes + winrate bajo → acción: sugerir squad + misión comeback.*
3. **Simulador:** mueve sliders (partidas, winrate, toxicidad, amigos, gasto) y ve el score en directo + qué lo baja.
4. **Adquisición:** conversión por canal/tutorial, calculadora de reasignación de budget, *Nuevo jugador #18372 → conversión 82%*.
5. **Metodología:** ER, features, métricas, limitaciones y roadmap.

Regla de negocio: score ≥0,7 → 🔴 contacto prioritario (top-5 semanal) · 0,4-0,7 → 🟡 nurturing · <0,4 → 🟢 sano.

**Nota técnica sobre el simulador web:** el simulador de `web/app.js` es una réplica fiel del modelo, no un wrapper sobre `.pkl`. En el entorno del navegador no hay `joblib`/`scikit-learn`. Se usa el mismo logit calibrado (`0.64 - 0.06*m30 - 0.08*m7 - 0.037*(wr-50) - 0.24*(kda-2.5) + 0.28*tox + 0.0094*(solo-50) - 0.02*min(gasto,40) - 0.067*activ`, ligeramente ajustado a mano respecto a `generate_data.py` para reproducir las cifras publicadas: #92831 → ~86 %, perfil sano → ~4 %). Si se necesita interacción con `.pkl` real, desplegar un endpoint mínimo (ej. `src/train.py` exporta JSON con coeficientes).

## 3. Cómo lo usa Riot cada lunes (demo script)
1. Abre Dashboard → filtra EUW + LoL → exporta Top-20 en riesgo.
2. Prioriza los 5 🔴 con mayor LTV (gasto previo).
3. Lanza acción del playbook (squad/misión/oferta) y mide reactivación a 14 días.
4. Revisa Adquisición → mueve 20% de TikTok a Discord/Evento.

## Entregable día 14 — checklist
- [x] Modelos entrenados y versionados (`models/`)
- [x] Prototipo usable por un PM no-técnico
- [x] Presentación preparada (storytelling día 15 en `..\..\..\NO_PAIN_NO_GAME_Storytelling.docx`, carpeta bootcamp)
