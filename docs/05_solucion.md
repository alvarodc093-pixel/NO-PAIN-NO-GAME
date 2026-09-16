# Solución y prototipo

## 1. Técnica elegida

**Random Forest** (no deep learning) por tres razones:
1. **Interpretabilidad:** Los PMs de PlayNova necesitan entender POR QUÉ un jugador tiene alto riesgo. Un RF permite ver las top features y sus valores. El deep learning no.
2. **Datos tabulares pequeños:** 16k reseñas × 11 features no necesitan redes neuronales. Un RF con 300 árboles es más rápido, más ligero y más robusto.
3. **Anti-fuga garantizado:** horas totales, últimas 2 semanas, recencia y p75 (y el voto en conversión) se excluyen porque definen las etiquetas. Verificable en `src/train_real.py`.

## 2. Métricas del modelo

### Churn Score (estado de actividad, threshold 0,50) — `real_churn_model`
- **ROC-AUC:** 0,930 · **PR-AUC:** 0,872 (base 0,271 → ×3,2) · **Accuracy:** 0,903
- **Precision:** 0,836 · **Recall:** 0,798 · **F1:** 0,817
- **Matriz (test 3.290):** [[2258, 140], [180, 712]]
- **Top features:** antigüedad reseña 0.50, título 0.24, horas en reseña 0.08, nº reseñas autor 0.08.
- **Validez por título:** ROC 0.891–0.924 en los 6 juegos (`src/eval_per_title.py`).

### Conversion Score (high_value, threshold 0,60 sintonizado por F1) — `real_conversion_model`
- **ROC-AUC:** 0,972 · **PR-AUC:** 0,873 (base 0,199 → ×4,4) · **Accuracy:** 0,933
- **Precision:** 0,774 · **Recall:** 0,934 · **F1:** 0,847
- **Matriz (test 3.290):** [[2458, 178], [43, 611]]
- **Top features:** horas en reseña 0.75, título 0.10, antigüedad 0.07.
- **Lectura:** high_value = top-25% horas + recomienda (proxy transparente de jugador monetizable).

## 3. Anti-leakage y reproducibilidad

- Solo observables del momento de la reseña como features (nada posterior). Verificable en `src/train_real.py`.
- Train/test split estratificado 80/20, seed 42. Modelos en `models/real_*.pkl` (con encoders) y métricas en `models/real_metrics.json`.

## 4. Prototipo web: ChurnGuard Dashboard

### Página Inicio — Hero
- Parallax con orb violeta/cyan, fondo `#14112b`.
- Título "CHURNGUARD" + subtítulo "Detecta el abandono antes de que ocurra".
- Contadores: 16.447 jugadores reales · ROC-AUC churn 0,930 · F1 churn 0,817 · ROC-AUC conversión 0,972.
- CTA: "Ver Demo" → Simulador.

### Página Datos
- Tabla de benchmarks + tasas por título medidas (Dota 5% → Fall Guys 91% en muestra de reseñistas).
- Figuras del EDA real (retención por título, engagement, voto vs churn).

### Página Solución
- Dos productos: **Churn Score** (estado de actividad) + **Conversion Score** (high_value, threshold 0,60).
- Tabla de métricas comparativa (ROC-AUC, precision, recall, F1).
- Explicación de anti-leakage.

### Página Demo — Simulador
- **Simulador:** sliders (horas en reseña, juegos en cuenta, antigüedad) + selector de título y voto → gauge con **motivo + acción del playbook**. Demo ilustrativa calibrada (declarado en la web), no el `.pkl` productivo.
- **Presets:** en riesgo (pocas horas, título en declive → ~80%) · típico (perfil medio → ~50%) · sano (muchas horas, título vivo → ~7%).
- **Calculadora ROI:** CPI + budget + LTV → installs, retenidos base vs con piloto (+5 pp D7), € incremental y múltiplo sobre los 2.500 € del piloto.
- **Sección piloto:** alcance 4 semanas, A/B con métrica primaria D7, precio fijo 2.500 €, integración (`POST /score`, p95 <200 ms) y GDPR (IDs anonimizados, borrado a petición).
 - Todo en el navegador, sin backend. El modelo real está en `models/real_*.pkl`.

## 5. Playbook semanal (para PMs de PlayNova)

Cada semana, ChurnGuard entrega:
1. **Top-100 jugadores en riesgo** + motivo + acción.
2. **Acción recomendada por motivo (drivers reales):**
   - Pocas horas tempranas (Q1 ≤18 h, churn 35,7%) → onboarding + evento diario personalizado
   - Título en fase de declive (p. ej. reseña antigua) → campaña win-back + bundle retorno
   - No recomienda (churn 29,6%) → ticket de soporte proactivo + oferta de guardado
   - Cuenta nueva/estrecha (pocos juegos) → guía de progresión + recompensa 2ª sesión
3. **Ranking por título:** esfuerzo de Live-Ops donde el churn medido es mayor.
