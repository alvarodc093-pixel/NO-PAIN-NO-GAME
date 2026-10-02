# Solución y prototipo

## 1. Técnica elegida

**Random Forest** (no deep learning) por tres razones:
1. **Interpretabilidad:** Los PMs de PlayNova necesitan entender POR QUÉ un jugador tiene alto riesgo. Un RF permite ver las top features y sus valores. El deep learning no.
2. **Datos tabulares pequeños:** 40k reseñas × 11 features no necesitan redes neuronales. Un RF con 300 árboles es más rápido, más ligero y más robusto.
3. **Anti-fuga garantizado:** horas totales, últimas 2 semanas, recencia y p75 (y el voto en conversión) se excluyen porque definen las etiquetas. Verificable en `src/train_real.py`.

## 2. Métricas del modelo

### Churn Score (estado de actividad, threshold 0,50 calibrado en validación interna, test intacto) — `real_churn_model`
- **ROC-AUC:** 0,927 · **PR-AUC:** 0,892 (base 0,345 → ×2,6) · **Accuracy:** 0,881
- **Precision:** 0,839 · **Recall:** 0,811 · **F1:** 0,825
- **Matriz (test 7.896):** [[4748, 425], [515, 2208]]
- **Top features:** antigüedad reseña 0.55, título 0.23, horas en reseña 0.07, nº reseñas autor 0.06.
- **Validez por título:** ROC 0.852–0.917 en los 6 juegos (`src/eval_per_title.py`).
  Ojo honesto: con un umbral global y prevalencias del 6% al 94%, el F1 varía por título
  (Dota 2 ~0,11, Fall Guys 0.97); el ROC dice que el ranking dentro de cada juego ordena bien,
  y en el piloto se calibra el umbral por título.

### Conversion Score (high_value, threshold 0,6 calibrado en validación interna) — `real_conversion_model`
- **ROC-AUC:** 0,974 · **PR-AUC:** 0,877 (base 0,200 → ×4,4) · **Accuracy:** 0,929
- **Precision:** 0,762 · **Recall:** 0,940 · **F1:** 0,841
- **Matriz (test 7.896):** [[5858, 463], [95, 1480]]
- **Top features:** horas en reseña 0.75, título 0.11, antigüedad 0.07.
- **Lectura:** high_value = top-25% horas + recomienda (proxy transparente de jugador monetizable).

## 3. Anti-leakage y reproducibilidad

- Solo observables del momento de la reseña como features (nada posterior). Verificable en `src/train_real.py`.
- Train/test split estratificado 80/20, seed 42. El **umbral se calibra en una validación interna
  (25% del train)** maximizando F1; el test se toca una sola vez para el reporte final.
- Modelos en `models/real_*.pkl` (con encoders) y métricas en `models/real_metrics.json`.

## 4. Prototipo web: ChurnGuard (página única por secciones)

### Sección Inicio — Hero
- Parallax con orb violeta/cyan, fondo `#14112b`.
- Contadores: 39.478 jugadores reales · ROC-AUC churn 0,927 · F1 churn 0,825 · ROC-AUC conversión 0,974.
- CTAs: "Probar el simulador" → Demo; "Ver los datos reales" → Datos.

### Sección Datos
- Tabla de tasas por título medidas sobre jugadores etiquetados (Dota 6% → Fall Guys 94% en muestra de reseñistas) + p75 de horas.
- Figuras del EDA real (estado por título, engagement, voto vs churn), ampliables con lightbox.

### Sección Solución
- Dos productos: **Churn Score** (estado de actividad) + **High-Value Score** (high_value, threshold 0,6).
- Métricas comparativas (ROC-AUC, PR-AUC, precision, recall, F1) + explicación anti-fuga + FAQ (incluye por qué el F1 varía por título).

### Sección Demo — Simulador
- **Simulador:** sliders (horas en reseña, juegos en cuenta, antigüedad) + selector de título y voto → gauge con **motivo + acción del playbook**. Demo ilustrativa calibrada (declarado en la web), no el `.pkl` productivo.
- **Presets:** en riesgo (10 h, Fall Guys, sin recomendar → ~79%, rojo) · típico (35 h, PoE, señal de 120 días → ~59%, amarillo) · sano (800 h, Dota 2 → ~9%, verde).
- **Calculadora de escenario:** budget + CPI + LTV → installs, ~20,0% en grupo de alto valor y valor potencial estimado (declarado como estimación, no garantía).
- **Sección piloto:** alcance 4 semanas, A/B con métrica primaria D7, precio fijo 2.500 €, integración (`POST /score`, p95 <200 ms) y GDPR (IDs anonimizados, borrado a petición).
 - Todo en el navegador, sin backend. El modelo real está en `models/real_*.pkl`.

## 5. Playbook semanal (para PMs de PlayNova)

Cada semana, ChurnGuard entrega:
1. **Top-100 jugadores en riesgo** + motivo + acción.
2. **Acción recomendada por motivo (drivers reales):**
   - Pocas horas tempranas (Q1 ≤19 h, churn 44,1%) → onboarding + evento diario personalizado
   - Título en fase de declive (p. ej. reseña antigua) → campaña win-back + bundle retorno
   - No recomienda (churn 35,2%) → ticket de soporte proactivo + oferta de guardado
   - Cuenta nueva/estrecha (pocos juegos) → guía de progresión + recompensa 2ª sesión
3. **Ranking por título:** esfuerzo de Live-Ops donde el churn medido es mayor.
